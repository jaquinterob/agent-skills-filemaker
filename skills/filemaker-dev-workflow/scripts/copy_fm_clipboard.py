#!/usr/bin/env python3
"""Copy FileMaker fmxmlsnippet XML onto the clipboard as script steps (XMSS).

macOS only (PyObjC). On Linux/Windows, exit with a clear fallback message.

Usage:
  python3 copy_fm_clipboard.py path/to/Script_steps.xml

Then in FileMaker Script Workspace: open script → select all → Delete → Paste.
"""

from __future__ import annotations

import platform
import sys
from pathlib import Path

# macOS dynamic UTI for FileMaker script steps (XMSS)
FM_XMSS = "dyn.ah62d4rv4gk8zuxnxnq"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 copy_fm_clipboard.py <file.xml>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 1

    xml = path.read_text(encoding="utf-8")
    if "fmxmlsnippet" not in xml:
        print(
            "File does not look like an fmxmlsnippet. "
            "Convert text→XML with the product tool first, or export steps from FM.",
            file=sys.stderr,
        )
        return 1

    system = platform.system()
    if system != "Darwin":
        print(
            f"XMSS clipboard is not supported on {system}.\n"
            "Options:\n"
            "  1) Run this script on macOS (PyObjC)\n"
            "  2) Codence FM Clipboard Tool / MBS Plugin\n"
            f"  3) Recreate steps manually from: {path}\n"
            "Do NOT pbcopy/xclip raw XML — Script Workspace will not paste steps.",
            file=sys.stderr,
        )
        return 1

    try:
        from AppKit import NSPasteboard, NSPasteboardTypeString
        from Foundation import NSData
    except ImportError:
        print(
            "PyObjC not installed. Run: pip3 install pyobjc-framework-Cocoa\n"
            "Or use Codence FM Clipboard Tool / MBS Plugin.",
            file=sys.stderr,
        )
        return 1

    raw = xml.encode("utf-8")
    data = NSData.dataWithBytes_length_(raw, len(raw))
    pb = NSPasteboard.generalPasteboard()
    pb.clearContents()
    pb.declareTypes_owner_([FM_XMSS, NSPasteboardTypeString], None)
    ok = pb.setData_forType_(data, FM_XMSS)
    pb.setString_forType_(xml, NSPasteboardTypeString)

    print(f"Copied {path.name} to clipboard as XMSS ({'OK' if ok else 'FAILED'}).")
    print(
        "FileMaker: open target script → select all steps → Delete → Paste (Cmd+V)."
    )
    if not ok:
        print("XMSS write failed — try Codence FM Clipboard Tool.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
