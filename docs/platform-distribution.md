# 平台分发总览

## 读者

- 需要把 `comfypet-jmcai-skill-pack` 分发到 OpenAI / Codex、Claude Code、OpenClaw 的维护者与发布者。

## 用途

- 统一说明三端的“官方渠道”是什么、当前仓库支持到哪一层、以及应该从哪个产物开始分发。

## 关联文档

- [README](../README.md)
- [OpenAI / Codex 分发](./openai-codex-distribution.md)
- [Claude Code 分发](./claude-code-distribution.md)
- [OpenClaw / ClawHub 分发](./openclaw-clawhub-distribution.md)

## 当前正式 payload

- 唯一正式 skill payload：`skills/comfypet-jmcai-skill/`
- 当前仓库不再维护第二套平台专用 payload
- 平台差异通过：
  - `SKILL.md` frontmatter
  - `agents/openai.yaml`
  - 发布脚本
  - 平台专项文档

## 三端官方渠道定义

### OpenAI / Codex

- 当前没有面向所有用户的公共技能商店口径。
- 这边采用的官方分发路径是：
  - GitHub 下载 skill payload
  - ChatGPT Skills 页面 `Upload from your computer`
  - 工作区内分享 / 安装

### Claude Code

- 当前没有公共技能市场口径。
- 这边采用的官方分发路径是：
  - GitHub 下载 payload
  - 安装到 `~/.claude/skills/comfypet-jmcai-skill`
  - 或放到项目内 `.claude/skills/`

### OpenClaw

- 当前支持两条正式路径：
  - GitHub 下载后本地安装
  - ClawHub 注册表发布与安装
- `comfypet-jmcai-skill@1.0.0` 已在 ClawHub 首发发布。
- 如果刚发布后短时间不可见，通常是 ClawHub 安全扫描仍在进行中。

## 推荐分发产物

发布时优先使用 `dist/` 目录里的构建产物，而不是让用户自己从仓库根目录手工抽 payload。

标准产物：

- `dist/comfypet-jmcai-skill/`
- `dist/comfypet-jmcai-skill-v1.0.0.zip`
- `dist/checksums.txt`

## 发布者工作流

1. 在仓库根目录运行：
   - Windows：`pwsh -File .\release\build-distribution.ps1`
   - macOS / Linux：`./release/build-distribution.sh`
2. 校验 `dist/` 是否包含 payload 副本、zip 和 SHA256。
3. 再按目标平台文档执行：
   - OpenAI / Codex：上传 payload 到 Skills 页面
   - Claude Code：个人级、项目级或团队 Git 分发
   - OpenClaw：必要时执行 ClawHub dry-run / 后续版本 publish

## 当前仓库已具备

- OpenAI / Codex 所需 `agents/openai.yaml`
- OpenClaw / ClawHub 所需 `metadata.openclaw`
- 通用 ZIP / payload 分发脚本
- 三端专项文档

## 当前仓库未直接代做

- 不自动帮你上传 OpenAI Skills 页面
- 不自动替你登录 Claude Code
- 不自动替你把 skill 发布到 ClawHub

这些动作仍依赖对应平台账号或本机客户端环境；其中 OpenClaw 的首发 ClawHub 发布已经完成，其余平台动作仍按各自环境执行。
