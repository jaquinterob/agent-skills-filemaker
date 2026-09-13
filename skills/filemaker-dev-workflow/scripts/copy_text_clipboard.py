#!/usr/bin/env python3
"""Copy a text file to the macOS/Linux clipboard (fallback for HTML paste into FM).

Usage:
  python3 copy_text_clipboard.py path/to/index.html
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 copy_text_clipboard.py <file>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")

    if shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
    elif shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text.encode("utf-8"), check=True)
    elif shutil.which("xclip"):
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode("utf-8"),
            check=True,
        )
    else:
        print("No clipboard tool found (pbcopy / wl-copy / xclip).", file=sys.stderr)
        return 1

    print(f"Copied {path.name} ({len(text)} chars) to clipboard as plain text.")
    print("FileMaker: open assets layout → paste into Content → Commit → run reload script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
