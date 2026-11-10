# Agent Skills — FileMaker

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-0A7EA4)](https://agentskills.io)
[![GitHub release](https://img.shields.io/github/v/release/jaquinterob/agent-skills-filemaker?include_prereleases)](https://github.com/jaquinterob/agent-skills-filemaker/releases)

Portable [Agent Skills](https://agentskills.io) for collaborating with an AI agent on **any** FileMaker project hosted on FileMaker Server.

Works with **Cursor**, **Claude Code**, **Codex**, and other hosts that load skill folders.

## Install (pick one)

```bash
# GitHub CLI (any agent that gh skill supports)
gh skill install jaquinterob/agent-skills-filemaker

# skills.sh / npx
npx skills add jaquinterob/agent-skills-filemaker

# Clone + symlink into Cursor / Claude / Codex
git clone https://github.com/jaquinterob/agent-skills-filemaker.git
cd agent-skills-filemaker
./install.sh                 # all three
# ./install.sh claude        # Claude Code only
# ./install.sh cursor
# ./install.sh --copy        # copy instead of symlink
```

Ask your agent: *install the skill from `jaquinterob/agent-skills-filemaker` path `skills/filemaker-dev-workflow`*.

## What you get

| Skill | Scope |
|-------|--------|
| [`filemaker-dev-workflow`](skills/filemaker-dev-workflow/) | Agent ↔ human roles, discovery checklist, HTML → `.fmp12`, XMSS paste queue, Web Viewer + `WEB_ASSETS`, Pro vs WebDirect — **product-agnostic**, with executable `scripts/` |

**Flow in one line:** edit in git → push HTML (Data API) → human reload Web Viewer → paste FM scripts as XMSS one-at-a-time → smoke Pro/WebDirect.

Bundled tools: `skill_root.py`, `fm_push_web_asset.py`, `copy_text_clipboard.py`, `copy_fm_clipboard.py` (XMSS, macOS).

## Layout

```
agent-skills-filemaker/
├── README.md
├── LICENSE
├── install.sh
└── skills/
    └── filemaker-dev-workflow/
        ├── SKILL.md          # core workflow (load first)
        ├── reference.md      # glossary, OS matrix, anti-patterns
        ├── examples.md       # end-to-end walkthroughs
        └── scripts/
            ├── skill_root.py
            ├── fm_push_web_asset.py
            ├── copy_text_clipboard.py
            └── copy_fm_clipboard.py   # macOS XMSS only
```

## Paths after install

| Tool | Personal path |
|------|----------------|
| Cursor | `~/.cursor/skills/filemaker-dev-workflow/` |
| Claude Code | `~/.claude/skills/filemaker-dev-workflow/` |
| Codex | `~/.codex/skills/filemaker-dev-workflow/` |

### Inside a product repo

```bash
mkdir -p .cursor/skills .claude/skills
cp -R skills/filemaker-dev-workflow .cursor/skills/
cp -R skills/filemaker-dev-workflow .claude/skills/
```

## Update

```bash
cd agent-skills-filemaker && git pull
# Symlink installs update automatically; --copy / gh skill: re-run install
gh skill update
```

## Secrets

Never commit `.env`, Data API passwords, or file-specific credentials. Those stay on each machine / product repo (gitignored).

## License

[MIT](LICENSE) — use and share freely. Keep secrets out of forks.
