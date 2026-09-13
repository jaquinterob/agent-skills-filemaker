# Referencia — FileMaker fms-dev

Detalle opcional; leer solo si hace falta.

## Credenciales / env (agente)

En el repo del proyecto, `.env.local` (nunca commitear):

| Variable | Uso |
|----------|-----|
| `FM_DATA_API_BASE_URL` | `https://fms-dev.celerix.com/fmi/data/vLatest` |
| `FM_DATA_API_DATABASE` | Nombre del archivo en FMS |
| `FM_DATA_API_ACCOUNT` | Cuenta técnica con privilegio **fmrest** |
| `FM_DATA_API_PASSWORD` | Password de esa cuenta |

Dentro del `.fmp12`, tabla `DATA_API_ENV` con fila activa cuyo `HostMatch` coincida con el host de fms-dev.

## Layouts habituales

| Layout | Uso |
|--------|-----|
| `App Web` | Web Viewer + UI |
| `Data WEB_ASSETS` | Editar HTML a mano (fallback) |
| `API_*` | Layouts mínimos para Data API / Find / Set Field |

## Scripts: capas

| Prefijo | Rol |
|---------|-----|
| `API_*` | Lógica / JSON |
| `WV_Call_*` | Puente desde Web Viewer (`Perform Script`) |
| `*_DataApi` | Misma operación vía HTTP Data API (WebDirect) |
| `UTIL_DataApi_*` | Login token, Request, Http |
| `WV_*` | Boot, ForceShow, Reload, AfterWebReady |

## Anti-patrones

| No hacer | Por qué |
|----------|---------|
| `pbcopy` del `.xml` y pegar en Script Workspace | No es XMSS; no pegan pasos |
| Dar por hecho que el HTML del repo está en FMS | Hay que `fm_push` + `WV_ForceShow` |
| Pegar varios scripts sin confirmación | El portapapeles se pisa; el usuario se pierde |
| `UTIL_LoadIndexHtml` / file:// en hosted | Length=0 frecuente |
| Commit en layout App Web sin `$$SkipWVEnter` (WD) | Remonta WV → cae a vista empleado |
| Commit de `.env.local` o passwords | Secretos |

## Multi-tenant (Soltrech Ideas)

En fms-dev típico: ITG=1, CTG=2, SBX=4. Confirmar con `API_Tenants` si se recrea. `WEB_ASSETS` / `DATA_API_ENV` son globales; el aislamiento es por `TenantId` en datos de negocio.

## Smoke mínimo post-deploy

1. Abrir App Web (Pro o WebDirect en fms-dev).
2. Login admin + empleado.
3. Una lectura (listar ideas) y una escritura relevante al cambio.
4. Si tocaste Data API: verificar que WD no remonte el shell admin tras guardar.

## Herramientas del repo

```bash
# Push HTML
python3 tools/fm_push_index_html.py
python3 tools/fm_push_index_html.py --dry-run

# Regenerar + copiar script
python3 scripts/xml/txt_to_fmxml.py scripts/API_Foo.txt scripts/xml/API_Foo_steps.xml
python3 scripts/xml/copy_fm_clipboard.py scripts/xml/API_Foo_steps.xml
```

Dependencia Mac para XMSS: `pyobjc-framework-Cocoa`. Si falla el copy, fallback: FM Clipboard Tool (Codence).
