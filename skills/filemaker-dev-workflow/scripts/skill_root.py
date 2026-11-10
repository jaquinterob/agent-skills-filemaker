#!/usr/bin/env python3
"""Print the absolute path of this skill's root (folder with SKILL.md + scripts/).

Usage:
  python3 skill_root.py
  SKILL_ROOT="$(python3 /path/to/scripts/skill_root.py)"
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    skill = root / "SKILL.md"
    scripts = root / "scripts"
    if not skill.is_file() or not scripts.is_dir():
        print(
            f"ERROR: expected SKILL.md and scripts/ under {root}",
            file=sys.stderr,
        )
        return 1
    print(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
