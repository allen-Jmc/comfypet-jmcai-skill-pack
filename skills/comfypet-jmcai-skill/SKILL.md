---
name: comfypet-jmcai-skill
description: |
  调用 JMCAI Comfypet 桌面应用中已经配置好的 ComfyUI 图片和视频工作流。用于查询可用 workflow、读取暴露参数、提交运行并轮询结果。适用于用户要求生成图片、生成视频或执行已配置 workflow 的场景；不适用于导入 workflow、修改 schema、修改 target 绑定或直连原生 ComfyUI 接口。
---

# JMCAI Comfypet Skill

先运行：

```bash
python scripts/jmcai_skill.py doctor
python scripts/jmcai_skill.py registry --agent
```

然后按以下顺序执行：

1. 根据 `summary`、`tags`、`input_modalities`、`output_modalities`、`example_prompts` 选择最合适的 workflow。
2. 只填写 alias schema 中暴露的参数。
3. 提交运行：

```bash
python scripts/jmcai_skill.py run --workflow <workflow_id> --args '{"prompt_1":"a cinematic scene"}'
```

4. 读取 `run_id` 后，单次查询状态：

```bash
python scripts/jmcai_skill.py status --run-id <run_id>
```

5. 如需回看，再读取：

```bash
python scripts/jmcai_skill.py history --workflow <workflow_id> --limit 5
```

## Parameter Rules

- 缺少 `required: true` 的参数时，向用户追问或在上下文足够明确时补齐
- 只能使用 `registry --agent` 返回的 alias 参数名
- `image` 类型参数必须是本机绝对路径
- 不要修改 schema、workflow 或 target 配置

## Failure Handling

- `doctor` 失败：提示用户启动或升级 JMCAI 桌面应用
- `run` 返回错误：把错误原文反馈给用户，不要伪造成功
- `status` 返回 `queued` 或 `running`：告诉用户仍在生成，并在下一次独立调用中继续查询
- `status` 返回 `success`：返回 `outputs` 中的本地文件路径

需要 bridge 契约细节时，读取 `references/bridge.md`。  
需要图片 / 视频工作流示例时，读取 `references/usage.md`。
