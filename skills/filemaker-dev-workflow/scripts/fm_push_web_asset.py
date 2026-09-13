#!/usr/bin/env python3
"""Push an HTML (or text) asset into a FileMaker table via Data API.

Generic: works with any FMS host / database / layout / file name.

Requires .env (or --env) with:
  FM_DATA_API_BASE_URL   https://host/fmi/data/vLatest
  FM_DATA_API_DATABASE   Exact .fmp12 name on Server
  FM_DATA_API_ACCOUNT    Technical account with fmrest
  FM_DATA_API_PASSWORD   Password

Usage:
  python3 fm_push_web_asset.py --html path/to/index.html
  python3 fm_push_web_asset.py --html web/index.html --dry-run
  python3 fm_push_web_asset.py --html web/app.html \\
      --layout "Data WEB_ASSETS" --filename app.html \\
      --find-layout "App Web"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote


def load_env(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    for k in (
        "FM_DATA_API_BASE_URL",
        "FM_DATA_API_DATABASE",
        "FM_DATA_API_ACCOUNT",
        "FM_DATA_API_PASSWORD",
    ):
        if not out.get(k):
            raise SystemExit(f"Missing {k} in {path}")
    return out


def curl_json(
    method: str,
    url: str,
    *,
    token: str | None = None,
    userpass: str | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    cmd = ["curl", "-sS", "-k", "--http1.1", "-X", method, url, "--max-time", "180"]
    if userpass:
        cmd.extend(["-u", userpass])
    if token:
        cmd.extend(["-H", f"Authorization: Bearer {token}"])
    if body is not None:
        payload = json.dumps(body, ensure_ascii=False)
        cmd.extend(["-H", "Content-Type: application/json", "--data-binary", payload])
    elif method in {"POST", "PATCH"}:
        cmd.extend(["-H", "Content-Type: application/json", "--data", "{}"])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"curl {proc.returncode}")
    text = proc.stdout.strip()
    return json.loads(text) if text else {}


def api_code(data: dict[str, Any]) -> str:
    return str((data.get("messages") or [{}])[0].get("code") or "")


def login(env: dict[str, str]) -> str:
    url = f"{env['FM_DATA_API_BASE_URL'].rstrip('/')}/databases/{env['FM_DATA_API_DATABASE']}/sessions"
    data = curl_json(
        "POST",
        url,
        userpass=f"{env['FM_DATA_API_ACCOUNT']}:{env['FM_DATA_API_PASSWORD']}",
        body={},
    )
    token = (data.get("response") or {}).get("token")
    if api_code(data) != "0" or not token:
        raise RuntimeError(f"Login failed: {data}")
    return str(token)


def logout(env: dict[str, str], token: str) -> None:
    url = (
        f"{env['FM_DATA_API_BASE_URL'].rstrip('/')}/databases/"
        f"{env['FM_DATA_API_DATABASE']}/sessions/{token}"
    )
    try:
        curl_json("DELETE", url, token=token)
    except Exception:
        pass


def find_record_id(
    env: dict[str, str],
    token: str,
    *,
    layout: str,
    filename: str,
    filename_field: str,
    find_layout: str | None,
) -> str | None:
    """Find recordId. Optional find_layout avoids downloading huge Content fields."""
    base = env["FM_DATA_API_BASE_URL"].rstrip("/")
    db = env["FM_DATA_API_DATABASE"]
    layout_q = quote(layout, safe="")
    find_url = f"{base}/databases/{db}/layouts/{layout_q}/_find"
    body: dict[str, Any] = {
        "query": [{filename_field: filename}],
        "limit": 1,
    }
    if find_layout:
        find_url += f"?layout.response={quote(find_layout)}"
        body["layout.response"] = find_layout

    data = curl_json("POST", find_url, token=token, body=body)
    code = api_code(data)
    if code == "105":
        raise SystemExit(
            f"Layout «{layout}» not found via Data API. "
            "Pass --layout with the exact layout name."
        )
    if code not in {"0", "401"}:
        raise RuntimeError(f"Find failed: {data}")
    rows = (data.get("response") or {}).get("data") or []
    if not rows:
        return None
    rid = rows[0].get("recordId")
    return str(rid) if rid else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Push web asset to FileMaker via Data API")
    ap.add_argument("--html", required=True, type=Path, help="Path to HTML/text file")
    ap.add_argument(
        "--env",
        type=Path,
        default=Path(".env.local"),
        help="Env file with FM_DATA_API_* (default: ./.env.local)",
    )
    ap.add_argument("--layout", default="Data WEB_ASSETS", help="Layout used to write")
    ap.add_argument("--filename", default=None, help="FileName field value (default: html name)")
    ap.add_argument("--filename-field", default="FileName", help="Field that stores the file name")
    ap.add_argument("--content-field", default="Content", help="Field that stores the body")
    ap.add_argument("--mime-field", default="MimeType", help="Optional mime field (empty to skip)")
    ap.add_argument("--mime", default="text/html", help="MimeType value")
    ap.add_argument(
        "--find-layout",
        default=None,
        help="Lighter layout.response for Find (avoids downloading huge Content)",
    )
    ap.add_argument("--min-chars", type=int, default=0, help="Abort if file shorter than N chars")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--reload-hint",
        default="Run your Web Viewer reload/boot script in FileMaker Pro",
        help="Message printed after successful write",
    )
    args = ap.parse_args()

    html_path: Path = args.html
    if not html_path.is_file():
        raise SystemExit(f"File not found: {html_path}")
    content = html_path.read_text(encoding="utf-8")
    if args.min_chars and len(content) < args.min_chars:
        raise SystemExit(f"File too short: {len(content)} < {args.min_chars}")

    filename = args.filename or html_path.name
    print(f"file: {html_path} ({len(content)} chars) → {args.layout} / {filename}")
    if args.dry_run:
        print("dry-run: not writing to FileMaker")
        return 0

    if not args.env.is_file():
        raise SystemExit(f"Env file not found: {args.env}")
    env = load_env(args.env)
    token = login(env)
    try:
        base = env["FM_DATA_API_BASE_URL"].rstrip("/")
        db = env["FM_DATA_API_DATABASE"]
        layout_q = quote(args.layout, safe="")
        rid = find_record_id(
            env,
            token,
            layout=args.layout,
            filename=filename,
            filename_field=args.filename_field,
            find_layout=args.find_layout,
        )

        patch_fields: dict[str, str] = {args.content_field: content}
        if args.mime_field:
            patch_fields[args.mime_field] = args.mime

        create_fields = {
            args.filename_field: filename,
            **patch_fields,
        }

        if rid:
            url = f"{base}/databases/{db}/layouts/{layout_q}/records/{rid}"
            print(f"updating recordId={rid} …")
            out = curl_json("PATCH", url, token=token, body={"fieldData": patch_fields})
        else:
            url = f"{base}/databases/{db}/layouts/{layout_q}/records"
            print(f"creating record {filename} …")
            out = curl_json("POST", url, token=token, body={"fieldData": create_fields})

        if api_code(out) != "0":
            raise RuntimeError(f"Write failed: {out}")
        print(f"OK — {args.content_field} updated.")
        print(f"Next: {args.reload_hint}")
        return 0
    finally:
        logout(env, token)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(1)
