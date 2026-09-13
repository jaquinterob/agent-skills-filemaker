---
name: filemaker-dev-workflow
description: >-
  Flujo de colaboración FileMaker en servidor de desarrollo (fms-dev): roles
  agente vs usuario, push HTML vía Data API, pegado XMSS de scripts de a uno,
  WebDirect vs Pro, y cierre en ClickUp. Use when working on FileMaker projects
  hosted on fms-dev, Soltrech Ideas, WEB_ASSETS, WV_ForceShow, copy_fm_clipboard,
  fm_push_index_html, scripts/*.txt, XMSS paste, Data API, WebDirect, or when
  the user mentions FileMaker Server, pegar scripts, o desplegar HTML al .fmp12.
---

# FileMaker — workflow en fms-dev

Cómo trabajamos **tú (usuario en FileMaker Pro)** y **yo (agente de código: Cursor, Claude Code, Codex u otro)** contra el archivo alojado en **FileMaker Server de desarrollo**.

**Dev server de referencia:** `fms-dev.celerix.com`  
WebDirect: `https://fms-dev.celerix.com/fmi/webd/...`  
Data API: `https://fms-dev.celerix.com/fmi/data/vLatest`

## Roles (no invertirlo)

| Quién | Hace |
|-------|------|
| **Agente** | Código en repo (`web/`, `scripts/*.txt`, `scripts/xml/`, `docs/`, tools). Genera XML, empuja HTML por Data API, copia XMSS al portapapeles, guía el pegado, registra ClickUp. |
| **Usuario** | Todo lo que solo se puede hacer en FileMaker: tablas/campos/layouts, crear scripts vacíos, pegar XMSS en Script Workspace, ejecutar `WV_ForceShow`, smoke en Pro/WebDirect. |

**Regla de oro:** archivos en Git **no** están en el `.fmp12` hasta que se empujen (HTML) o se peguen (scripts). Nunca dar por desplegado un cambio solo porque está en el repo.

## Arquitectura mental

- Un solo `.fmp12` en FMS (p. ej. `SoltrechIdeas.fmp12`).
- UI HTML vive en `WEB_ASSETS::Content` (no carpeta `web/` en el servidor).
- `web/` en Git = fuente de desarrollo.
- Comunicación: JS → `FileMaker.PerformScript` → scripts `API_*` / `WV_Call_*` → JSON de vuelta.
- WebDirect carga HTML con `data:text/html,` + `WV_BuildWebHtml` / `WV_ForceShow`.

Convenciones: tablas `MAYUSCULAS_`, campos PascalCase, scripts en inglés, UI en español.

## Entrega obligatoria (orden fijo)

Cuando cambien `web/index.html` y/o `scripts/`:

### 1. HTML primero

```bash
python3 tools/fm_push_index_html.py
```

Requiere `.env.local` con `FM_DATA_API_*` apuntando a **fms-dev**.

Luego decir al usuario: layout **App Web** → ejecutar **`WV_ForceShow`** (o `WV_ReloadWeb`).

Fallback solo si Data API falla:

```bash
pbcopy < web/index.html
```

→ layout `Data WEB_ASSETS` → `FileName=index.html` → pegar en `Content` → Commit → `WV_ForceShow`.

Evitar `UTIL_LoadIndexHtml` / `Insert from URL` file:// en hosted (suele Length=0).

### 2. Scripts después, de a uno

Si cambió el `.txt`, regenerar XML:

```bash
python3 scripts/xml/txt_to_fmxml.py scripts/<Script>.txt scripts/xml/<Script>_steps.xml
```

Copiar al portapapeles en formato **XMSS** (nunca `pbcopy` del XML crudo):

```bash
python3 scripts/xml/copy_fm_clipboard.py scripts/xml/<Script>_steps.xml
```

Usuario en Script Workspace: abrir script → ⌘A → Delete → ⌘V → ⌘S.

**Cola:** numerar scripts; avanzar solo cuando el usuario diga **“listo”** / **“siguiente”**. Decir qué hay en el portapapeles **ahora**.

Tras pegar: validar que los pasos se vean completos (variables, Insert from URL, etc.). Algunos pasos (p. ej. Insert from URL en `UTIL_DataApi_Http`) pueden requerir ajuste manual una vez.

## Pro vs WebDirect

- **Pro (escritorio):** escrituras clásicas (`WV_Call_Save*`, Commit local).
- **WebDirect:** escrituras vía **Data API** (`*_DataApi`) para no remontar el Web Viewer.
- El HTML decide el bridge (`callWrite` / flags `DATA_API_WRITES`).
- Token Data API (`$$DataApiToken`) ≠ sesión de la app (`$$CurrentUserId`).
- Config por ambiente en tabla `DATA_API_ENV` (fila `dev` / HostMatch de fms-dev).

No hacer `Commit` agresivo sobre layouts ligados a App Web en WD sin `$$SkipWVEnter` — remonta el WV y pierde el shell admin.

## Estilo de colaboración

1. Guías por fase en `docs/FASE-*.md`: el usuario construye en FM; el agente prepara pasos y revisa.
2. Cambios pequeños y verificables; smoke explícito (qué probar en Pro y/o WebDirect).
3. Responder en español; instrucciones de pegado claras y numeradas.
4. No inventar que algo ya está en el Server: preguntar o guiar el push/pegado.

## Cierre (ClickUp)

Al entregar o cerrar trabajo:

1. Comentario en la tarjeta: resumen, commit + link GitHub, push/rama, qué se pegó en FM, smoke/pendientes.
2. Tiempo: **solo horas reales**; si no hay cifra clara, preguntar.
3. Closed solo cuando el entregable esté hecho o acordado.

## Checklist rápida

```
- [ ] Código en repo
- [ ] HTML: fm_push_index_html.py → WV_ForceShow
- [ ] Scripts: txt_to_fmxml (si aplica) → copy_fm_clipboard → pegar uno a uno
- [ ] Smoke Pro y/o WebDirect en fms-dev
- [ ] Comentario ClickUp (+ tiempo real)
```

## Más detalle

- [reference.md](reference.md) — env Data API, anti-patrones, layout mínimo, multi-tenant SBX
