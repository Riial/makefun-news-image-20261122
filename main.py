#!/usr/bin/env python3
"""Entry point for news-image-20261122.

Copies the finished newspaper image (news22.png, held in this repository)
to the grader's output path as entry.png.

The program is deliberately trivial: it uses only the standard library, reads
no network, and writes the same bytes on every run, so the two grading runs
are byte-identical.
"""

import os
import shutil
from pathlib import Path

SOURCE_NAME = "news22.png"
OUTPUT_NAME = "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parent
    source = repo_root / SOURCE_NAME
    if not source.is_file():
        raise SystemExit(f"missing source image: {source}")
    with source.open("rb") as handle:
        if handle.read(len(PNG_MAGIC)) != PNG_MAGIC:
            raise SystemExit(f"source image is not a PNG: {source}")
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / OUTPUT_NAME
    shutil.copyfile(source, target)
    if target.stat().st_size != source.stat().st_size:
        raise SystemExit(f"copy incomplete: {target}")
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
