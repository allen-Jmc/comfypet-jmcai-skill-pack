#!/usr/bin/env bash
set -euo pipefail

agent="${1:-}"
repo_root="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

if [[ -z "${agent}" ]]; then
  echo "Usage: ./install/update.sh <codex|claude|openclaw> [repo_root]" >&2
  exit 1
fi

if command -v git >/dev/null 2>&1; then
  (
    cd "${repo_root}"
    git pull --ff-only
  )
else
  echo "git was not found in PATH; skipping git pull and continuing with local files." >&2
fi

"${repo_root}/install/install.sh" "${agent}" "${repo_root}"
