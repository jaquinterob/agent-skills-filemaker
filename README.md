# Agent Skills — FileMaker (fms-dev)

Skills portables (estándar [Agent Skills](https://agentskills.io) / `SKILL.md`) para trabajar proyectos FileMaker en el servidor de desarrollo **fms-dev**.

Compatible con **Cursor**, **Claude Code**, **Codex** y cualquier herramienta que lea carpetas `SKILL.md`.

## Skills incluidas

| Skill | Qué cubre |
|-------|-----------|
| [`filemaker-dev-workflow`](skills/filemaker-dev-workflow/) | Roles agente↔usuario, push HTML (Data API), pegado XMSS de a uno, Pro vs WebDirect, ClickUp |

## Mejor forma de distribuir (recomendado)

1. **Este repo** como fuente de verdad del equipo.
2. Cada compañero **clona e instala** en su máquina (o lo enlaza el agente).
3. Opcional: copiar la skill también a un repo de producto (`.cursor/skills/` + `.claude/skills/`) si solo aplica a ese proyecto.

No hace falta un plugin distinto por herramienta: el formato es el mismo folder + `SKILL.md`.

```
agent-skills-filemaker/
├── README.md
├── install.sh
└── skills/
    └── filemaker-dev-workflow/
        ├── SKILL.md
        └── reference.md
```

## Instalación rápida

```bash
git clone https://github.com/jaquinterob/agent-skills-filemaker.git
cd agent-skills-filemaker
./install.sh          # Cursor + Claude + Codex (symlink)
# ./install.sh --copy # copia en vez de symlink
# ./install.sh cursor # solo Cursor
```

### Dónde queda instalada

| Herramienta | Ruta personal |
|-------------|---------------|
| Cursor | `~/.cursor/skills/<skill>/` |
| Claude Code | `~/.claude/skills/<skill>/` |
| Codex | `~/.codex/skills/<skill>/` |

### Solo un proyecto (compartir con quien clone el producto)

Copia o submodule dentro del repo de la app:

```bash
# Ejemplo en un repo FileMaker
mkdir -p .cursor/skills .claude/skills
cp -R /ruta/a/agent-skills-filemaker/skills/filemaker-dev-workflow .cursor/skills/
cp -R /ruta/a/agent-skills-filemaker/skills/filemaker-dev-workflow .claude/skills/
```

Cursor lee `.cursor/skills/`; Claude Code lee `.claude/skills/`. Conviene duplicar (o symlink) si el equipo usa ambas.

### Codex desde GitHub

Si usas el instalador de Codex:

```text
Instala la skill desde jaquinterob/agent-skills-filemaker path skills/filemaker-dev-workflow
```

## Actualizar

```bash
cd agent-skills-filemaker && git pull
# Si instalaste con symlink, ya está actualizado.
# Si usaste --copy, vuelve a correr: ./install.sh --copy
```

## Privacidad

Repo pensado para el equipo. No incluye secretos (`.env`, passwords Data API). Esos viven en cada máquina / `.env.local` del proyecto FileMaker.
