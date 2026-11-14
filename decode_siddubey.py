#!/usr/bin/env python3
"""
decode_siddubey.py

این صفحه کل کد واقعی‌اش رو به‌صورت فشرده (deflate-raw) و کدشده با یک
الفبای سفارشی (پایه‌ی ۴۳، و بعد از کاراکتر '~' پایه‌ی ۷۰) داخل خودِ
fragment آدرس (بعد از #) جاسازی کرده. این اسکریپت همون منطقی که در
<script> صفحه هست (location.hash -> BigInt -> bytes -> inflate) رو
برعکس اجرا می‌کنه و کد جاوااسکریپت واقعی رو بیرون می‌کشه.

استفاده:
    python3 decode_siddubey.py "<URL کامل یا فقط خودِ fragment بعد از #>"

اگر آرگومان ندید، از ورودی استاندارد (stdin) می‌خونه.
"""

import sys
import zlib
from urllib.parse import unquote, urlsplit

BASE_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ$*+-./:"   # طول 43
EXTRA_ALPHABET = "abcdefghijklmnopqrstuvwxyz_"                   # طول 27 -> مجموع 70


def extract_fragment(raw: str) -> str:
    """اگر یک URL کامل داده شده، فقط قسمت بعد از # رو برمی‌گردونه."""
    raw = raw.strip()
    if "#" in raw:
        return urlsplit(raw).fragment
    return raw


def fragment_to_bytes(frag: str) -> bytes:
    frag = unquote(frag)
    alphabet = BASE_ALPHABET
    base = 43
    n = 0
    for ch in frag:
        if ch == "~":
            base = 70
            alphabet = BASE_ALPHABET + EXTRA_ALPHABET
            continue
        idx = alphabet.index(ch)  # اگر کاراکتر ناشناخته بود، همینجا ValueError می‌ده
        n = n * base + idx

    out = bytearray()
    while n:
        out.insert(0, n & 0xFF)
        n >>= 8
    return bytes(out)


def decode(frag_or_url: str) -> str:
    frag = extract_fragment(frag_or_url)
    raw_bytes = fragment_to_bytes(frag)
    # deflate خام (بدون هدر zlib/gzip) - دقیقاً معادل DecompressionStream('deflate-raw')
    decompressed = zlib.decompress(raw_bytes, -15)
    return decompressed.decode("utf-8")


def main() -> None:
    if len(sys.argv) > 1:
        source_text = sys.argv[1]
    else:
        source_text = sys.stdin.read()

    try:
        code = decode(source_text)
    except Exception as exc:  # noqa: BLE001
        print(f"خطا در دیکود کردن: {exc}", file=sys.stderr)
        sys.exit(1)

    sys.stdout.write(code)
    if not code.endswith("\n"):
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
