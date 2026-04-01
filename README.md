# JMCAI Comfypet Skill Pack

- 仓库名：`comfypet-jmcai-skill-pack`
- 正式 skill 名：`comfypet-jmcai-skill`
- 正式可安装 skill 子路径：`skills/comfypet-jmcai-skill/`
- GitHub 仓库：`https://github.com/allen-Jmc/comfypet-jmcai-skill-pack`

JMCAI Comfypet Skill Pack 是给 OpenClaw、Codex、Claude Code 共用的独立 skill 仓。仓库根目录负责提供人类文档、安装脚本和验收记录；真正给 agent 安装的只有 `skills/comfypet-jmcai-skill/` 这个标准 skill payload。

## 文档导航

- [安装指南](./docs/install-guide.md)
- [使用指南](./docs/usage-guide.md)
- [平台分发总览](./docs/platform-distribution.md)
- [OpenAI / Codex 分发](./docs/openai-codex-distribution.md)
- [Claude Code 分发](./docs/claude-code-distribution.md)
- [OpenClaw / ClawHub 分发](./docs/openclaw-clawhub-distribution.md)
- [交付状态说明](./docs/release-readiness.md)
- [Windows Codex 验收记录](./acceptance/windows-codex.md)
- [Windows Claude Code 验收记录](./acceptance/windows-claude-code.md)
- [Windows OpenClaw 验收记录](./acceptance/windows-openclaw.md)

## 功能范围

- 查询当前可供 agent 调用的 workflows
- 读取安全 alias schema 与 agent metadata
- 提交运行任务并轮询状态
- 读取历史记录
- 执行本地自检，确认 bridge、版本与默认 target 状态

## 仓库结构

```text
CHANGELOG.md
README.md
acceptance/
docs/
install/
skills/
  comfypet-jmcai-skill/
    SKILL.md
    __init__.py
    jmcai_skill.py
    agents/openai.yaml
    references/
    assets/
    config.example.json
```

## GitHub 安装

### Codex

优先安装 GitHub 仓库中的 skill 子路径：

```text
https://github.com/allen-Jmc/comfypet-jmcai-skill-pack/tree/main/skills/comfypet-jmcai-skill
```

注意：安装目标是 `skills/comfypet-jmcai-skill/`，不是整个仓库根目录。

### Claude Code / OpenClaw

当前以 clone 或下载 ZIP 后执行安装脚本为主。

## 平台分发与发布产物

- OpenAI / Codex：GitHub 分发 + ChatGPT Skills 页面上传 / 工作区分享
- Claude Code：GitHub 分发 + 官方 skills 目录安装 / 项目级共享
- OpenClaw：GitHub 分发 + ClawHub 已发布

发布者若要生成正式分发产物，请在仓库根目录执行：

### Windows

```powershell
pwsh -File .\release\build-distribution.ps1
```

### macOS / Linux

```bash
./release/build-distribution.sh
```

产物会生成到 `dist/`：

- `dist/comfypet-jmcai-skill/`
- `dist/comfypet-jmcai-skill-v1.2.0.zip`
- `dist/checksums.txt`

平台级分发细节见：

- [平台分发总览](./docs/platform-distribution.md)
- [OpenAI / Codex 分发](./docs/openai-codex-distribution.md)
- [Claude Code 分发](./docs/claude-code-distribution.md)
- [OpenClaw / ClawHub 分发](./docs/openclaw-clawhub-distribution.md)

当前 OpenClaw 侧已经完成首发注册表发布：`comfypet-jmcai-skill@1.2.0`。
若 ClawHub 刚发布后短时间内还不可见，通常是平台安全扫描尚未完成，可稍后重试 `clawhub install comfypet-jmcai-skill` 或 `clawhub inspect comfypet-jmcai-skill`。

## Clone / ZIP 安装

### Windows

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

安装脚本会：

- 同步 `skills/comfypet-jmcai-skill/` 到目标技能目录
- 迁移旧目录 `jmcai-workflow-skill` 到新目录 `comfypet-jmcai-skill`
- 保留已有 `config.json`
- 自动执行 `doctor`

## CLI

正式 CLI 入口统一为：

```bash
python jmcai_skill.py --version
python jmcai_skill.py doctor
python jmcai_skill.py registry --agent
python jmcai_skill.py run --workflow demo-workflow --args '{"prompt_1":"a studio cat"}'
python jmcai_skill.py status --run-id <run_id>
python jmcai_skill.py history --workflow demo-workflow --limit 5
```

CLI 输出始终为机器可读 JSON，字段统一为 `snake_case`。

## 默认安装目录

- Codex: `~/.codex/skills/comfypet-jmcai-skill`
- Claude Code: `~/.claude/skills/comfypet-jmcai-skill`
- OpenClaw: `~/.openclaw/workspace/skills/comfypet-jmcai-skill`

## 更新

### Windows

```powershell
pwsh -File .\install\update.ps1 -Agent codex
```

### macOS / Linux

```bash
./install/update.sh codex
```

更新脚本会尝试 `git pull --ff-only`，然后重新同步 skill 子目录并执行 `doctor`。

## 排错

- `doctor` 失败：先确认桌面端已启动，并检查 Workflow Bridge 是否可达
- `python jmcai_skill.py` 不可用：确认是在 skill 安装目录内执行，且使用 Python 3
- 看不到 workflow：确认 workflow 已启用，且默认 target 当前可用
- 图片/视频任务失败：优先看 `status` 或 `history` 返回的 `error_message`
