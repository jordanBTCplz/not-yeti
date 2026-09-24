# Security

These scripts are small, stdlib-only helpers for an air-gapped machine. They are not a wallet.

## Do

- Generate entropy with physical dice (1–4 only; reroll 5 and 6).
- Run only on an offline OS (Tails with persistence off, or equivalent).
- Verify `english.txt`:
  `sha256sum english.txt`
  expected `2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda`
- Run `python3 bip39_account.py --test` before any real seed.
- Confirm address 0 on a second tool (BlueWallet / Sparrow / Core) before sending.
- Keep the 24 words on paper/steel. Delete `rows.txt`. Do not photograph a real plate.
- Use `--xprv` only on the air-gap box. Never paste an xprv into a hot machine.

## Do not

- Run this in a browser or on a phone that has ever been online with the real seed.
- Trust a download of these files from anywhere but a repo whose history you checked.
- Treat a matching xpub as proof the printed address is correct. An earlier bug hashed `m/84h/0h/0h/0` instead of `/0/0`. The xpub can be right while address 0 is wrong. Always compare address 0.

## What this is not

Not multisig. Not a PSBT signer. Not a substitute for reviewing the Python yourself.
