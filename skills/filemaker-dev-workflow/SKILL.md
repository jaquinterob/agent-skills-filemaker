---
name: filemaker-dev-workflow
description: >-
  Generic FileMaker + AI agent collaboration on a shared FileMaker Server
  (dev/staging/prod): roles (agent vs human in Pro), deploy HTML to the .fmp12,
  paste scripts as XMSS one-at-a-time, WebDirect vs Pro / Data API pitfalls.
  Use when working with FileMaker, .fmp12, FileMaker Server, WebDirect, Web
  Viewer, WEB_ASSETS, Data API, XMSS, Script Workspace paste, fmxmlsnippet, or
  when the user asks how to deliver HTML/scripts from a git repo into FM.
---

# FileMaker — agent workflow (server-hosted)

How an **AI coding agent** and a **human in FileMaker Pro** collaborate on a
`.fmp12` hosted on **FileMaker Server**. Product-agnostic: apply to any app.

## Roles (do not invert)

| Who | Does |
|-----|------|
| **Agent** | Edits the git repo (HTML/JS, script sources, docs, tools). Prepares clipboard payloads. Pushes HTML when a project tool exists. Guides paste/reload. Never assumes “in git” means “in the .fmp12”. |
| **Human** | Everything that only FileMaker can do: tables, fields, relationships, layouts, privilege sets, creating empty scripts, pasting steps in Script Workspace, running reload/boot scripts, smoke tests in Pro and WebDirect. |

**Golden rule:** the Server `.fmp12` is the runtime. Git is the source of truth for *text*. Delivery is a separate step.

## Discover the project (first)

Before prescribing commands, inspect the repo and ask if unclear:

1. **Host / file:** FMS hostname, database name, WebDirect URL.
2. **UI pattern:** Web Viewer + HTML in a table (common) vs native layouts only.
3. **Script sources:** `.txt` / `.xml` under `scripts/` (or similar) vs scripts only inside FM.
4. **Deploy tools:** e.g. a Data API push script for HTML, or XMSS clipboard helpers. Use them if present; otherwise fall back to manual steps below.
5. **Tracker:** if the team uses ClickUp/Jira/etc., follow *that* project’s closing rules — do not invent a tracker.

Do not hardcode product names, tenants, or business features into this workflow.

## Mental model (typical HTML-in-FM app)

Many projects store the UI inside the file:

- One (or few) `.fmp12` on FMS.
- HTML/CSS/JS in a container/text table (often named like `WEB_ASSETS`) referenced by a Web Viewer.
- Browser/WebDirect talks to FM via `FileMaker.PerformScript` → scripts return JSON (or similar) back into the viewer.
- WebDirect often needs `data:text/html,...` (not `file://`) for the viewer.

**Suggested conventions** (adopt if the project has none):

| Layer | Convention |
|-------|------------|
| Tables | `UPPER_SNAKE` |
| Fields | `PascalCase` |
| Scripts | English names |
| End-user UI copy | Project language (often Spanish) |

Adapt to existing naming; do not rename a mature file for style alone.

## Delivery order (when both UI and scripts change)

### 1. HTML / web assets first

**Preferred (if the repo has a push tool + Data API credentials):** run that tool against the target environment (dev/staging/prod). Credentials live in local env files — never commit them.

**Fallback:** copy the HTML to the clipboard → open the assets layout in Pro → paste into the content field → Commit → run the project’s reload script (names vary: ForceShow, ReloadWeb, BuildWebHtml, etc.).

Avoid loading hosted Web Viewers via `file://` or fragile “Insert from URL” of a local path — on Server this often yields empty content.

Tell the human explicitly which reload/boot script to run after the push.

### 2. Scripts second — one at a time

FileMaker Script Workspace does **not** accept raw XML text paste. Steps must be on the clipboard as **XMSS** (FileMaker’s internal script-steps pasteboard type).

If the repo provides converters/helpers (e.g. text → fmxmlsnippet → XMSS clipboard), use them. Otherwise:

- Use a known XMSS clipboard utility (e.g. Codence FM Clipboard Tool), or
- Recreate steps manually from the documented source.

Human loop per script:

1. Open Script Workspace → target script  
2. Select all steps → Delete  
3. Paste → Save  

**Queue:** number the scripts; wait for **“listo” / “next” / “siguiente”** before putting the next one on the clipboard. Always state what is on the clipboard *now*.

After paste, spot-check that steps look complete (variables, URLs, layout names). Some step types (notably Insert from URL options) may need a one-time manual fix after paste.

## Pro vs WebDirect

| Client | Typical write path |
|--------|--------------------|
| **FileMaker Pro** | Native script steps (Set Field, Commit, etc.) |
| **WebDirect** | Prefer **Data API** (or other non-remounting path) for writes that would otherwise Commit on the Web Viewer layout and remount the HTML |

Keep sessions separate in your head:

- App session (logged-in end user) ≠ Data API technical session/token.

Environment config for Data API (host, database, technical account) usually lives in a table or globals inside the `.fmp12` and/or local `.env` for agent tools — confirm per project.

**WebDirect pitfall:** aggressive Commit / OnLayoutEnter on the viewer layout remounts the Web Viewer and can wipe in-memory UI state (roles, shells, SPA state). Use project guards (skip flags, no reassign of viewer source after ready) when editing those scripts.

## Collaboration style

1. Prefer short, numbered paste/reload instructions the human can follow without guessing.
2. Ship small, testable slices; state smoke steps for Pro and/or WebDirect.
3. Match the user’s language for chat (often Spanish); keep script identifiers as in the file.
4. Never claim something is live on Server until push/paste + reload were done (or the user confirmed).

## Close-out (if the team tracks work)

When finishing a slice, leave a trail in the team’s tracker:

- What changed (UI / scripts / schema)
- Git commit/PR if any
- What was pasted or pushed into FM
- What to smoke / what remains

Record **real** time only; ask if unknown. Mark done only when the deliverable is actually in FM or explicitly deferred.

## Quick checklist

```
- [ ] Repo changes ready
- [ ] HTML/assets delivered into .fmp12 + reload run
- [ ] Scripts pasted one-by-one (XMSS) with confirmation between each
- [ ] Smoke on Pro and/or WebDirect on the target host
- [ ] Tracker note (if the team uses one)
```

## More detail

- [reference.md](reference.md) — env vars, anti-patterns, optional tool patterns
