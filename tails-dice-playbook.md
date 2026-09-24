# Tails dice → xpub playbook (ASUS Vivobook)

Test run is the same as a real run. For a real plate: no photos of dice, paper, or the terminal once words are on screen.

## 0. What you should have

- This laptop (Ubuntu on the disk — ignore it this session)
- Tails USB (PNY) in a **laptop** port, not a hub
- Tools USB (`USB20FD`) with:
  - `bip39_last_word.py`
  - `bip39_account.py`
  - `lookup.py`
  - `english.txt`
- Casino dice, paper, pen
- Desktop node stays **on and online**. Never type the 24 words there.

---

## 1. Power on into Tails

1. Laptop **off**. Tails stick already plugged in.
2. Power on. At the **ASUS logo**, tap **Esc** a few times, then stop.
3. Pick the **USB / UEFI** stick (Tails). Not `ubuntu`.
4. If you land on `grub>` you were too late. Type `exit` or hold power to shut down. Try again.
5. Wait for `Booting Tails 7.x` and the logo.

**Welcome screen**

- Language: English US is fine
- **Create Persistent Storage: OFF**
- Optional: **+** → Offline mode if you see it
- **Start Tails** (not Shutdown)

Blue desktop = you made it. Do not join Wi-Fi.

---

## 2. Terminal + tools USB

1. Plug the tools stick (`USB20FD`) if it isn’t already in.
2. Apps → **Terminal** (or Super, type `terminal`).
3. Find the stick:

```bash
ls /media/amnesia
```

4. Go into it (use the name you see; often `USB20FD`):

```bash
cd /media/amnesia/USB20FD
ls
```

You want the `.py` files and `english.txt`.

5. Prove the xpub script is intact:

```bash
python3 bip39_account.py --test
```

You want `PASS`. The long `xprv9s21ZrQH…` line is the published test key, not yours.

If `cd USB20FD` fails from `~$`, you forgot the `/media/amnesia/` part. The prompt must show that folder before you run scripts.

---

## 3. Dice (entropy)

Mapping: **1=00  2=01  3=10  4=11**  
**5 and 6 = reroll.** Cocked die = reroll that die.

- Roll several at once if you want. **Keep left-to-right order as they landed.** Don’t rearrange after you see faces.
- Write bits in rows of **11** (one future word per row).
- Do this **23 times** = 253 bits.
- Then **3 more bits**. A die is 2 bits, so you will throw one leftover bit away. That is normal.
- Write those 3 bits separately (example: `000`). Do not put them in `rows.txt`.

---

## 4. Bits → 23 words

1. Apps → **Text Editor** (or `nano rows.txt`).
2. Type 23 lines, each exactly 11 characters of `0` and `1`. No spaces. No extra bits line.
3. Save as `rows.txt` **on the tools USB** (`USB20FD`).
4. Check line count:

```bash
cd /media/amnesia/USB20FD
wc -l rows.txt
```

Must say `23 rows.txt`.  
(`-l` by itself is not a command. The program is `wc`.)

5. Turn rows into words:

```bash
python3 lookup.py
```

You get `1 76 another` style lines. Check **row 1** against the notebook. Repeating a word is allowed.

If `lookup.py` is missing, create it with `nano lookup.py`:

```python
w = open("english.txt").read().split()
for i, line in enumerate(open("rows.txt"), 1):
    b = line.strip()
    n = int(b, 2)
    print(i, n, w[n])
```

`for` has **no** indent. The three lines under it do. The `for` line must stay on **one** line, ending with `1):`.

---

## 5. Word 24

```bash
python3 bip39_last_word.py
```

- Paste/type the 23 words, spaces between them.
- Extra bits: your 3 bits (`000` or `101` or `0`–`7`).
- Write **word 24** and the full 24 on paper.

`english.txt` index is **0-based** (`abandon` = 0). GitHub line numbers are 1-based. Trust `lookup.py`, not line numbers.

---

## 6. xpub + first address

```bash
python3 bip39_account.py
```

Type all **24** words. Empty passphrase (just Enter if it only asks for words).

Write down from the output:

- path (`m/84h/0h/0h`)
- master fingerprint (xfp)
- **xpub**
- the `wpkh([xfp/84h/0h/0h]xpub…/0/*)` line
- first address (`bc1q…`)

Do **not** add `--xprv` for a receive test.

These public bits can go in a text file on the USB (`test-watch.txt`). **Not** the 24 words.

---

## 7. Desktop node (online Core)

Words stay on paper / Tails. Only xpub/descriptor/address move.

1. New watch-only wallet if you can.
2. `getdescriptorinfo` on the receive `wpkh(…/0/*)` line; copy the `#checksum`.
3. Same for change `…/1/*`.
4. `importdescriptors` both (receive `internal: false`, change `internal: true`).
5. `getnewaddress` — must match script address 0. If not, stop.

Send ~$10 to that `bc1q`. Confirm it shows in Core.

---

## 8. Leave / shut down

- Stepping away **before** any real words: lock the screen; fine.
- After words have been typed: don’t leave it. Shutdown.
- Menu → **Shutdown**. Wait for the memory-wipe message. Then pull Tails if you want.
- To use Ubuntu again: power on **without** the Tails stick (or don’t pick USB in the Esc menu).

Tails does not keep `lookup.py` in RAM after shutdown. The USB does.

---

## Command cheat sheet

```bash
ls /media/amnesia
cd /media/amnesia/USB20FD
ls
python3 bip39_account.py --test
wc -l rows.txt
python3 lookup.py
python3 bip39_last_word.py
python3 bip39_account.py
```

Flags are two short dashes with no space: `--test` not `—test`.
