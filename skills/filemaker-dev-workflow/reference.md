# Reference — FileMaker agent workflow

Optional detail. Product-agnostic. Read when SKILL.md is not enough.

## Glossary

| Term | Meaning |
|------|---------|
| **`.fmp12`** | FileMaker database file; on Server it is the runtime. |
| **FMS** | FileMaker Server — hosts the file for Pro / WebDirect / Data API. |
| **WebDirect** | Browser client for a hosted `.fmp12`. |
| **Web Viewer** | Layout object that renders HTML; can call FM scripts from JS. |
| **`WEB_ASSETS`** | Recommended table storing HTML (and related text assets) in a `Content` field. |
| **Data API** | HTTP API (`/fmi/data/vLatest`) for reads/writes with an `fmrest` account. |
| **fmxmlsnippet** | XML envelope FileMaker uses for clipboard snippets (scripts, layout objects, etc.). |
| **XMSS** | Clipboard flavor/UTI for **script steps**. Plain XML via `pbcopy` is **not** XMSS. |
| **Reload / boot / ForceShow** | Script that rebuilds `data:text/html,...` and refreshes the Web Viewer. Names vary. |

## Credentials (agent tools)

Local env file only (e.g. `.env.local`), never commit:

| Variable | Meaning |
|----------|---------|
| `FM_DATA_API_BASE_URL` | `https://<fms-host>/fmi/data/vLatest` |
| `FM_DATA_API_DATABASE` | Exact file name on FMS |
| `FM_DATA_API_ACCOUNT` | Technical account with **fmrest** |
| `FM_DATA_API_PASSWORD` | That account’s password |

Many teams also keep per-environment rows inside the `.fmp12` (host match, base URL, account) so WebDirect scripts can call Data API without hardcoding.

## OS / clipboard matrix

| Task | macOS | Linux | Windows |
|------|-------|-------|---------|
| Push HTML via Data API | ✅ `fm_push_web_asset.py` | ✅ | ✅ |
| Plain-text HTML clipboard | ✅ `pbcopy` | ✅ `wl-copy` / `xclip` | ✅ `clip` (UTF-16 via script) |
| XMSS script-step clipboard | ✅ PyObjC + `copy_fm_clipboard.py` | ❌ | ❌ |

On Linux/Windows for scripts: use a Mac for XMSS, or Codence FM Clipboard Tool / MBS Plugin, or recreate steps manually. Do not pretend `pbcopy`/`xclip` of raw XML will paste as steps.

## Recommended UI stack (Web Viewer)

Default for **new** apps:

1. Layout (e.g. `App Web`) hosts a full-bleed Web Viewer.
2. Viewer: Allow interaction + Allow JavaScript to perform FileMaker scripts.
3. Source = `"data:text/html," & <asset>::Content` via global/calc (e.g. `$$WebHtmlSource`).
4. Table `WEB_ASSETS`: `FileName`, `Content` (HTML+CSS+JS), `MimeType`, optional `FolderPath`.
5. Git `web/` is edited by the agent; runtime is always the field inside the `.fmp12`.

Do **not** recommend external CDN / `file://` as the primary WebDirect delivery path.

### `WEB_ASSETS` schema

| Field | Type | Role |
|-------|------|------|
| `FileName` | Text | e.g. `index.html` |
| `Content` | Text | Full HTML (inline CSS/JS) |
| `MimeType` | Text | e.g. `text/html` |
| `FolderPath` | Text | Optional |
| `UpdatedAt` | Timestamp | Optional |

## Layout patterns

| Kind | Role |
|------|------|
| App / shell | Hosts the Web Viewer |
| Assets (e.g. `Data WEB_ASSETS`) | Edit `Content` / Data API target |
| Thin `API_*` | Minimal fields for Find / Set Field / Data API |

Discover names from the file if it already exists.

## Script layering (optional)

| Prefix / suffix | Role |
|-----------------|------|
| `API_*` | Business logic + JSON response |
| `WV_Call_*` | Thin Web Viewer → API entry |
| `*_DataApi` | Same op via HTTP Data API (WD-friendly) |
| `UTIL_*` | Helpers (token, HTTP, encoding) |
| Boot / reload | Refresh Web Viewer HTML |

Use whatever the project already uses.

## Script XML (fmxmlsnippet) — agent rules

- `copy_fm_clipboard.py` expects a file that **already** contains `fmxmlsnippet` (script steps).
- This skill does **not** ship a text→XML converter (formats and FM versions vary).
- If the product repo has a converter, run it first; then XMSS copy.
- Minimal shape (illustrative — real step XML is verbose and version-sensitive):

```xml
<fmxmlsnippet type="FMObjectList">
  <Step><!-- … exported or tool-generated steps … --></Step>
</fmxmlsnippet>
```

- Valid sources: FM export/copy via a proper XMSS tool, Codence, product generator, or hand-maintained XML known to paste in the target FM version.
- If only prose/pseudocode exists, give the human step-by-step instructions — do **not** invent full fmxmlsnippet and claim it will paste.

## Anti-patterns

| Don’t | Why |
|-------|-----|
| `pbcopy` raw `.xml` into Script Workspace | Not XMSS |
| Assume git == Server | Must push/paste + reload |
| Paste many scripts without confirmation | Clipboard overwrite |
| `file://` HTML on hosted FMS | Often empty / Length 0 |
| Heavy Commit on Web Viewer layout in WebDirect | Remounts viewer; loses UI state |
| Commit secrets (`.env`, passwords) | Leak risk |
| Invent host/DB/reload script names | Breaks delivery; ask in discovery |
| Rename mature schema for cosmetics | Unnecessary migration risk |

## Smoke (generic)

1. Open app layout (Pro and/or WebDirect on target host).
2. Exercise auth / main entry if touched.
3. One read and one write related to the change.
4. If WebDirect + Data API writes: confirm viewer does **not** remount / lose shell after save.

## Bundled tools

| Script | Role |
|--------|------|
| `scripts/skill_root.py` | Print absolute skill root |
| `scripts/fm_push_web_asset.py` | PATCH/POST HTML via Data API |
| `scripts/copy_text_clipboard.py` | Plain-text clipboard (macOS/Linux/Windows) |
| `scripts/copy_fm_clipboard.py` | XMSS clipboard (macOS + PyObjC only) |

Always prefer these (or product equivalents) over ad-hoc commands.

## Multi-environment

1. Host `.fmp12` on target FMS; enable Data API if used.
2. Technical account with **fmrest** (+ URL privileges as needed).
3. Environment row / config for that host.
4. Confirm Web Viewer HTML is current; run reload.
5. Smoke login + one write.

Isolation (tenants, companies, sandboxes) is **per product** — read that project’s docs.
