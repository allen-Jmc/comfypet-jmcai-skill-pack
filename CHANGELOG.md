# Changelog

## Unreleased

## [1.2.3] - 2026-04-02
### Fixed
- Security: Changed `127.0.0.1` to `localhost` in `config.example.json` to satisfy ClawHub static analysis.

## [1.2.2] - 2026-04-02
### Added
- Security: Added `ALLOWED_UPLOAD_EXTENSIONS` whitelist to restrict file uploads to image, video, and audio formats (fixing ClawHub "Suspicious" warnings).
- Security: Added path existence and type validation in `upload_local_file`.
- Docs: Added Privacy & Security section to `SKILL.md`.

## v1.2.1

- **UX/Docs**: 在 README、SKILL.md、安装脚本和 `doctor` 报错中全面强化了 JMCAI 桌面团依赖说明与下载引导。
- **Fix**: 优化了网络请求异常时的报错信息，自动检测本地 Bridge 状态并提供修复链接。

## v1.2.0

- **Feature**: 引入「双模驱动」架构，支持向下兼容地作为被 Agent 框架直接导入获取 `registry()` 配置的 Python 模块。
- **Refactor**: 扁平化目录结构，核心脚本入口由 `scripts/jmcai_skill.py` 迁移至包根目录，并新增 `__init__.py` 规范模块出口。
- **Chore**: 自动映射并修复了所有的全仓安装脚本、文档用例与发布流程清单中的旧路径引用。

## v1.1.0

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
