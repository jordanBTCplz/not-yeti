# Instructions: BIP39 words → Core watch-only

Same steps for a $10 test and for a real plate. For a real plate: no photos
of slips, paper, or the terminal once words are on screen.

There are three roles, not just one computer:

1. **Meatspace** — bag of word slips (default) or casino dice
2. **Offline signer** — a laptop that boots **Tails** (or equivalent) and
   never joins a network this session
3. **Online node** — Bitcoin Core. It only ever sees an xpub / descriptor.
   Never the 24 words.

## 0. What you should have

- Any PC that can boot from USB
- A Tails USB verified against https://tails.net
- A **second** USB ("tools") with:
  - `bip39_last_word.py`
  - `bip39_account.py`
  - `english.txt`
  - `lookup.py` and `bip39-dice-worksheet.pdf` **only if you use dice**
  - these instructions (optional)
- A **third** USB if you want the xpub on a separate data stick
- Printer, scissors, container for slips (default path)
- Casino dice + pen **only for the dice path**
- A Bitcoin Core node on its own machine

Do not put the 24 words on any USB. The xpub rides the data stick, not the
tools stick, if you have both.

`english.txt` check (once on a hot machine, then copy the file):

    sha256sum english.txt

Must be `2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda`.

---

## 1. Boot the offline laptop into Tails

1. Laptop **off**. Tails stick in a port on the laptop itself (hubs are flaky for boot).
2. Power on and open the firmware boot menu (Esc, F12, F10, F9, F2, or Del).
   If you land on `grub>` you were late — type `exit` or hold power and try again.
3. Pick the **USB / UEFI** entry for Tails.
4. Welcome screen: Persistent Storage **OFF**. Do **not** join Wi-Fi.

Blue desktop = offline enough. After boot, Tails runs from RAM; you can unplug the Tails stick if you need the port.

---

## 2. Terminal + tools USB

1. Plug the tools stick.
2. Open Terminal.
3. Mount point:

    ls /media/amnesia
    cd /media/amnesia/LABEL
    ls

`LABEL` is the stick's name. If `cd` fails, you typed only the name. Use the full path `/media/amnesia/LABEL`.

Some live USBs use `/run/media/USERNAME/LABEL` instead.

4. Prove the account script:

    python3 bip39_account.py --test

You want `PASS`. The `xprv9s21ZrQH…` line is Trezor's test key, not yours.

---

## 3. Entropy (default: bag)

1. Print the hashed `english.txt`. Cut each word onto its own slip.
2. Mix. Draw one, write it, **put it back**, mix. Do that **23 times**.
3. Repeats are allowed.
4. Get **3 extra bits** on paper (`000` … `111`) with coins or a 1-4 die
   (`1=00 2=01 3=10 4=11`). This is **not** a 24th drawn word.

Skip section 4. Go to section 5. You do not need `rows.txt` or `lookup.py`.

---

## 4. Dice path (optional)

Mapping: **1=00  2=01  3=10  4=11**. **5 and 6 = reroll.** Cocked die = reroll.

- Keep left-to-right order as they landed.
- 23 rows of 11 bits, then 3 more bits written separately.
- Those 3 bits do **not** go in `rows.txt`.
- Sheet: `bip39-dice-worksheet.pdf`.

1. `nano rows.txt` — 23 lines, exactly 11 characters of `0` and `1`. No leftover-bits line.
2. `wc -l rows.txt` must say `23`.
3. `python3 lookup.py`
4. Spot-check first, middle, and last row against paper. Same word twice is allowed.

Then section 5.

---

## 5. Word 24

    python3 bip39_last_word.py

- 23 words, spaces between them
- Extra bits: the three `0`/`1`s from paper (example `000` or `101`)
- Write **word 24** and the full 24-word seed on paper

---

## 6. xpub + first address

    python3 bip39_account.py

Type all **24** words. Script default is no passphrase.

There is a `--passphrase` option. Do not use it unless that extra secret is written down with the plate. When you check in Sparrow or BlueWallet, leave the passphrase blank so it matches.

Copy onto paper or a **public-only** text file on the data USB (not the words):

- path (`m/84h/0h/0h`)
- master fingerprint (xfp)
- **xpub**
- `wpkh([xfp/84h/0h/0h]xpub…/0/*)`
- first receive address (`bc1q…`)

Do **not** pass `--xprv` unless this box is air-gapped and you need a signing descriptor. Address 0 is `m/84h/0h/0h/0/0`. Confirm it on a second tool (Sparrow / BlueWallet / Core) before sending.

If you used the dice path:

    rm rows.txt

---

## 7. Online node (Bitcoin Core)

Words stay on paper. Only the descriptor moves.

1. Create a **watch-only** wallet (disable private keys).
2. `getdescriptorinfo` on the receive `wpkh(…/0/*)` line; use the string that includes `#checksum`.
3. Same for change: same xpub with `/1/*`.
4. `importdescriptors` both (receive `internal: false`, change `internal: true`). Use `"timestamp": "now"` if coins have not been sent yet. A pruned node may refuse `timestamp: 0`.
5. Receive / `getnewaddress` must match script address 0. If not, stop.

Send a small test amount to that `bc1q`. Confirm it in Core before any serious balance.

---

## 8. Shut down

- Before real words: locking the screen is fine.
- After words: **Shutdown**. Tails menu → Shutdown. Wait for the memory-wipe line.

Tails does not keep scripts in RAM after shutdown. The tools USB does.

---

## Spend later (outline)

The node builds a PSBT. The Tails box (Sparrow or Core binaries, network off) loads the 24 words for that session only, signs, writes the signed PSBT back to a USB. The node broadcasts. These scripts do not sign PSBTs.

---

## Command cheat sheet

    ls /media/amnesia
    cd /media/amnesia/LABEL
    ls
    python3 bip39_account.py --test
    python3 bip39_last_word.py
    python3 bip39_account.py

Dice path only:

    wc -l rows.txt
    python3 lookup.py
    rm rows.txt

Flags are two short ASCII dashes: `--test` not a word-processor dash.
