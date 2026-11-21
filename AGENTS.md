# comfypet-jmcai-skill-pack 项目规则

## 项目边界

- 本目录是公开发布的独立 Skill Pack，正式 payload 为 `skills/comfypet-jmcai-skill/`。
- 源项目：`/mnt/c/Users/cdall/Desktop/AG/comfypet-jmcai-skill-pack`；宿主机目录作为备份保留。
- Git 仓库：`https://github.com/allen-Jmc/comfypet-jmcai-skill-pack.git`，主分支为 `main`。
- 桌面端是同级独立项目 `../Comfypet-JMCAI`；维护者仓是同级独立项目 `../comfypet-jmcai-skill-pack-maintainers`。

## 开发约定

- 只在本项目目录执行 Python、测试和 Git 命令；不要把 Skill 源码复制到工作区根目录或桌面端目录。
- 使用 Python 3 运行 CLI 和测试；当前项目无需要复制的第三方虚拟环境。
- `dist/`、`__pycache__/`、`.pyc` 和日志是可重建产物，不要提交或跨项目复制。
- 当前仓库迁移时已保留源项目的未提交修改；开发前先运行 `git status --short`，不要擅自 reset、clean 或 checkout 覆盖这些修改。
- 修改 Bridge 契约时，需要对照同级桌面端的 Workflow Bridge 实现和维护仓的发布验收文档，但变更分别在对应仓库中完成。

## 常用检查

```bash
python3 -m py_compile skills/comfypet-jmcai-skill/jmcai_skill.py
python3 -m unittest discover -s tests
python3 skills/comfypet-jmcai-skill/jmcai_skill.py --version
```

正式发布 payload 只取 `skills/comfypet-jmcai-skill/`，发布流程和分发脚本由同级维护者仓负责。
