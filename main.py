"""The World in One Day -- Sunday 22 November 2026.

Copies the bundled newspaper image (news22.png) to the output
directory as entry.png, after validating that it is a well-formed
PNG whose bytes match the expected SHA-256 digest.

Standard library only. No network access.
"""

import binascii
import hashlib
import os
import struct
import sys

EXPECTED_SHA256 = "e3f9e6fb9d42dc59b93597f2b505e2ca05c396cfacfcbe85de1bd740bf2ccfc1"
SOURCE_NAME = "news22.png"
OUTPUT_NAME = "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1024 * 1024


def fail(message):
    print("main.py: " + message, file=sys.stderr)
    raise SystemExit(1)


def validate_png_chunks(data):
    """Walk every PNG chunk, checking its CRC32, and confirm the
    header describes a 1024x1024 8-bit RGB image ending in IEND."""
    pos = 8
    seen_ihdr = False
    seen_iend = False
    while pos + 8 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 12 + length
        if end > len(data):
            fail("news22.png has a truncated chunk")
        body = data[pos + 8:pos + 8 + length]
        stored_crc, = struct.unpack(">I", data[pos + 8 + length:end])
        actual_crc = binascii.crc32(ctype + body) & 0xFFFFFFFF
        if actual_crc != stored_crc:
            fail("news22.png chunk " + ctype.decode("ascii", "replace")
                 + " fails its CRC32 check")
        if ctype == b"IHDR":
            if seen_ihdr:
                fail("news22.png has two IHDR chunks")
            seen_ihdr = True
            width, height, depth, color = struct.unpack(">IIBB", body[:10])
            if (width, height) != (1024, 1024):
                fail("news22.png is %dx%d, not 1024x1024" % (width, height))
            if depth != 8 or color != 2:
                fail("news22.png is not 8-bit RGB")
        if ctype == b"IEND":
            seen_iend = True
            if end != len(data):
                fail("news22.png has trailing bytes after IEND")
            break
        pos = end
    if not seen_ihdr:
        fail("news22.png has no IHDR chunk")
    if not seen_iend:
        fail("news22.png has no IEND chunk")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(out_dir, OUTPUT_NAME)

    with open(source, "rb") as f:
        data = f.read()

    if len(data) < 8 or data[:8] != PNG_SIGNATURE:
        fail("news22.png is not a PNG file")

    validate_png_chunks(data)

    if len(data) > MAX_BYTES:
        fail("news22.png exceeds the 1 MiB limit")

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        fail("news22.png sha256 mismatch: got " + digest)

    os.makedirs(out_dir, exist_ok=True)
    with open(target, "wb") as f:
        f.write(data)

    print("wrote " + target + " (" + str(len(data))
          + " bytes, sha256 " + digest + ")")


if __name__ == "__main__":
    main()
