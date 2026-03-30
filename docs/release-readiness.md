# Skill 交付状态说明

## 读者

- 需要判断当前 skill 是否达到正式交付标准的项目负责人、研发和联调同学。

## 用途

- 说明当前已经完成什么、哪些验证已经通过、哪些仍受本机环境限制。

## 关联文档

- [README](../README.md)
- [安装指南](./install-guide.md)
- [使用指南](./usage-guide.md)
- [Windows Codex 验收记录](../acceptance/windows-codex.md)
- [Windows Claude Code 验收记录](../acceptance/windows-claude-code.md)
- [Windows OpenClaw 验收记录](../acceptance/windows-openclaw.md)

## 当前完成情况

已经完成：

- Skill 仓命名规范化为 `comfypet-jmcai-skill-pack`
- Skill 安装目录规范化为 `comfypet-jmcai-skill`
- 正式可安装 skill 子路径固定为 `skills/comfypet-jmcai-skill/`
- 轻量脚本式 payload、安装脚本、更新脚本已补齐
- 主应用 bridge 契约、agent metadata、typed outputs、视频输出链路已打通
- 主仓 `qa:workflow-smoke` 已覆盖：
  - bridge health
  - `registry --agent`
  - 图片 workflow
  - 视频 workflow
  - `history`

## 当前交付真相

当前已经达到：

- 代码交付可用
- 文档交付可用
- 标准 skill payload 调用链路可用
- 图片 / 视频 workflow 契约可用

当前尚未完全达到：

- Windows 上 OpenClaw、Codex、Claude Code 三端客户端级“实际发现 skill 并调用”的全部现场验收

## 已通过的验证

- 主仓：
  - `npm run typecheck`
  - `npm run build`
  - `npm run qa:workflow-smoke`
- Skill 仓：
  - `python -m py_compile ...`
  - 新 skill 子路径中的 `python scripts/jmcai_skill.py --version`

## 当前阻塞

阻塞不在代码层，而在本机客户端环境：

- Codex：
  - 本机 `codex.exe` 位于 WindowsApps 目录
  - 直接调用时返回 access denied
- Claude Code：
  - 本机未安装可直接调用的客户端命令
- OpenClaw：
  - 本机未安装可直接调用的客户端命令

这意味着：

- 可以证明 skill 包本身可用
- 也可以证明桥接与 workflow 调用链路可用
- 但还不能单凭这台机器，对外宣称“三端客户端级最终联调全部完成”

## 正式对外宣称“已完成”的条件

需要补齐以下最后验收：

1. Windows 上安装 Codex 客户端并完成 skill 发现
2. Windows 上安装 Claude Code 客户端并完成 skill 发现
3. Windows 上安装 OpenClaw 客户端并完成 skill 发现
4. 三端分别完成：
   - `doctor`
   - `registry --agent`
   - 一条图片 workflow
   - 一条视频 workflow
   - 返回本地输出路径

## 当前建议口径

如果现在要对外描述，建议使用：

- “JMCAI Comfypet Skill Pack 已完成代码交付、安装脚本、文档、图片/视频 workflow 调用链路和本地 smoke 验证。”
- “三端客户端级最终联调仍需在已安装对应客户端的 Windows 环境中完成最后验收。”

不建议直接说：

- “OpenClaw、Codex、Claude Code 三端真实安装联调已全部完成。”
