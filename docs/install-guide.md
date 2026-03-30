# Skill 安装指南

## 读者

- 需要把 `JMCAI Comfypet Skill Pack` 安装到 OpenClaw、Codex 或 Claude Code 的使用者。

## 用途

- 说明 skill 应该安装到哪里、如何安装、如何验证安装结果，以及安装失败时优先排查什么。

## 关联文档

- [README](../README.md)
- [使用指南](./usage-guide.md)
- [平台分发总览](./platform-distribution.md)
- [交付状态说明](./release-readiness.md)

## 安装前检查

- JMCAI Comfypet 桌面应用已安装并已启动
- Workflow Center 中至少已经启用了一个 workflow
- 目标 workflow 已配置默认 target，或你准备在运行时显式传入 `target`
- 本机可用 Python 3.10 及以上版本

## 正式命名

- Skill 仓库名：`comfypet-jmcai-skill-pack`
- Skill 名：`comfypet-jmcai-skill`
- 正式可安装子路径：`skills/comfypet-jmcai-skill/`
- GitHub 仓库：`https://github.com/allen-Jmc/comfypet-jmcai-skill-pack`

## 默认安装目录

- Codex：`~/.codex/skills/comfypet-jmcai-skill`
- Claude Code：`~/.claude/skills/comfypet-jmcai-skill`
- OpenClaw：`~/.openclaw/workspace/skills/comfypet-jmcai-skill`

## GitHub 安装

### Codex

优先使用 GitHub 仓库子路径安装：

```text
https://github.com/allen-Jmc/comfypet-jmcai-skill-pack/tree/main/skills/comfypet-jmcai-skill
```

注意：不要把整个仓库根目录当作 skill 安装目标。

### Claude Code / OpenClaw

当前仍以 clone 或下载 ZIP 后执行安装脚本为主。

## Clone / ZIP 安装

### Windows

在仓库根目录执行：

```powershell
pwsh -File .\install\install.ps1 -Agent codex
pwsh -File .\install\install.ps1 -Agent claude
pwsh -File .\install\install.ps1 -Agent openclaw
```

### macOS / Linux

```bash
./install/install.sh codex
./install/install.sh claude
./install/install.sh openclaw
```

## 安装脚本会做什么

- 将 `skills/comfypet-jmcai-skill/` 同步到目标技能目录
- 检查旧目录 `jmcai-workflow-skill`，并在适合时迁移到新目录 `comfypet-jmcai-skill`
- 保留已有的 `config.json`
- 自动执行一次 `doctor`
- 如果桌面端暂未启动，安装仍会完成，但会输出需要稍后重跑 `doctor` 的提醒

## 安装完成后应看到的目录

```text
comfypet-jmcai-skill/
  agents/
  assets/
  references/
  scripts/
  config.example.json
  config.json
  SKILL.md
```

## 安装后验证

### 1. 验证 CLI

```powershell
python scripts/jmcai_skill.py --version
```

期望返回：

```text
jmcai-skill 1.0.0
```

### 2. 验证 bridge

```powershell
python scripts/jmcai_skill.py doctor
```

如果桌面端正在运行且 bridge 已暴露 workflow，`doctor` 应返回 `status: "success"`。

### 3. 验证可见 workflows

```powershell
python scripts/jmcai_skill.py registry --agent
```

若结果中 `workflow_count > 0`，说明当前 skill 已能看到桌面端公开的 workflow。

## 配置文件

默认配置文件为 `config.json`。若不存在，会从 `config.example.json` 复制生成。

当前固定配置项：

- `bridge_url`
- `request_timeout_ms`
- `min_bridge_version`

默认 bridge 地址为：

```text
http://127.0.0.1:32100
```

## 旧目录迁移规则

- 旧目录名 `jmcai-workflow-skill` 只作为迁移源保留
- 正式目标目录始终是 `comfypet-jmcai-skill`
- 如果旧目录存在且新目录不存在，安装脚本会优先迁移
- 如果旧目录和新目录同时存在，安装脚本不会静默覆盖旧目录

## 常见安装问题

### `doctor` 提示 bridge 不可达

优先检查：

- JMCAI Comfypet 桌面应用是否已启动
- Workflow Bridge 是否正在监听 `127.0.0.1:32100`
- 是否至少有一个已启用 workflow 被公开

### `python scripts/jmcai_skill.py --version` 失败

优先检查：

- 目标目录下是否存在 `scripts/jmcai_skill.py`
- 是否使用 Python 3 运行
- 是否误把整个仓库根目录当作 skill 安装目标

### 安装后看不到 workflows

优先检查：

- workflow 是否在 Workflow Center 中启用
- workflow 是否配置了默认 target
- 默认 target 当前是否可用
