---
name: jmcai-release-manager
description: |
  在 comfypet-jmcai-skill-pack 当前仓中调用全局 jmcai-release-manager，准备、正式发布或回顾 JMCAI 双仓版本更新。适用于“准备 1.1.0 双仓发布”“正式发布 1.1.0”“回顾 1.1.0 发布状态”等维护者请求。
---

# JMCAI Release Manager Wrapper

当前仓角色：`skill-pack`

先读取：

- `release/release-manifest.json`
- 全局 skill：`C:\Users\cdall\.codex\skills\jmcai-release-manager\SKILL.md`

然后直接调用全局脚本：

```bash
python C:\Users\cdall\.codex\skills\jmcai-release-manager\scripts\jmcai_release_manager.py doctor
python C:\Users\cdall\.codex\skills\jmcai-release-manager\scripts\jmcai_release_manager.py prepare --version <semver>
python C:\Users\cdall\.codex\skills\jmcai-release-manager\scripts\jmcai_release_manager.py publish --version <semver>
python C:\Users\cdall\.codex\skills\jmcai-release-manager\scripts\jmcai_release_manager.py review --version <semver>
```
