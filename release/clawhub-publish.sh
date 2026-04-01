#!/usr/bin/env bash
set -euo pipefail

version="${1:-1.2.0}"
repo_root="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
changelog="${3:-Release 1.2.0}"
run_dry_run="${RUN_DRY_RUN:-0}"

if [[ ! "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must be semver without a leading v. Current value: ${version}" >&2
  exit 1
fi

if ! command -v clawhub >/dev/null 2>&1; then
  echo "clawhub CLI is not installed. Install it first with 'npm i -g clawhub' or 'pnpm add -g clawhub'." >&2
  exit 1
fi

slug="comfypet-jmcai-skill"
display_name="JMCAI Comfypet"
tags="latest,comfyui,image,video,jmcai"
payload_root="${repo_root}/skills/${slug}"
skills_root="${repo_root}/skills"

if [[ ! -d "${payload_root}" ]]; then
  echo "Skill payload not found: ${payload_root}" >&2
  exit 1
fi

echo "ClawHub publish template ready."
echo "Slug: ${slug}"
echo "Name: ${display_name}"
echo "Version: ${version}"
echo "Tags: ${tags}"
echo
echo "Dry-run preview:"
echo "clawhub sync --root \"${skills_root}\" --dry-run --tags \"${tags}\" --changelog \"${changelog}\""
echo
echo "Publish single skill:"
echo "clawhub publish \"${payload_root}\" --slug \"${slug}\" --name \"${display_name}\" --version \"${version}\" --tags \"${tags}\" --changelog \"${changelog}\""
echo
echo "Sync all local skills:"
echo "clawhub sync --root \"${skills_root}\" --all --tags \"${tags}\" --changelog \"${changelog}\" --bump patch"

if [[ "${run_dry_run}" == "1" ]]; then
  echo
  echo "Running clawhub dry-run..."
  clawhub sync --root "${skills_root}" --dry-run --tags "${tags}" --changelog "${changelog}"
fi
