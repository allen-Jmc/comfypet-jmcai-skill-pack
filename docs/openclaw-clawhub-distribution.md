# OpenClaw / ClawHub 分发说明

## 读者

- 需要把 `JMCAI Comfypet` skill 分发到 OpenClaw，并准备 ClawHub 发布的维护者。

## 用途

- 说明 GitHub 安装与 ClawHub 安装两条路径，并把 ClawHub 发布所需参数和命令固定下来。

## 关联文档

- [平台分发总览](./platform-distribution.md)
- [安装指南](./install-guide.md)

## 两条正式路径

### 1. GitHub / 本地安装

- 用户从 GitHub 下载 skill
- 安装到：
  - `~/.openclaw/workspace/skills/comfypet-jmcai-skill`
- 或复制到当前 workspace 的 `skills/` 目录

### 2. ClawHub 注册表安装

发布完成后，用户可通过：

```bash
clawhub install comfypet-jmcai-skill
```

或：

```bash
openclaw skills install comfypet-jmcai-skill
```

进行安装。

## 当前发布状态

- ClawHub 首发版本：`comfypet-jmcai-skill@1.1.0`
- 发布结果：已完成首发 publish
- 若 `clawhub inspect comfypet-jmcai-skill` 短时间返回“hidden while security scan is pending”，表示平台安全扫描尚未结束，等待几分钟后重试即可。

## 固定发布参数

- `slug`: `comfypet-jmcai-skill`
- `name`: `JMCAI Comfypet`
- `version`: `1.2.0`
- `tags`: `latest,comfyui,image,video,jmcai`
- `changelog`: `Release 1.2.0`

## 推荐发布命令

### Dry-run 预览

```powershell
pwsh -File .\release\clawhub-publish.ps1 -RunDryRun
```

### 发布单个 skill

```bash
clawhub publish ./skills/comfypet-jmcai-skill --slug comfypet-jmcai-skill --name "JMCAI Comfypet" --version 1.2.0 --tags latest,comfyui,image,video,jmcai --changelog "Release 1.2.0"
```

### 扫描并同步 skills 目录

```bash
clawhub sync --root ./skills --all --tags latest,comfyui,image,video,jmcai --changelog "Release 1.2.0" --bump patch
```

## 当前仓库已就绪的内容

- `SKILL.md` 已包含 `metadata.openclaw`
- GitHub 仓已公开
- 分发脚本已准备好 dry-run 与命令模板
- ClawHub 首发版本已发布

## 当前仍依赖外部环境的步骤

- 后续版本发布仍需要：
  - 安装 `clawhub` CLI
  - `clawhub login`
  - 实际执行 publish 或 sync

## 验证建议

1. 在本地先跑：

```powershell
pwsh -File .\release\clawhub-publish.ps1 -RunDryRun
```

2. 确认生成的命令与参数正确
3. 登录 ClawHub 后再执行正式 publish
4. 发布后在 OpenClaw 中验证：

```bash
clawhub install comfypet-jmcai-skill
```

## 对外口径

- “当前 OpenClaw 路线支持 GitHub 安装，且 `comfypet-jmcai-skill@1.1.0` 已发布到 ClawHub。”
- “如果刚发布后短时间内尚不可见，通常是平台安全扫描未完成，可稍后再次安装或 inspect。”
