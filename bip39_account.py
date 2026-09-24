#!/usr/bin/env python3
"""
Offline: 24 BIP39 words -> account xpub, first address, optional --xprv.

Stdlib only. No pip. No network.

Put official english.txt next to this file:
  https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt
  sha256 2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda

Default path: m/84h/0h/0h  (Core descriptor: wpkh(xpub.../0/*) )

Test (do this before any real seed):
  words = 23 * 'abandon' + ' art'
  expected master xprv starts with xprv9s21ZrQH143K32qBag
  (see Trezor BIP39 vectors)
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import sys
from pathlib import Path

# secp256k1
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (Gx, Gy)

XPUB_VER = bytes.fromhex("0488B21E")
XPRV_VER = bytes.fromhex("0488ADE4")


def load_wordlist(path: Path) -> list[str]:
    words = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(words) != 2048:
        sys.exit(f"{path} must have 2048 words, found {len(words)}")
    return words


def mnemonic_to_entropy(words: list[str], wordlist: list[str]) -> bytes:
    idx = {w: i for i, w in enumerate(wordlist)}
    n = 0
    for w in words:
        if w not in idx:
            sys.exit(f"not on the wordlist: {w}")
        n = (n << 11) | idx[w]
    ms = len(words)
    if ms not in (12, 15, 18, 21, 24):
        sys.exit("need 12/15/18/21/24 words")
    ent_bits = ms * 32 // 3
    cs_bits = ent_bits // 32
    total = ent_bits + cs_bits
    packed = n.to_bytes(total // 8, "big")
    entropy, cs = packed[: ent_bits // 8], packed[ent_bits // 8 :]
    digest = hashlib.sha256(entropy).digest()
    got = digest[0] >> (8 - cs_bits)
    want = int.from_bytes(cs, "big") >> (8 * len(cs) - cs_bits) if cs else 0
    # last cs_bits of packed
    want = n & ((1 << cs_bits) - 1)
    if got != want:
        sys.exit("checksum failed — words are not a valid BIP39 mnemonic")
    return entropy


def mnemonic_to_seed(words: list[str], passphrase: str) -> bytes:
    pw = " ".join(words).encode("utf-8")
    salt = ("mnemonic" + passphrase).encode("utf-8")
    return hashlib.pbkdf2_hmac("sha512", pw, salt, 2048, dklen=64)


def _inv(a: int, m: int) -> int:
    return pow(a, m - 2, m)


def _add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        lam = (3 * x1 * x1) * _inv(2 * y1, P) % P
    else:
        lam = (y2 - y1) * _inv((x2 - x1) % P, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)


def _mul(k: int, pt=G):
    if k % N == 0 or pt is None:
        return None
    k = k % N
    out = None
    acc = pt
    while k:
        if k & 1:
            out = _add(out, acc)
        acc = _add(acc, acc)
        k >>= 1
    return out


def ser_p(pt) -> bytes:
    x, y = pt
    return bytes([2 + (y & 1)]) + x.to_bytes(32, "big")


def hash160(b: bytes) -> bytes:
    sha = hashlib.sha256(b).digest()
    try:
        r = hashlib.new("ripemd160", sha).digest()
    except ValueError:
        r = _ripemd160(sha)
    return r


def _ripemd160(data: bytes) -> bytes:
    # Minimal RIPEMD-160 so OpenSSL-3 hosts without the hash still work.
    # Spec: ISO/IEC 10118-3
    def rol(x, n):
        return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF

    kl = [
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
        7, 4, 13, 1, 10, 6, 15, 3, 12, 0, 9, 5, 2, 14, 11, 8,
        3, 10, 14, 4, 9, 15, 8, 1, 2, 7, 0, 6, 13, 11, 5, 12,
        1, 9, 11, 10, 0, 8, 12, 4, 13, 3, 7, 15, 14, 5, 6, 2,
        4, 0, 5, 9, 7, 12, 2, 10, 14, 1, 3, 8, 11, 6, 15, 13,
    ]
    kr = [
        5, 14, 7, 0, 9, 2, 11, 4, 13, 6, 15, 8, 1, 10, 3, 12,
        6, 11, 3, 7, 0, 13, 5, 10, 14, 15, 8, 12, 4, 9, 1, 2,
        15, 5, 1, 3, 7, 14, 6, 9, 11, 8, 12, 2, 10, 0, 4, 13,
        8, 6, 4, 1, 3, 11, 15, 0, 5, 12, 2, 13, 9, 7, 10, 14,
        12, 15, 10, 4, 1, 5, 8, 7, 6, 2, 13, 14, 0, 3, 9, 11,
    ]
    sl = [
        11, 14, 15, 12, 5, 8, 7, 9, 11, 13, 14, 15, 6, 7, 9, 8,
        7, 6, 8, 13, 11, 9, 7, 15, 7, 12, 15, 9, 11, 7, 13, 12,
        11, 13, 6, 7, 14, 9, 13, 15, 14, 8, 13, 6, 5, 12, 7, 5,
        11, 12, 14, 15, 14, 15, 9, 8, 9, 14, 5, 6, 8, 6, 5, 12,
        9, 15, 5, 11, 6, 8, 13, 12, 5, 12, 13, 14, 11, 8, 5, 6,
    ]
    sr = [
        8, 9, 9, 11, 13, 15, 15, 5, 7, 7, 8, 11, 14, 14, 12, 6,
        9, 13, 15, 7, 12, 8, 9, 11, 7, 7, 12, 7, 6, 15, 13, 11,
        9, 7, 15, 11, 8, 6, 6, 14, 12, 13, 5, 14, 13, 13, 7, 5,
        15, 5, 8, 11, 14, 14, 6, 14, 6, 9, 12, 9, 12, 5, 15, 8,
        8, 5, 12, 9, 12, 5, 14, 6, 8, 13, 6, 5, 15, 13, 11, 11,
    ]
    fl = [
        lambda x, y, z: x ^ y ^ z,
        lambda x, y, z: (x & y) | (~x & z),
        lambda x, y, z: (x | ~y) ^ z,
        lambda x, y, z: (x & z) | (y & ~z),
        lambda x, y, z: x ^ (y | ~z),
    ]
    ml = [0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xA953FD4E]
    mr = [0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x7A6D76E9, 0x00000000]
    ml_data = data + b"\x80" + b"\x00" * ((55 - len(data)) % 64) + (len(data) * 8).to_bytes(8, "little")
    h0, h1, h2, h3, h4 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0
    for i in range(0, len(ml_data), 64):
        x = [int.from_bytes(ml_data[i + 4 * j : i + 4 * j + 4], "little") for j in range(16)]
        al = ar = h0
        bl = br = h1
        cl = cr = h2
        dl = dr = h3
        el = er = h4
        for j in range(80):
            t = (rol((al + fl[j // 16](bl, cl, dl) + x[kl[j]] + ml[j // 16]) & 0xFFFFFFFF, sl[j]) + el) & 0xFFFFFFFF
            al, el, dl, cl, bl = el, dl, rol(cl, 10), bl, t
            t = (rol((ar + fl[4 - j // 16](br, cr, dr) + x[kr[j]] + mr[j // 16]) & 0xFFFFFFFF, sr[j]) + er) & 0xFFFFFFFF
            ar, er, dr, cr, br = er, dr, rol(cr, 10), br, t
        t = (h1 + cl + dr) & 0xFFFFFFFF
        h1 = (h2 + dl + er) & 0xFFFFFFFF
        h2 = (h3 + el + ar) & 0xFFFFFFFF
        h3 = (h4 + al + br) & 0xFFFFFFFF
        h4 = (h0 + bl + cr) & 0xFFFFFFFF
        h0 = t
    return b"".join(int(v).to_bytes(4, "little") for v in (h0, h1, h2, h3, h4))


B58 = b"123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58check(payload: bytes) -> str:
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    raw = payload + chk
    n = int.from_bytes(raw, "big")
    out = b""
    while n:
        n, r = divmod(n, 58)
        out = bytes([B58[r]]) + out
    pad = 0
    for b in raw:
        if b == 0:
            pad += 1
        else:
            break
    return (B58[0:1] * pad + out).decode()


def bech32_encode(hrp: str, witver: int, witprog: bytes) -> str:
    charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"

    def convertbits(data, frombits, tobits, pad=True):
        acc = 0
        bits = 0
        ret = []
        maxv = (1 << tobits) - 1
        for v in data:
            acc = (acc << frombits) | v
            bits += frombits
            while bits >= tobits:
                bits -= tobits
                ret.append((acc >> bits) & maxv)
        if pad and bits:
            ret.append((acc << (tobits - bits)) & maxv)
        return ret

    def polymod(values):
        gen = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
        chk = 1
        for v in values:
            b = chk >> 25
            chk = ((chk & 0x1FFFFFF) << 5) ^ v
            for i in range(5):
                if (b >> i) & 1:
                    chk ^= gen[i]
        return chk

    def hrp_expand(h):
        return [ord(x) >> 5 for x in h] + [0] + [ord(x) & 31 for x in h]

    data = [witver] + convertbits(list(witprog), 8, 5)
    values = hrp_expand(hrp) + data
    p = polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    combined = data + [(p >> 5 * (5 - i)) & 31 for i in range(6)]
    return hrp + "1" + "".join(charset[d] for d in combined)


def master_from_seed(seed: bytes):
    I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
    return int.from_bytes(I[:32], "big"), I[32:]


def ckd_priv(k: int, chain: bytes, index: int):
    if index >= 0x80000000:
        data = b"\x00" + k.to_bytes(32, "big") + index.to_bytes(4, "big")
    else:
        data = ser_p(_mul(k)) + index.to_bytes(4, "big")
    I = hmac.new(chain, data, hashlib.sha512).digest()
    ki = (int.from_bytes(I[:32], "big") + k) % N
    return ki, I[32:]


def encode_ext(ver: bytes, depth: int, fpr: bytes, child: int, chain: bytes, key: bytes) -> str:
    payload = ver + bytes([depth]) + fpr + child.to_bytes(4, "big") + chain + key
    return b58check(payload)


def fingerprint(k: int) -> bytes:
    return hash160(ser_p(_mul(k)))[:4]


def parse_path(s: str) -> list[int]:
    s = s.strip().replace("m/", "").replace("M/", "")
    if not s:
        return []
    out = []
    for p in s.split("/"):
        hardened = p.endswith("h") or p.endswith("'") or p.endswith("H")
        n = int(p[:-1] if hardened else p)
        if hardened:
            n += 0x80000000
        out.append(n)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wordlist", default="english.txt")
    ap.add_argument("--words")
    ap.add_argument("--passphrase", default="")
    ap.add_argument("--path", default="m/84h/0h/0h", help="account path")
    ap.add_argument("--test", action="store_true", help="run built-in vector and exit")
    ap.add_argument(
        "--xprv",
        action="store_true",
        help="also print account xprv + Core signing descriptors (offline only)",
    )
    args = ap.parse_args()

    if args.test:
        # Trezor vectors use passphrase "TREZOR"
        words = ["abandon"] * 23 + ["art"]
        seed = mnemonic_to_seed(words, "TREZOR")
        expect = bytes.fromhex(
            "bda85446c68413707090a52022edd26a1c9462295029f2e60cd7c4f2bbd30971"
            "70af7a4d73245cafa9c3cca8d561a7c3de6f5d4a10be8ed2a5e608d68f92fcc8"
        )
        if seed != expect:
            sys.exit("FAIL seed vector")
        k, c = master_from_seed(seed)
        xprv = encode_ext(XPRV_VER, 0, b"\x00" * 4, 0, c, b"\x00" + k.to_bytes(32, "big"))
        if not xprv.startswith("xprv9s21ZrQH143K32qBag"):
            sys.exit("FAIL master xprv prefix: " + xprv)
        print("PASS built-in vector (TREZOR passphrase seed + master xprv prefix)")
        print(xprv)
        return

    wordlist = load_wordlist(Path(args.wordlist))
    raw = args.words or input("24 words: ")
    words = raw.strip().lower().split()
    mnemonic_to_entropy(words, wordlist)
    seed = mnemonic_to_seed(words, args.passphrase)
    k, c = master_from_seed(seed)
    fpr_master = fingerprint(k)
    depth = 0
    child = 0
    parent_fpr = b"\x00" * 4
    for i, idx in enumerate(parse_path(args.path)):
        parent_fpr = fingerprint(k)
        k, c = ckd_priv(k, c, idx)
        depth = i + 1
        child = idx
    path_body = args.path[2:] if args.path.startswith("m/") else args.path
    xpub = encode_ext(XPUB_VER, depth, parent_fpr, child, c, ser_p(_mul(k)))
    acct_xprv = encode_ext(XPRV_VER, depth, parent_fpr, child, c, b"\x00" + k.to_bytes(32, "big"))
    # Account key is m/84h/0h/0h. BIP84 address 0 is m/84h/0h/0h/0/0
    # (change=0, then index=0). The descriptor wpkh(xpub/0/*) does that too.
    k_recv, c_recv = ckd_priv(k, c, 0)
    k0, _c0 = ckd_priv(k_recv, c_recv, 0)
    addr_pub = ser_p(_mul(k0))
    addr = bech32_encode("bc", 0, hash160(addr_pub))
    print("path:", args.path)
    print("master fingerprint (xfp):", fpr_master.hex())
    print("xpub:")
    print(xpub)
    print()
    print("Core watch-only (receive):")
    print(f"wpkh([{fpr_master.hex()}/{path_body}]{xpub}/0/*)")
    print()
    print("first receive address (index 0):")
    print(addr)
    if args.xprv:
        print()
        print("ACCOUNT xprv (this spends the coins — offline only):")
        print(acct_xprv)
        print()
        print("Core signing descriptors (add checksum via getdescriptorinfo):")
        print(f"wpkh([{fpr_master.hex()}/{path_body}]{acct_xprv}/0/*)")
        print(f"wpkh([{fpr_master.hex()}/{path_body}]{acct_xprv}/1/*)")
        print()
        print("Delete this wallet after signing. Do not save this output.")
    else:
        print()
        print("xprv not printed. Pass --xprv on an air-gap box if you need Core signing descriptors.")


if __name__ == "__main__":
    main()
