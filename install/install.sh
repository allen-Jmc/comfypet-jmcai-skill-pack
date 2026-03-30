#!/usr/bin/env bash
set -euo pipefail

agent="${1:-}"
repo_root="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
skill_name="comfypet-jmcai-skill"
legacy_skill_name="jmcai-workflow-skill"
payload_root="${repo_root}/skills/${skill_name}"

if [[ -z "${agent}" ]]; then
  echo "Usage: ./install/install.sh <codex|claude|openclaw> [repo_root]" >&2
  exit 1
fi

if [[ ! -d "${payload_root}" ]]; then
  echo "Skill payload not found: ${payload_root}" >&2
  exit 1
fi

case "${agent}" in
  codex)
    target_dir="${HOME}/.codex/skills/${skill_name}"
    ;;
  claude)
    target_dir="${HOME}/.claude/skills/${skill_name}"
    ;;
  openclaw)
    target_dir="${HOME}/.openclaw/workspace/skills/${skill_name}"
    ;;
  *)
    echo "Unsupported agent: ${agent}" >&2
    exit 1
    ;;
esac

target_parent="$(dirname "${target_dir}")"
legacy_dir="${target_parent}/${legacy_skill_name}"
mkdir -p "${target_parent}"

if [[ -d "${legacy_dir}" && ! -e "${target_dir}" ]]; then
  mv "${legacy_dir}" "${target_dir}"
  echo "Migrated legacy skill directory to ${target_dir}"
fi

temp_config=""
if [[ -f "${target_dir}/config.json" ]]; then
  temp_config="$(mktemp)"
  cp "${target_dir}/config.json" "${temp_config}"
fi

mkdir -p "${target_dir}"
find "${target_dir}" -mindepth 1 -maxdepth 1 ! -name 'config.json' -exec rm -rf {} +
cp -R "${payload_root}/." "${target_dir}/"

if [[ -n "${temp_config}" ]]; then
  cp "${temp_config}" "${target_dir}/config.json"
  rm -f "${temp_config}"
elif [[ ! -f "${target_dir}/config.json" && -f "${target_dir}/config.example.json" ]]; then
  cp "${target_dir}/config.example.json" "${target_dir}/config.json"
fi

python_bin="$(command -v python3 || command -v python || true)"
if [[ -z "${python_bin}" ]]; then
  echo "Python 3 is required but was not found in PATH." >&2
  exit 1
fi

if ! (
  cd "${target_dir}"
  "${python_bin}" scripts/jmcai_skill.py --config config.json doctor
); then
  echo "Warning: skill payload installed, but doctor reported issues. Open JMCAI desktop app and rerun 'python scripts/jmcai_skill.py doctor' in ${target_dir}." >&2
fi

echo "Installed ${skill_name} to ${target_dir}"
