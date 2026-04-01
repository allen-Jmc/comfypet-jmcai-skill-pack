# Claude Code 分发说明

## 读者

- 需要把 `JMCAI Comfypet` skill 分发给 Claude Code 用户或团队的维护者。

## 用途

- 说明 Claude Code 当前的正式分发路径、安装范围选择，以及团队共享的推荐做法。

## 关联文档

- [平台分发总览](./platform-distribution.md)
- [安装指南](./install-guide.md)

## 当前官方路径

Claude Code 当前采用官方支持的 skills 目录 / 项目级共享方式，不宣称存在公共技能商店。

推荐路径：

- 个人级：`~/.claude/skills/comfypet-jmcai-skill`
- 项目级：`<workspace>/.claude/skills/comfypet-jmcai-skill`
- 团队级：Git 仓共享或插件 bundle

## 推荐安装范围

### 个人级

- 适合个人长期使用
- 直接从 GitHub clone 或 ZIP 安装
- 正式目录：`~/.claude/skills/comfypet-jmcai-skill`

### 项目级

- 适合只在某个仓库里启用
- 建议把 `dist/comfypet-jmcai-skill/` 复制到：
  - `<workspace>/.claude/skills/comfypet-jmcai-skill`

### 团队级

- 优先采用 Git 仓共享
- 如果团队已经使用插件体系，再考虑打包为 Claude Code plugin bundle

## 分发建议

1. 先运行：

```powershell
pwsh -File .\release\build-distribution.ps1
```

2. 根据范围选择：

- 个人级：运行根仓安装脚本
- 项目级：复制 `dist/comfypet-jmcai-skill/`
- 团队级：直接引用 GitHub 仓或内网镜像仓

3. 在目标目录中验证：

```powershell
python jmcai_skill.py --version
python jmcai_skill.py doctor
```

## 团队共享推荐规则

- 个人习惯类安装用 `~/.claude/skills/`
- 与具体项目强绑定的能力用 `<workspace>/.claude/skills/`
- 公司内部统一分发优先用 Git 仓，而不是手工拷贝多个副本

## 对外口径

- “Claude Code 当前支持官方 skills 目录与项目级共享安装”
- “当前不宣称 Claude Code 存在公共技能市场”
