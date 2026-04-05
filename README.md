# JMCAI Comfypet Skill Pack

- 仓库名：`comfypet-jmcai-skill-pack`
- 正式 skill 名：`comfypet-jmcai-skill`
- 正式可安装 skill 子路径：`skills/comfypet-jmcai-skill/`
- GitHub 仓库：[allen-Jmc/comfypet-jmcai-skill-pack](https://github.com/allen-Jmc/comfypet-jmcai-skill-pack)

JMCAI Comfypet Skill Pack 是给 OpenClaw、Codex、Claude Code 共用的独立 skill 仓。公开仓只保留用户安装和使用 skill 所需的最小内容；真正给 agent 安装的 payload 是 `skills/comfypet-jmcai-skill/`。

> [!IMPORTANT]
> 本 Skill 必须配合 **JMCAI Comfypet 桌面客户端** 运行。
> 请先启动桌面端并开启 Workflow Bridge。
>
> - 桌面端下载：[allen-Jmc/comfypet-jmcai-Dist](https://github.com/allen-Jmc/comfypet-jmcai-Dist)
> - 项目主页：[allen-Jmc/Comfypet-JMCAI](https://github.com/allen-Jmc/Comfypet-JMCAI)

## 文档入口

- [安装指南](./docs/install-guide.md)
- [使用指南](./docs/usage-guide.md)
- [GitHub Releases](https://github.com/allen-Jmc/comfypet-jmcai-skill-pack/releases)

## 功能范围

- 查询当前可供 agent 调用的 workflows
- 读取安全 alias schema 与 agent metadata
- 在远程 bridge 场景下自动上传本机资产输入，并改写成 `upload:<id>`
- 提交运行任务并轮询状态
- 读取历史记录
- 执行本地自检，确认 bridge、版本与默认 target 状态

## 仓库结构

```text
CHANGELOG.md
README.md
docs/
  install-guide.md
  usage-guide.md
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

## 安装方式

### Codex

优先安装 GitHub 仓库中的 skill 子路径：

```text
https://github.com/allen-Jmc/comfypet-jmcai-skill-pack/tree/main/skills/comfypet-jmcai-skill
```

注意：安装目标是 `skills/comfypet-jmcai-skill/`，不是整个仓库根目录。

### Clone / ZIP 安装

Windows：

```powershell
pwsh -File .\install\install.ps1 -Agent codex
pwsh -File .\install\install.ps1 -Agent claude
pwsh -File .\install\install.ps1 -Agent openclaw
```

macOS / Linux：

```bash
./install/install.sh codex
./install/install.sh claude
./install/install.sh openclaw
```

安装脚本会保留已有 `config.json`，同时自动补齐缺失配置，并把过低或非法的 `min_bridge_version` 提升到当前硬性最低值 `1.2.0`。

### OpenClaw / ClawHub

如果你已经安装 `clawhub`，可以直接：

```bash
clawhub install comfypet-jmcai-skill
```

## 发布产物下载

预构建产物统一放在 [GitHub Releases](https://github.com/allen-Jmc/comfypet-jmcai-skill-pack/releases)。

标准资产名称：

- `comfypet-jmcai-skill-v1.2.5.zip`
- `checksums.txt`

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

- Codex：`~/.codex/skills/comfypet-jmcai-skill`
- Claude Code：`~/.claude/skills/comfypet-jmcai-skill`
- OpenClaw：`~/.openclaw/workspace/skills/comfypet-jmcai-skill`

## 更新

Windows：

```powershell
pwsh -File .\install\update.ps1 -Agent codex
```

macOS / Linux：

```bash
./install/update.sh codex
```

更新脚本会尝试 `git pull --ff-only`，然后重新同步 skill 子目录并执行 `doctor`。
如果旧配置里仍保留 `min_bridge_version: 1.1.0` 之类的历史值，更新时也会自动迁移到 `1.2.0`。

## 排错

- `doctor` 失败：先确认桌面端已启动，并检查 Workflow Bridge 是否可达
- `python jmcai_skill.py` 不可用：确认是在 skill 安装目录内执行，且使用 Python 3
- 看不到 workflow：确认 workflow 已启用，且默认 target 当前可用
- 图片、视频或资产输入任务失败：优先看 `status` 或 `history` 返回的 `error_message`
