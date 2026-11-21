#!/usr/bin/env python3
"""Entry program for news-image-20261121.

Reads the front-page image stored beside this file (entry.png) and
writes the exact same bytes to $MAKEFUN_OUTPUT_DIR/entry.png.

The run is offline and deterministic: the output is a byte-for-byte
copy of the bundled image, so two runs always agree. Before copying,
the image is checked: PNG signature, a well-formed IHDR chunk with
width and height at most 1024, and a total size of at most 1 MiB.
"""
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("main.py: " + message, file=sys.stderr)
    return 1


def read_entry(path):
    """Return the entry bytes after the PNG gate, or None on failure."""
    try:
        with open(path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        print("main.py: cannot read %s: %s" % (path, exc), file=sys.stderr)
        return None
    if len(data) > MAX_BYTES:
        print("main.py: entry.png is %d bytes, over the 1 MiB limit"
              % len(data), file=sys.stderr)
        return None
    if not data.startswith(PNG_MAGIC):
        print("main.py: entry.png is not a PNG file", file=sys.stderr)
        return None
    if len(data) < 24 or data[12:16] != b"IHDR":
        print("main.py: entry.png has no IHDR chunk", file=sys.stderr)
        return None
    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_SIDE or height > MAX_SIDE or width < 1 or height < 1:
        print("main.py: entry.png is %dx%d, over the 1024x1024 limit"
              % (width, height), file=sys.stderr)
        return None
    if b"IEND" not in data[-12:]:
        print("main.py: entry.png has no IEND trailer", file=sys.stderr)
        return None
    return data


def write_output(data, out_dir):
    """Write data to out_dir/entry.png and report its sha256."""
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as handle:
        handle.write(data)
    digest = hashlib.sha256(data).hexdigest()
    print("main.py: wrote %s (%d bytes, sha256 %s)"
          % (target, len(data), digest))
    return 0


def run():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        return fail("MAKEFUN_OUTPUT_DIR is not set")
    data = read_entry(SOURCE)
    if data is None:
        return 1
    return write_output(data, out_dir)


if __name__ == "__main__":
    sys.exit(run())
