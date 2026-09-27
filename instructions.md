# Instructions: dice → BIP39 → Core watch-only

Same steps for a $10 test and for a real plate. For a real plate: no photos of dice, paper, or the terminal once words are on screen.

There are three roles, not just one computer:

1. **Meatspace** — casino dice + paper (Or however you want to generate entropy)
2. **Offline signer** — a laptop that boots **Tails** (or equivalent amnesic OS) and never joins a network this session
3. **Online node** — Bitcoin Core. It only ever sees an xpub / descriptor. Never the 24 words.

## 0\. What you should have

* Any PC that can boot from USB (the brand does not matter)
* A Tails USB you verified against [tails.net](https://tails.net)
* A **second** USB (“tools”) with only:

  * `bip39_last_word.py`
  * `bip39_account.py`
  * `lookup.py`
  * `english.txt`
  * these instructions / the worksheet PDF (optional)
* A **third** USB if you want to segregate data transfer from the "tools" stick
* Casino-grade dice, paper, pen
* You could also use something like Entropia Seed Pills to minimize this step. lookup.py is only a tool for converting the raw bits to bip39 words without looking over the wordlist 23 times. Using a different scheme eliminates the need for lookup.py.
* A Bitcoin Core node that stays on its own machine

Do not put the 24 words on any USB sticks. XPUB rides the data transfer stick, not the tools stick, if you have both.

`english.txt` check (can be done once on a hot machine, then copy the file):

```bash
sha256sum english.txt
```

Must be `2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda`.

\---

## 1\. Boot the offline laptop into Tails

1. Laptop **off**. Tails stick in a port on the laptop itself (hubs are flaky for boot).
2. Power on and open the firmware boot menu. Common keys:

   * Esc, F12, F10, F9, F2, or Del
   * Hold the key at the vendor logo. If you land on `grub>` you were late — type `exit` or hold power and try again.
3. Pick the **USB / UEFI** entry for Tails. Not the copy of Windows or Ubuntu on the internal disk.
4. Wait for the Tails boot screen.

**Welcome screen**

* Language: whatever you read
* **Persistent Storage: OFF** (real seed sessions especially)
* Start Tails. Do **not** join Wi-Fi.

Blue desktop = you are offline enough for this procedure. Leave the Tails stick in; after boot Tails runs from RAM and you can unplug it if you need the port.

\---

## 2\. Terminal + tools USB

1. Plug the tools stick.
2. Open **Terminal** (Applications, or the Super/Windows key then type `terminal`).
3. Find the mount point:

```bash
ls /media/amnesia
```

Tails mounts removable disks under `/media/amnesia/LABEL`. `LABEL` is whatever the stick is named (`USB20FD`, `TOOLS`, `UNTITLED`, …).

```bash
cd /media/amnesia/LABEL
ls
```

You want the `.py` files and `english.txt`. If `cd` fails, you may have typed only the stick's name. Use the full path: /media/amnesia/LABEL.

4. Prove the account script matches the published test vector:

```bash
python3 bip39_account.py --test
```

You want `PASS`. The `xprv9s21ZrQH…` line is Trezor’s published test key, not yours.

On some live USBs the mount is `/run/media/USERNAME/LABEL` instead. `ls /media` and `ls /run/media` will show you which world you are in. Same idea: `cd` into the folder that actually lists the scripts.

\---

## 3\. Dice (entropy)

Mapping: **1=00  2=01  3=10  4=11**  
**5 and 6 = reroll.** Cocked die = reroll that die.

* Roll several at once if you want. **Keep left-to-right order as they landed.** Do not sort them after you see faces.
* Write bits in rows of **11** (one future word per row).
* Do this **23 times** = 253 bits.
* Then **3 more bits**. A die is 2 bits, so one leftover unused bit is normal.
* Write those 3 bits separately (example: `000`). They do **not** go in `rows.txt`.

Printable sheet: `bip39-dice-worksheet.pdf` in this repo.

\---

## 4\. Bits → 23 words

1. Open a text editor on Tails, or `nano rows.txt` in the tools folder.
2. Type 23 lines, each exactly 11 characters of `0` and `1`. No spaces. No extra-bits line.

3. Example of the *shape* (fake bits — do not use):

```
01001110101
11010001100
00101101011
```

23 lines like that. No spaces. Do Not put the extra 3 bits in this file.
Those 3 extra bits stay on paper until step 5.

4. Save as `rows.txt` **on the tools USB**.
5. Check line count (from the tools folder):

```bash
wc -l rows.txt
```

Must say `23 rows.txt`.  

6. Turn rows into words:

```bash
python3 lookup.py
```

Each line is: your row number, word list index number, word. Check rows against paper. The same word twice is allowed.

`english.txt` indexes are **0-based** (`abandon` = 0). GitHub line numbers are 1-based. Trust `lookup.py`.

\---

## 5\. Word 24

```bash
python3 bip39_last_word.py
```

* 23 words, spaces between them
* Extra bits: Example: `000` / `101` / whatever your extra bits are
* Write **word 24** and the full 24 word seed on paper

\---

## 6\. xpub + first address

```bash
python3 bip39_account.py
```

Type all **24** words. Script default is no passphrase.
There is a '--passphrase' option you can add to the script. Do not use this unless you intend to back this up as well.
Remember whether you used a passphrase when you cross check this tool against a wallet software. 

Copy onto paper or a **public-only** text file on the USB (not the words):

* path (`m/84h/0h/0h`)
* master fingerprint (xfp)
* **xpub**
* `wpkh([xfp/84h/0h/0h]xpub…/0/*)`
* first receive address (`bc1q…`)

Do **not** pass `--xprv` unless this box is air-gapped and you need a signing descriptor. Address 0 is `m/84h/0h/0h/0/0`. Confirm it on a second tool (Sparrow / BlueWallet / Core) before sending.

Delete `rows.txt` off the tools stick or separate data transfer stick when you are done:

```bash
rm rows.txt
```

\---

## 7\. Online node (Bitcoin Core)

Words stay on paper/ metal plate / the Tails session. Only the descriptor moves.

1. Create a **watch-only** wallet (`disable private keys`, blank if offered).
2. `getdescriptorinfo` on the receive `wpkh(…/0/*)` line; use the string that includes `#checksum`.
3. Same for change: same xpub with `/1/*`.
4. `importdescriptors` both (receive `internal: false`, change `internal: true`). Use `"timestamp": "now"` if the coins have not been sent yet. A **pruned** node may refuse a full rescan (`timestamp: 0`).
5. `getnewaddress` (or Receive in the GUI) must match script address 0. If not, stop.

Send a small test amount to that `bc1q`. Confirm it in Core before any serious balance.

GUI is enough after the descriptors are imported. The JSON is only because Core’s “paste xpub” path is still awkward.

\---

## 8\. Shut down

* Before any real words have been typed: locking the screen is fine.
* After words have been typed: don’t walk away. **Shutdown**.
* Tails menu → Shutdown. Wait for the memory-wipe line. Then pull sticks if you want.
* Next power-on without the Tails stick returns whatever OS is on the internal disk.

Tails does not keep scripts in RAM after shutdown. The tools USB does.

\---

## Spend later (outline)

The node builds a PSBT. The Tails box (Sparrow or Bitcoin Core binaries, network off) loads the 24 words for that session only, signs, writes the signed PSBT back to a USB. The node broadcasts. Do not leave the seed on the laptop disk.

These scripts do not sign PSBTs.

\---

## Command cheat sheet

```bash
ls /media/amnesia
cd /media/amnesia/LABEL
ls
python3 bip39_account.py --test
wc -l rows.txt
python3 lookup.py
python3 bip39_last_word.py
python3 bip39_account.py
rm rows.txt
```

Flags are two short ASCII dashes: `--test` not a word-processor `—test`.

