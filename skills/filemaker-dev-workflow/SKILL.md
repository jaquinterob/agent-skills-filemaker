---
name: filemaker-dev-workflow
description: >-
  Product-agnostic FileMaker Server collaboration between an AI agent and a
  human in FileMaker Pro: discover host/file, deliver HTML into WEB_ASSETS via
  Data API, paste scripts as XMSS one-at-a-time, Web Viewer + data:text/html
  architecture, Pro vs WebDirect pitfalls. Ships scripts/ tools. Use when the
  user mentions FileMaker, .fmp12, FileMaker Server, WebDirect, Web Viewer,
  WEB_ASSETS, Data API, XMSS, fmxmlsnippet, Script Workspace, pegar scripts,
  empujar HTML, fms-dev, or delivering git HTML/scripts into a hosted .fmp12.
---

# FileMaker — agent workflow (server-hosted)

How an **AI agent** and a **human in FileMaker Pro** collaborate on a `.fmp12`
hosted on **FileMaker Server**. Works with Cursor, Claude Code, Codex, and any
host that loads Agent Skills. Product-agnostic.

## What this skill does / does not

| Does | Does **not** |
|------|----------------|
| Define agent vs human roles | Create tables/layouts/scripts inside FM by itself |
| Push HTML into assets via Data API | Convert free text → fmxmlsnippet (use product converter or hand-built XML) |
| Copy HTML/XMSS to clipboard for human paste | Claim “live on Server” before push/paste + reload |
| Recommend Web Viewer + `WEB_ASSETS` for new apps | Rename mature schemas “for style” |
| Guide one-script-at-a-time paste queues | Paste many scripts without human “listo” / “next” |

## Resolve `SKILL_ROOT` (portable)

Before running tools, set `SKILL_ROOT` to the folder that contains **this**
`SKILL.md` and `scripts/`. Prefer:

```bash
# 1) Prefer the directory of this loaded skill (host-specific). Else first hit:
for d in \
  "$HOME/.claude/skills/filemaker-dev-workflow" \
  "$HOME/.cursor/skills/filemaker-dev-workflow" \
  "$HOME/.codex/skills/filemaker-dev-workflow"; do
  [ -f "$d/SKILL.md" ] && [ -d "$d/scripts" ] && SKILL_ROOT="$d" && break
done
# 2) Or from a clone: .../agent-skills-filemaker/skills/filemaker-dev-workflow
# 3) Or: python3 path/to/scripts/skill_root.py   → prints absolute skill root
```

Any script under `scripts/` can also be invoked by absolute path; its parent’s
parent **is** `SKILL_ROOT`. Prefer product-repo equivalents if they exist.

**Deps:** `curl` + `python3`. XMSS paste on macOS: `pip3 install pyobjc-framework-Cocoa`.

## Decision flow (run first)

```
1. Mode?
   ├─ new app     → propose Recommended architecture; human builds schema/UI
   └─ mature app  → discover existing names; adapt; do not rename for style
2. Change type?
   ├─ HTML/CSS/JS only → Delivery §1 then reload
   ├─ FM scripts only  → Delivery §2 (queue)
   └─ both             → HTML first, then scripts one-by-one
3. Data API env present? (.env.local or equivalent)
   ├─ yes → prefer fm_push_web_asset.py
   └─ no  → ask for env OR use copy_text_clipboard.py fallback
4. OS for clipboard?
   ├─ macOS → all scripts OK (XMSS needs PyObjC)
   ├─ Linux → plain-text HTML OK; XMSS not supported → tell human to use Codence/MBS or paste on a Mac
   └─ Windows → plain-text HTML via clip; XMSS not supported → same as Linux
```

## Discovery (mandatory before delivery)

Fill and show this block. Ask for unknowns — do not invent host/DB/script names.

```
FM_DISCOVERY
- mode: new | mature
- host: 
- database: 
- webdirect_url: 
- ui: web_viewer+assets | native_only | mixed | unknown
- assets_table/layout: 
- content_field: 
- filename_field: 
- html_path_in_git: 
- reload_script: 
- script_sources: path/pattern | inside_fm_only
- converter_text_to_fmxmlsnippet: path | none
- env_file: 
- data_api_ready: yes | no | unknown
- tracker: none | clickup | jira | other
- os_agent: macOS | linux | windows
```

## Roles (do not invert)

| Who | Does |
|-----|------|
| **Agent** | Edits git; runs skill/product tools; guides paste/reload; never equates git with the live `.fmp12`. |
| **Human** | Tables, fields, layouts, privileges, empty scripts, Script Workspace paste, reload/boot, smoke Pro/WebDirect. |

**Golden rule:** Server `.fmp12` = runtime. Git = source of truth for *text*. Delivery is a separate step.

## New app vs mature app

| | **New app** | **Mature app** |
|--|-------------|----------------|
| Schema | Propose `WEB_ASSETS` + Web Viewer stack below | Discover real table/layout/field/script names |
| Naming | Suggest `UPPER_SNAKE` tables, `PascalCase` fields, English scripts | Keep existing identifiers |
| Tools | Use this skill’s `scripts/` | Prefer product-repo tools if equivalent |

### Recommended architecture (default for **new** apps)

| Layer | Recommendation |
|-------|----------------|
| Runtime | One `.fmp12` on FMS (+ WebDirect if needed) |
| UI | Layout + **Web Viewer** (interaction + “Allow JavaScript to perform FileMaker scripts”) |
| Storage | Table **`WEB_ASSETS`**, field **`Content`** = full HTML (+ inline CSS/JS) |
| Identity | `FileName` (+ optional `MimeType`, `FolderPath`) |
| Viewer source | Global/calc = `"data:text/html," & WEB_ASSETS::Content` |
| Git `web/` | Dev only — not a folder deploy on Server |
| Bridge | JS → `FileMaker.PerformScript(name, json)` → FM → JSON / `Perform JavaScript` |

Why: WebDirect is unreliable with `file://` and external `<link>`/`<script src>`. Ship one packaged HTML. After push, human runs reload/boot (names vary: ForceShow, ReloadWeb, BuildWebHtml).

## Tools

| Script | When | Command |
|--------|------|---------|
| `scripts/skill_root.py` | Print absolute `SKILL_ROOT` | `python3 …/scripts/skill_root.py` |
| `scripts/fm_push_web_asset.py` | HTML → FM via Data API (preferred) | `python3 "$SKILL_ROOT/scripts/fm_push_web_asset.py" --html web/index.html --env .env.local` |
| `scripts/copy_text_clipboard.py` | Fallback: plain-text HTML clipboard | `python3 "$SKILL_ROOT/scripts/copy_text_clipboard.py" web/index.html` |
| `scripts/copy_fm_clipboard.py` | Script steps as **XMSS** (macOS only) | `python3 "$SKILL_ROOT/scripts/copy_fm_clipboard.py" path/to/Script_steps.xml` |

Rules:

1. Prefer these (or product equivalents) over ad-hoc `pbcopy` / invented curl.
2. Never `pbcopy` raw `.xml` into Script Workspace — that is not XMSS.
3. If a product converter (text → fmxmlsnippet) exists, run it **before** `copy_fm_clipboard.py`.
4. Env for push: `FM_DATA_API_BASE_URL`, `FM_DATA_API_DATABASE`, `FM_DATA_API_ACCOUNT`, `FM_DATA_API_PASSWORD`.

```bash
python3 "$SKILL_ROOT/scripts/fm_push_web_asset.py" \
  --html web/index.html --env .env.local \
  --layout "Data WEB_ASSETS" --filename index.html \
  --find-layout "App Web" \
  --reload-hint "App Web → run your reload/ForceShow script"
```

## Delivery order

### 1. HTML first

```bash
python3 "$SKILL_ROOT/scripts/fm_push_web_asset.py" --html web/index.html --env .env.local
```

Then send the human the **reload** template below.

Fallback (no Data API / push failed):

```bash
python3 "$SKILL_ROOT/scripts/copy_text_clipboard.py" web/index.html
```

→ human pastes into assets layout → Commit → reload.

### 2. Scripts second — one at a time

Input must already be **fmxmlsnippet** XML (or converted by the product tool).

```bash
python3 "$SKILL_ROOT/scripts/copy_fm_clipboard.py" path/to/Script_steps.xml
```

**Queue:** wait for “listo” / “next” / “siguiente” before the next script. Always state what is on the clipboard *now*.

## Human message templates (use these)

**After HTML push (Data API):**
```
HTML en FileMaker (Data API) → layout «{layout}» / FileName «{filename}».
Siguiente: layout «{app_layout}» → ejecutar «{reload_script}».
Cuando el Web Viewer se refresque, responde «listo».
```

**After HTML clipboard fallback:**
```
HTML en el portapapeles (texto plano).
FileMaker: layout «{assets_layout}» → campo Content → pegar → Commit → «{reload_script}».
Responde «listo» cuando termine.
```

**Script paste (one):**
```
Portapapeles listo (XMSS): «{script_name}».
Script Workspace → abrir ese script → seleccionar todos los pasos → Delete → Pegar → Save.
Responde «listo» / «siguiente» para el próximo.
(Cola restante: {n})
```

**XMSS unavailable (Linux/Windows):**
```
No puedo poner XMSS en el portapapeles en este OS.
Opciones: (1) pegar desde un Mac con copy_fm_clipboard.py, (2) Codence FM Clipboard Tool / MBS, (3) recrear pasos a mano desde el XML en {path}.
```

**Never claim live until:** push or paste confirmed **and** reload (or user confirms).

## Pro vs WebDirect

| Client | Typical writes |
|--------|----------------|
| **Pro** | Native Set Field / Commit |
| **WebDirect** | Prefer Data API (or non-remounting path) so the Web Viewer does not remount |

App session ≠ Data API technical token. Heavy Commit on the viewer layout in WD remounts HTML and can wipe UI state.

## Collaboration style

1. Short numbered paste/reload steps (templates above).
2. Small slices + explicit smoke.
3. Match the user’s chat language; keep FM identifiers as in the file.
4. Close-out if they track work: UI/scripts/schema, git ref, pushed/pasted, smoke/remaining — real time only.

## Quick checklist

```
- [ ] FM_DISCOVERY filled
- [ ] Repo changes ready
- [ ] HTML: push or clipboard + reload
- [ ] Scripts: XMSS one at a time (or OS fallback explained)
- [ ] Smoke Pro and/or WebDirect
- [ ] Tracker note (only if team uses one)
```

## More detail

- [reference.md](reference.md) — glossary, env, OS matrix, anti-patterns, script XML notes, multi-env
- [examples.md](examples.md) — end-to-end walkthrough (fictional app)
