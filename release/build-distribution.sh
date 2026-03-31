#!/usr/bin/env bash
set -euo pipefail

version="${1:-1.1.0}"
repo_root="${2:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
skill_name="comfypet-jmcai-skill"
payload_root="${repo_root}/skills/${skill_name}"
dist_root="${repo_root}/dist"
dist_payload_root="${dist_root}/${skill_name}"
zip_path="${dist_root}/${skill_name}-v${version}.zip"
checksums_path="${dist_root}/checksums.txt"

if [[ ! "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must be semver without a leading v. Current value: ${version}" >&2
  exit 1
fi

for required_path in \
  "${payload_root}/SKILL.md" \
  "${payload_root}/agents/openai.yaml" \
  "${payload_root}/scripts/jmcai_skill.py" \
  "${payload_root}/references" \
  "${payload_root}/assets" \
  "${payload_root}/config.example.json"; do
  if [[ ! -e "${required_path}" ]]; then
    echo "Missing required payload path: ${required_path}" >&2
    exit 1
  fi
done

if ! command -v zip >/dev/null 2>&1; then
  echo "zip is required to build distribution artifacts." >&2
  exit 1
fi

rm -rf "${dist_root}"
mkdir -p "${dist_root}"
cp -R "${payload_root}" "${dist_root}/"

find "${dist_payload_root}" -type d -name '__pycache__' -prune -exec rm -rf {} +
find "${dist_payload_root}" -type f \( -name '*.pyc' -o -name 'config.json' \) -delete

(
  cd "${dist_payload_root}"
  zip -qr "${zip_path}" .
)

if command -v zipinfo >/dev/null 2>&1; then
  if ! zipinfo -1 "${zip_path}" | grep -qx 'SKILL.md'; then
    echo "Zip archive root does not contain SKILL.md" >&2
    exit 1
  fi
fi

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "${zip_path}" | awk '{print $1 " *" substr($0, index($0,$2))}' > "${checksums_path}"
elif command -v shasum >/dev/null 2>&1; then
  checksum="$(shasum -a 256 "${zip_path}" | awk '{print $1}')"
  echo "${checksum} *$(basename "${zip_path}")" > "${checksums_path}"
else
  echo "sha256sum or shasum is required to compute checksums." >&2
  exit 1
fi

echo "Distribution build complete."
echo "Payload directory: ${dist_payload_root}"
echo "Zip package: ${zip_path}"
echo "Checksums file: ${checksums_path}"
