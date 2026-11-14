# siddubey-decoder

A small, dependency-free command-line tool that reverse-engineers and
decodes the URL-fragment encoding scheme used by pages such as
`https://www.siddubey.com/q#...`.

[فارسی (Persian README)](README.fa.md)

## How the encoding works

The target page ships almost no visible HTML. Its only inline
`<script>` does roughly this, on every page load:

1. Reads everything after `#` in the page's own URL (`location.hash`).
2. Walks that string character by character, treating the whole thing
   as one big integer written in a custom numeral system:
   - Base 43, alphabet: `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:`
   - If the character `~` shows up, the alphabet is extended with
     `abcdefghijklmnopqrstuvwxyz_` (27 more symbols, 70 total) and the
     base switches to 70 for every character that follows.
3. Splits that big integer into big-endian bytes.
4. Treats those bytes as **raw DEFLATE** data (no zlib/gzip header) and
   decompresses them — in the browser this is
   `DecompressionStream('deflate-raw')`.
5. `eval()`s the resulting text, which is the page's *real* JavaScript
   source — the entire page/program is stored inline in the URL
   instead of on a server.

`decode_siddubey.py` reproduces steps 2–4 in plain Python (standard
library only: `zlib`, `urllib.parse`), so you can get the decompressed
source text without a browser at all.

## Usage

```bash
python3 decode_siddubey.py "FULL_URL_OR_JUST_THE_FRAGMENT" > out.js
```

You can pass either the full URL or just the part after `#`. With no
argument, it reads from standard input instead.

### Quoting — this trips people up

The fragment contains characters like `$ * + - . / :`, which several
shells treat specially.

| Shell                      | Correct quoting         |
|-----------------------------|--------------------------|
| bash / zsh (Linux, macOS)   | single quotes `'...'`   |
| Windows **PowerShell**      | single quotes `'...'`   |
| Windows **Command Prompt** (`cmd.exe`) | double quotes `"..."` — `cmd.exe` does **not** treat `'` as a quote character; it would be passed through literally and break the decode |

If you'd rather not touch a terminal at all, open the script in an
editor (e.g. IDLE on Windows), hardcode your fragment as a string at
the top, and run it with `F5` / "Run Module" — no command line needed.

## What this repo intentionally does *not* include

This repo contains only the decoder tool — code I wrote myself to
reproduce a publicly documented client-side encoding/compression
scheme. It does **not** bundle any already-decoded output from any
specific page. Whatever a given fragment decodes to is that page
author's own content and copyright; run the script yourself against
whatever link you're curious about, for your own use.

## License

MIT — see [LICENSE](LICENSE). This license covers the decoder script
in this repository only; it says nothing about the copyright of
whatever content you choose to decode with it.
