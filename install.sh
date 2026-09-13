#!/usr/bin/env bash
# Instala skills de este repo en Cursor, Claude Code y/o Codex.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$ROOT/skills"
MODE="symlink" # symlink | copy
TARGETS=()

usage() {
  cat <<'EOF'
Uso: ./install.sh [--copy] [cursor|claude|codex|all]

  (sin args)     Instala en cursor + claude + codex (symlink)
  cursor         Solo ~/.cursor/skills
  claude         Solo ~/.claude/skills
  codex          Solo ~/.codex/skills
  all            Las tres (default)
  --copy         Copia archivos en vez de symlink (útil en Windows / sin git pull auto)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --help|-h) usage; exit 0 ;;
    cursor|claude|codex|all) TARGETS+=("$1"); shift ;;
    *) echo "Opción desconocida: $1" >&2; usage; exit 1 ;;
  esac
done

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  TARGETS=(all)
fi

resolve_dest() {
  case "$1" in
    cursor) echo "$HOME/.cursor/skills" ;;
    claude) echo "$HOME/.claude/skills" ;;
    codex)  echo "$HOME/.codex/skills" ;;
    *) return 1 ;;
  esac
}

expand_targets() {
  local t
  for t in "${TARGETS[@]}"; do
    if [[ "$t" == "all" ]]; then
      echo cursor
      echo claude
      echo codex
    else
      echo "$t"
    fi
  done | sort -u
}

install_one() {
  local tool="$1"
  local dest_root skill_name src dest
  dest_root="$(resolve_dest "$tool")"
  mkdir -p "$dest_root"

  for src in "$SKILLS_SRC"/*/; do
    [[ -d "$src" ]] || continue
    [[ -f "${src}SKILL.md" ]] || continue
    skill_name="$(basename "$src")"
    dest="$dest_root/$skill_name"

    if [[ -e "$dest" || -L "$dest" ]]; then
      rm -rf "$dest"
    fi

    if [[ "$MODE" == "symlink" ]]; then
      ln -s "$src" "$dest"
      echo "✓ $tool: symlink $dest → $src"
    else
      mkdir -p "$dest"
      cp -R "$src"/. "$dest"/
      echo "✓ $tool: copy → $dest"
    fi
  done
}

if [[ ! -d "$SKILLS_SRC" ]]; then
  echo "No existe $SKILLS_SRC" >&2
  exit 1
fi

while IFS= read -r tool; do
  install_one "$tool"
done < <(expand_targets)

echo
echo "Listo ($MODE). Reinicia o abre un chat nuevo para que el agente cargue las skills."
