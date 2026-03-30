# OpenAI / Codex 分发说明

## 读者

- 需要把 `JMCAI Comfypet` 分发到 OpenAI / Codex 使用环境的维护者。

## 用途

- 说明 OpenAI / Codex 当前的正式分发路径、需要准备什么 payload，以及应该如何验证安装前准备。

## 关联文档

- [平台分发总览](./platform-distribution.md)
- [安装指南](./install-guide.md)

## 当前官方路径

- GitHub 下载 skill payload
- 在 ChatGPT / OpenAI Skills 页面中选择 `Upload from your computer`
- 若工作区允许，再进行分享或代他人安装

当前不采用“公开技能商店”口径。

## 推荐上传产物

优先使用：

- `dist/comfypet-jmcai-skill/`

如果平台只接受压缩包，先解压：

- `dist/comfypet-jmcai-skill-v1.0.0.zip`

上传时要确保根目录直接包含：

- `SKILL.md`
- `agents/openai.yaml`
- `scripts/`
- `references/`
- `assets/`
- `config.example.json`

## 上传前准备

1. 先在仓库根目录生成分发产物：

```powershell
pwsh -File .\release\build-distribution.ps1
```

2. 确认以下内容都存在：

- `agents/openai.yaml`
- `SKILL.md`
- `scripts/jmcai_skill.py`

3. 确认 `agents/openai.yaml` 的品牌信息符合当前版本：

- `display_name`: `JMCAI Comfypet`
- `short_description`: `调用已配置的 ComfyUI 图片/视频工作流`
- `default_prompt` 已指向 `$comfypet-jmcai-skill`

## 工作区发布前提

- 需要能够访问 Skills 页面
- 若要分享给工作区成员，需要管理员允许 skill 分享或安装
- 若要代他人安装，需要工作区权限支持

## 建议上传后的验证

1. 在工作区内确认 skill 名与图标展示正常
2. 让 Codex / ChatGPT 读取 skill，并确认默认提示词与描述可见
3. 从已配置 workflow 的桌面端环境中跑：

```powershell
python scripts/jmcai_skill.py doctor
python scripts/jmcai_skill.py registry --agent
```

4. 再验证一条图片 workflow 和一条视频 workflow

## 对外口径

- “当前 OpenAI / Codex 路线支持 GitHub 分发与 Skills 页面上传 / 工作区分享”
- “当前不宣称存在面向所有用户的公共技能市场下载入口”
