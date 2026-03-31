# Changelog

## Unreleased

- Added remote bridge auto-upload/download support and raised the minimum bridge requirement to `1.1.0`.
- Added the manifest-driven `jmcai-release-manager` workflow for dual-repo release preparation and publish.
- Added repo-local release manager wrappers so maintainers can trigger the same release flow from either repo.

## v1.0.0

- Formalized the standalone skill-pack naming as `comfypet-jmcai-skill-pack`.
- Formalized the installable skill payload path as `skills/comfypet-jmcai-skill/`.
- Added the official skill payload structure with `SKILL.md`, `agents/openai.yaml`, `scripts/`, `references/`, and `assets/`.
- Consolidated the CLI around `python scripts/jmcai_skill.py`.
- Standardized install paths for Codex, Claude Code, and OpenClaw.
- Added migration handling from the legacy `jmcai-workflow-skill` directory name.
- Added root-level install and update scripts that sync only the skill payload and preserve `config.json`.
- Published install, update, troubleshooting, and release-readiness documentation.
