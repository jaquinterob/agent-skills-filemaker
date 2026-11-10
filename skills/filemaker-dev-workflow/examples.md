# Examples — FileMaker agent workflow

Fictional app. Names are illustrative; always replace with discovery results.

## Example A — Mature app: HTML tweak + one script

**Context:** Product repo `acme-orders`, hosted on `fms.example.com`, database `AcmeOrders`. Web Viewer already uses `WEB_ASSETS` / `WV_ForceShow`. Agent OS: macOS. `.env.local` present.

### 1. Discovery (agent shows)

```
FM_DISCOVERY
- mode: mature
- host: fms.example.com
- database: AcmeOrders
- webdirect_url: https://fms.example.com/fmi/webd/AcmeOrders
- ui: web_viewer+assets
- assets_table/layout: WEB_ASSETS / Data WEB_ASSETS
- content_field: Content
- filename_field: FileName
- html_path_in_git: web/index.html
- reload_script: WV_ForceShow
- script_sources: scripts/xml/*.xml
- converter_text_to_fmxmlsnippet: none (XML already committed)
- env_file: .env.local
- data_api_ready: yes
- tracker: none
- os_agent: macOS
```

### 2. Edit git

Agent changes `web/index.html` and updates `scripts/xml/API_ListOrders_steps.xml`.

### 3. Push HTML

```bash
SKILL_ROOT="$(python3 ~/.claude/skills/filemaker-dev-workflow/scripts/skill_root.py)"
# or ~/.cursor/... — whichever is installed

python3 "$SKILL_ROOT/scripts/fm_push_web_asset.py" \
  --html web/index.html \
  --env .env.local \
  --layout "Data WEB_ASSETS" \
  --filename index.html \
  --reload-hint "App Web → WV_ForceShow"
```

### 4. Message to human

```
HTML en FileMaker (Data API) → layout «Data WEB_ASSETS» / FileName «index.html».
Siguiente: layout «App Web» → ejecutar «WV_ForceShow».
Cuando el Web Viewer se refresque, responde «listo».
```

Human: `listo`.

### 5. One script

```bash
python3 "$SKILL_ROOT/scripts/copy_fm_clipboard.py" scripts/xml/API_ListOrders_steps.xml
```

```
Portapapeles listo (XMSS): «API_ListOrders».
Script Workspace → abrir ese script → seleccionar todos los pasos → Delete → Pegar → Save.
Responde «listo» / «siguiente» para el próximo.
(Cola restante: 0)
```

### 6. Smoke

- Pro: open App Web → list orders.
- WebDirect: same URL → list + one write if the change touched saves.
- Agent does **not** say “ya está en Server” until push + paste + reload confirmed.

---

## Example B — New app: propose stack only

**Context:** User wants a greenfield WebDirect UI. No `.fmp12` schema yet.

Agent does **not** invent a live host. It:

1. Sets `mode: new` in `FM_DISCOVERY` (unknowns left blank).
2. Proposes Recommended architecture from SKILL.md (`WEB_ASSETS`, Web Viewer, `data:text/html`).
3. Lists human setup steps: create table/fields, layout + Web Viewer options, empty reload script, `fmrest` account, `.env.local`.
4. Scaffolds `web/index.html` in git only.
5. Waits until human confirms schema + env before first `fm_push_web_asset.py`.

---

## Example C — Linux agent, script paste blocked

**Context:** Agent runs on Linux; HTML push via Data API works; need to update `API_Save`.

1. Push HTML normally with `fm_push_web_asset.py`.
2. For the script, do **not** run `copy_fm_clipboard.py` pretending it works.
3. Send the XMSS-unavailable template; offer Mac / Codence / manual steps from the XML path.
4. Continue only when the human confirms the script is pasted.

---

## Example D — No Data API yet

1. Discovery: `data_api_ready: no`.
2. Agent runs `copy_text_clipboard.py web/index.html`.
3. Human pastes into assets layout → Commit → reload.
4. Optionally help create `.env.local` so the next delivery can use Data API.
