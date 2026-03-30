# Changelog

## Unreleased

- Added platform distribution metadata in `SKILL.md` for OpenClaw / ClawHub compatibility.
- Added `release/` scripts to build `dist/` payload artifacts and prepare ClawHub publish commands.
- Added platform distribution docs for OpenAI/Codex, Claude Code, and OpenClaw / ClawHub.

## v1.0.0

- Formalized the standalone skill-pack naming as `comfypet-jmcai-skill-pack`.
- Formalized the installable skill payload path as `skills/comfypet-jmcai-skill/`.
- Added the official skill payload structure with `SKILL.md`, `agents/openai.yaml`, `scripts/`, `references/`, and `assets/`.
- Consolidated the CLI around `python scripts/jmcai_skill.py`.
- Standardized install paths for Codex, Claude Code, and OpenClaw.
- Added migration handling from the legacy `jmcai-workflow-skill` directory name.
- Added root-level install and update scripts that sync only the skill payload and preserve `config.json`.
- Published install, update, troubleshooting, and release-readiness documentation.
