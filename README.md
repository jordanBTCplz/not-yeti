# Minimalist Bitcoin Cold Storage Vault
Dice → BIP39 → xpub (stdlib only)

Small offline Python tools for:

1. Assist in converting dice rolls to initial 23 words   
2. 23 words plus 3 extra bits become word 24 (checksum)
3. 24 words → BIP84 account XPUB + core watch-only descriptor + address 0

No pip. No network. Python 3 stdlib only.

This is **not** a wallet. Signing will have to be done on Sparrow or Bitcoin Core on an air-gapped machine. The online node only ever sees an xpub.
This setup can be used to generate an XPRV as well in order to sign, but my primary goal is to create a vault.

## Files

| File | Job |
|---|---|
| `english.txt` | Official BIP-39 English list (2048 words) |
| `lookup.py` | `rows.txt` (23 × 11 bits) → word + index |
| `bip39_last_word.py` | 23 words + 3 bits → word 24 |
| `bip39_account.py` | 24 words → xpub / `wpkh` / address 0 |
| `bip39-dice-worksheet.pdf` | Printable transcription sheet |
| `instructions.md` | Tails + Core watch-only walkthrough |

## Wordlist check

```bash
sha256sum english.txt
```

Must be:

```
2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda
```

Source: [bitcoin/bips english.txt](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt)

Indexes are **0-based** (`abandon` = 0). GitHub line numbers are 1-based. Trust `lookup.py`, not line numbers.

## Dice

- Faces **1–4** only. **5 and 6 = reroll.**
- `1=00  2=01  3=10  4=11`
- Keep left-to-right order as they landed.
- 23 rows × 11 bits = 253 bits. Then **3 more bits** (a leftover unused bit on a die is normal).
- the bits you rolled go in a text editor saved as 'rows.txt'
- Those extra 3 bits do **not** go in `rows.txt`.

## Offline commands

```bash
python3 bip39_account.py --test
```

Must print `PASS`. Built-in vector is Trezor BIP-39: 23× `abandon` + `art`, passphrase `TREZOR`. Master xprv starts `xprv9s21ZrQH143K32qBag`.

```bash
python3 lookup.py
python3 bip39_last_word.py
python3 bip39_account.py
```

Default path `m/84h/0h/0h`. Add `--xprv` to the end of 'python3 bip39_account.py' only on the air-gap box if you need the account xprv.

Address 0 is `m/84h/0h/0h/0/0` (account → receive branch → index 0). Core import:

```
wpkh([xfp/84h/0h/0h]xpub.../0/*)
wpkh([xfp/84h/0h/0h]xpub.../1/*)
```

Confirm address 0 against BlueWallet / Sparrow / Core **before** sending.

## What this will not do

- Multisig descriptors (`wsh(sortedmulti(...))`) — architecture can, these scripts do not
- PSBT signing

## License

MIT. Read the scripts. Run `--test`. Compare address 0 on a second tool.
