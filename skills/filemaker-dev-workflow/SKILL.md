---
name: filemaker-dev-workflow
description: >-
  Generic FileMaker + AI agent collaboration on a shared FileMaker Server
  (dev/staging/prod): roles (agent vs human in Pro), deploy HTML to the .fmp12,
  paste scripts as XMSS one-at-a-time, WebDirect vs Pro / Data API pitfalls.
  Ships executable scripts under scripts/. Use when working with FileMaker,
  .fmp12, FileMaker Server, WebDirect, Web Viewer, WEB_ASSETS, Data API, XMSS,
  Script Workspace paste, fmxmlsnippet, or when the user asks how to deliver
  HTML/scripts from a git repo into FM.
---

# FileMaker — agent workflow (server-hosted)

How an **AI coding agent** and a **human in FileMaker Pro** collaborate on a
`.fmp12` hosted on **FileMaker Server**. Product-agnostic: apply to any app.

## Tools (agent must execute these)

Scripts live in this skill’s `scripts/` directory. Resolve the skill root first
(wherever it is installed), then run with `python3`:

```bash
SKILL_ROOT="$HOME/.cursor/skills/filemaker-dev-workflow"
# Also valid if installed via Claude/Codex:
#   $HOME/.claude/skills/filemaker-dev-workflow
#   $HOME/.codex/skills/filemaker-dev-workflow
# Or the clone: .../agent-skills-filemaker/skills/filemaker-dev-workflow
```

| Script | When | Command |
|--------|------|---------|
| `scripts/fm_push_web_asset.py` | Deliver HTML into FM via Data API (preferred) | `python3 "$SKILL_ROOT/scripts/fm_push_web_asset.py" --html web/index.html --env .env.local` |
| `scripts/copy_text_clipboard.py` | Fallback: plain-text HTML to clipboard | `python3 "$SKILL_ROOT/scripts/copy_text_clipboard.py" web/index.html` |
| `scripts/copy_fm_clipboard.py` | Put script steps on clipboard as **XMSS** | `python3 "$SKILL_ROOT/scripts/copy_fm_clipboard.py" path/to/Script_steps.xml` |

**Rules for the agent:**

1. Prefer `$SKILL_ROOT/scripts/...` over inventing one-off paste commands.
2. Never `pbcopy` raw `.xml` for Script Workspace — that is not XMSS; use `copy_fm_clipboard.py`.
3. If the **product repo** already has equivalent tools, use those instead (same job).
4. If a script converter exists in the product repo (text → fmxmlsnippet), run it **before** `copy_fm_clipboard.py`. This skill does not ship a converter (formats vary by project).
5. Dependencies: `curl`; for XMSS on Mac: `pip3 install pyobjc-framework-Cocoa`.

### `fm_push_web_asset.py` options

```bash
python3 "$SKILL_ROOT/scripts/fm_push_web_asset.py" \
  --html web/index.html \
  --env .env.local \
  --layout "Data WEB_ASSETS" \
  --filename index.html \
  --find-layout "App Web" \
  --reload-hint "App Web → run your reload/ForceShow script"
```

Needs `FM_DATA_API_BASE_URL`, `FM_DATA_API_DATABASE`, `FM_DATA_API_ACCOUNT`, `FM_DATA_API_PASSWORD` in the env file.

## Roles (do not invert)

| Who | Does |
|-----|------|
| **Agent** | Edits git; runs the tools above; guides paste/reload. Never assumes “in git” means “in the .fmp12”. |
| **Human** | Tables, fields, layouts, privileges, create empty scripts, paste in Script Workspace, run reload/boot, smoke Pro/WebDirect. |

**Golden rule:** the Server `.fmp12` is the runtime. Git is the source of truth for *text*. Delivery is a separate step.

## Discover the project (first)

1. **Host / file:** FMS hostname, database name, WebDirect URL.
2. **UI pattern:** Web Viewer + HTML table vs native layouts only.
3. **Script sources:** `.txt` / `.xml` under `scripts/` vs only inside FM.
4. **Env file** for Data API (usually `.env.local` in the product repo).
5. **Tracker:** follow the team’s ClickUp/Jira rules if any — do not invent one.

Do not hardcode product names, tenants, or business features.

## Mental model (typical HTML-in-FM app)

- One (or few) `.fmp12` on FMS.
- HTML in a text/container table (often `WEB_ASSETS`) + Web Viewer.
- JS → `FileMaker.PerformScript` → scripts → JSON back.
- WebDirect usually needs `data:text/html,...` (not `file://`).

Suggested conventions if the project has none: tables `UPPER_SNAKE`, fields `PascalCase`, scripts English, UI copy in the project language.

## Delivery order

### 1. HTML first

```bash
python3 "$SKILL_ROOT/scripts/fm_push_web_asset.py" --html web/index.html --env .env.local
```

Then tell the human which reload script to run.

Fallback if Data API fails:

```bash
python3 "$SKILL_ROOT/scripts/copy_text_clipboard.py" web/index.html
```

→ human pastes into assets layout → Commit → reload.

### 2. Scripts second — one at a time

```bash
# If the product repo has a converter, run it first, then:
python3 "$SKILL_ROOT/scripts/copy_fm_clipboard.py" path/to/Script_steps.xml
```

Human: Script Workspace → select all → Delete → Paste → Save.

**Queue:** wait for “listo” / “next” / “siguiente” before the next script. State what is on the clipboard *now*.

## Pro vs WebDirect

| Client | Typical write path |
|--------|--------------------|
| **Pro** | Native Set Field / Commit |
| **WebDirect** | Prefer Data API (or non-remounting path) so the Web Viewer does not remount |

App session ≠ Data API technical token. Heavy Commit on the viewer layout in WD remounts HTML and can wipe UI state.

## Collaboration style

1. Short numbered paste/reload instructions.
2. Small slices + explicit smoke steps.
3. Match the user’s chat language; keep FM identifiers as in the file.
4. Never claim “live on Server” until push/paste + reload (or user confirm).

## Close-out (if the team tracks work)

Summarize UI/scripts/schema, git ref, what was pushed/pasted, smoke/remaining. Real time only; ask if unknown.

## Quick checklist

```
- [ ] Repo changes ready
- [ ] fm_push_web_asset.py (or clipboard fallback) + reload
- [ ] copy_fm_clipboard.py one script at a time
- [ ] Smoke Pro and/or WebDirect
- [ ] Tracker note (if any)
```

## More detail

- [reference.md](reference.md) — env, anti-patterns, multi-environment
