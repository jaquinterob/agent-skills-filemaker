#!/usr/bin/env python3
"""Copy a text file to the system clipboard (fallback for HTML paste into FM).

Supports macOS (pbcopy), Linux (wl-copy / xclip), Windows (clip).

Usage:
  python3 copy_text_clipboard.py path/to/index.html
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def copy_text(text: str) -> str:
    """Copy text; return backend name used."""
    data = text.encode("utf-8")

    if shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input=data, check=True)
        return "pbcopy"

    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=data, check=True)
        return "wl-copy"

    if shutil.which("xclip"):
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=data,
            check=True,
        )
        return "xclip"

    if shutil.which("clip"):
        # Windows clip.exe expects UTF-16LE
        subprocess.run(
            ["clip"],
            input=text.encode("utf-16le"),
            check=True,
            shell=False,
        )
        return "clip"

    raise RuntimeError(
        "No clipboard tool found (pbcopy / wl-copy / xclip / clip)."
    )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 copy_text_clipboard.py <file>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    text = path.read_text(encoding="utf-8")

    try:
        backend = copy_text(text)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print(f"Copied {path.name} ({len(text)} chars) via {backend} as plain text.")
    print(
        "FileMaker: open assets layout → paste into Content → Commit → run reload script."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
