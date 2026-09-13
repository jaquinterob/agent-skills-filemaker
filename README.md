# Agent Skills — FileMaker (generic)

Portable [Agent Skills](https://agentskills.io) (`SKILL.md`) for collaborating with an AI agent on **any** FileMaker project hosted on FileMaker Server.

Works with **Cursor**, **Claude Code**, **Codex**, and other tools that load skill folders.

## Skills

| Skill | Scope |
|-------|--------|
| [`filemaker-dev-workflow`](skills/filemaker-dev-workflow/) | Agent ↔ human roles, deliver HTML into the `.fmp12`, XMSS script paste (one at a time), Pro vs WebDirect — **product-agnostic**, with executable `scripts/` |

Includes runnable tools: `fm_push_web_asset.py`, `copy_fm_clipboard.py`, `copy_text_clipboard.py`. No product names or business rules — each app keeps those in its own repo.

## Distribute

1. This repo = team source of truth.
2. Each person clones + installs (or the agent installs for them).
3. Optional: copy into a product repo under `.cursor/skills/` and `.claude/skills/` if the skill should travel with that project only.

```
agent-skills-filemaker/
├── README.md
├── install.sh
└── skills/
    └── filemaker-dev-workflow/
        ├── SKILL.md
        └── reference.md
```

## Install

```bash
git clone https://github.com/jaquinterob/agent-skills-filemaker.git
cd agent-skills-filemaker
./install.sh          # Cursor + Claude + Codex (symlink)
# ./install.sh --copy # copy instead of symlink
# ./install.sh cursor # Cursor only
```

| Tool | Personal path |
|------|----------------|
| Cursor | `~/.cursor/skills/<skill>/` |
| Claude Code | `~/.claude/skills/<skill>/` |
| Codex | `~/.codex/skills/<skill>/` |

### Inside a product repo

```bash
mkdir -p .cursor/skills .claude/skills
cp -R skills/filemaker-dev-workflow .cursor/skills/
cp -R skills/filemaker-dev-workflow .claude/skills/
```

### Codex from GitHub

```text
Install the skill from jaquinterob/agent-skills-filemaker path skills/filemaker-dev-workflow
```

## Update

```bash
cd agent-skills-filemaker && git pull
# Symlink installs update automatically; --copy needs ./install.sh --copy again
```

## Secrets

This repo must stay free of `.env`, Data API passwords, and file-specific credentials. Those belong on each machine / product repo (gitignored).
