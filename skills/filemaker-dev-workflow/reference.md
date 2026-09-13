# Reference — FileMaker agent workflow

Optional detail. Product-agnostic.

## Credentials (agent tools)

If the project pushes HTML or data via Data API from the agent machine, keep secrets in a **local** env file (e.g. `.env.local`), never in git:

| Typical variable | Meaning |
|------------------|---------|
| `FM_DATA_API_BASE_URL` | `https://<fms-host>/fmi/data/vLatest` |
| `FM_DATA_API_DATABASE` | Exact file name on FMS |
| `FM_DATA_API_ACCOUNT` | Technical account with **fmrest** |
| `FM_DATA_API_PASSWORD` | That account’s password |

Inside the `.fmp12`, many teams also store per-environment rows (host match, base URL, account) so WebDirect scripts can call Data API without hardcoding.

## Layout patterns (common, not mandatory)

| Kind | Role |
|------|------|
| App / shell layout | Hosts the Web Viewer |
| Assets layout | Edit stored HTML/CSS/JS records by hand |
| Thin `API_*` layouts | Minimal fields for Find / Set Field / Data API |

Names vary by project — discover from the file or docs.

## Script layering (optional convention)

| Prefix / suffix | Role |
|-----------------|------|
| `API_*` | Business logic + JSON (or equivalent) response |
| Bridge / `WV_Call_*` | Thin entry from Web Viewer → API script |
| `*_DataApi` | Same operation via HTTP Data API (WebDirect-friendly) |
| `UTIL_*` | Shared helpers (token, HTTP, encoding) |
| Boot / reload | Load or refresh the Web Viewer HTML |

Use whatever the project already uses.

## Anti-patterns

| Don’t | Why |
|-------|-----|
| `pbcopy` raw `.xml` into Script Workspace | Not XMSS — paste does nothing useful |
| Assume git == Server | Must push/paste + reload |
| Paste many scripts without confirmation | Clipboard overwrite; human loses place |
| `file://` HTML on hosted FMS | Often empty / Length 0 |
| Heavy Commit on the Web Viewer layout in WebDirect | Remounts viewer; loses UI state |
| Commit secrets (`.env`, passwords) | Leak risk |

## Smoke (generic)

After delivery:

1. Open the app layout (Pro and/or WebDirect on the target host).
2. Exercise auth / main entry if the change touches it.
3. One read and one write path related to the change.
4. If WebDirect + Data API writes: confirm the viewer does **not** remount / lose session shell after save.

## Optional repo helpers

Projects may include scripts such as:

- Push HTML → assets table via Data API
- Convert human-readable script text → `fmxmlsnippet` XML
- Copy XML to macOS clipboard as XMSS (often needs PyObjC / Cocoa pasteboard)

If missing, fall back to manual paste utilities (e.g. Codence FM Clipboard Tool) or hand-built steps.

## Multi-environment

When moving a file across hosts:

1. Host `.fmp12` on the target FMS; enable Data API if used.
2. Technical account with **fmrest** + outbound URL privileges as needed.
3. Environment row / config for that host.
4. Confirm Web Viewer HTML is current; run reload.
5. Smoke login + one write.

Isolation (tenants, companies, sandboxes) is **per product** — read that project’s docs; do not assume IDs or names from other apps.
