# Skill 使用指南

## 读者

- 通过 OpenClaw、Codex、Claude Code 或命令行直接调用 skill 的使用者。

## 用途

- 说明正确调用顺序、图片和视频 workflow 的最小调用方式，以及运行结果应该怎么看。

## 关联文档

- [README](../README.md)
- [安装指南](./install-guide.md)

## 使用前提

- Skill 已按 [安装指南](./install-guide.md) 正确安装
- 桌面端已经启动
- Workflow Center 中已经配置好 workflow、暴露参数和 target

## 推荐调用顺序

1. `doctor`
2. `registry --agent`
3. `run`
4. `status`
5. `history`

## 1. 自检

```powershell
python jmcai_skill.py doctor
```

成功时会返回：

- `bridge_version`
- `capabilities`
- `workflow_count`
- `problems`
- `warnings`

## 2. 查询可用 workflow

```powershell
python jmcai_skill.py registry --agent
```

重点关注这些字段：

- `id`
- `name`
- `summary`
- `tags`
- `input_modalities`
- `output_modalities`
- `example_prompts`
- `schema`
- `available_targets`
- `default_target_id`

## 3. 提交一次图片 workflow

```powershell
python jmcai_skill.py run --workflow smoke-workflow --args "{\"prompt_1\":\"a clean product photo\",\"image_6\":\"/absolute/path/to/input.png\"}"
```

说明：

- `args` 只能使用 `registry --agent` 返回的 alias 字段
- 本机 bridge 场景下，`image` 参数可直接使用本机绝对路径
- 局域网远程 bridge 场景下，仍然传当前机器的本机绝对路径，skill 会自动上传并改写成 `upload:<id>`
- 如果 workflow 配置了默认 target，可以不传 `--target`

## 4. 提交一次视频 workflow

```powershell
python jmcai_skill.py run --workflow smoke-video-workflow --args "{\"prompt_1\":\"a cinematic cat video\"}"
```

图片 workflow 和视频 workflow 的调用形式相同，区别主要体现在：

- `registry --agent` 返回的 `output_modalities`
- `status` / `history` 返回的 `outputs[*].media_kind`

## 5. 查询运行状态

```powershell
python jmcai_skill.py status --run-id <run_id>
```

当前状态只有四种：

- `queued`
- `running`
- `success`
- `error`

成功时，读取 `outputs`。
如果返回了 `warnings`，说明任务本身可能已经成功，但自动下载到本机的某一步出现了网络或本地写入问题。

## 6. 读取历史

```powershell
python jmcai_skill.py history --workflow smoke-workflow --limit 5
```

适合用于：

- 回看最近运行记录
- 对比图片 / 视频输出
- 查找错误信息

## 输出结果怎么看

`outputs` 当前是 typed output 数组，例如：

```json
[
  {
    "path": "/absolute/path/to/smoke-video-workflow_01.mp4",
    "media_kind": "video",
    "file_name": "smoke-video-workflow_01.mp4",
    "mime_type": "video/mp4"
  }
]
```

字段含义：

- `path`：当前执行 skill 这台机器上的本地绝对路径；远程 bridge 场景会先自动下载再返回
- `media_kind`：`image | video | file`
- `file_name`：文件名
- `mime_type`：可选 MIME 类型
- `warnings`：可选；当远程任务生成成功，但输出回传到本机失败时，会给出可执行告警

## 参数使用规则

- 只能填写已暴露 alias 参数
- 不能自己构造 `node_id.field` 参数
- `required: true` 的参数必须补齐
- `choices`、`min`、`max` 会继续由 bridge 在主应用侧做硬校验
- `image` 类型始终传当前机器上的本机绝对路径；远程 bridge 会由 skill 自动上传

## 不支持的事情

当前 V1 不支持：

- 通过 skill 导入 workflow
- 通过 skill 修改 schema
- 通过 skill 修改 target 绑定
- 通过 skill 直连 ComfyUI 原生 `/prompt`

## 常见错误

### `No enabled workflows are currently exposed by Workflow Bridge.`

说明桌面端当前没有对外公开任何可用 workflow。  
优先检查：

- workflow 是否启用
- default target 是否存在
- target 当前是否可用

### `Cannot reach Workflow Bridge`

说明 skill 能运行，但你配置的 bridge 不可达。  
优先检查：

- 桌面端是否已启动
- `bridge_url` 是否正确
- 目标主机的 `32100` 端口是否可达，或本机 `127.0.0.1:32100` 是否被其他程序占用或未监听

### `Timed out while uploading ...`

说明远程 bridge 的上传阶段超时了，常见于：

- 图片较大
- 当前网络上行带宽较低
- 远程桌面端临时无响应

优先处理：

- 增大 `upload_timeout_ms`
- 保持 `request_timeout_ms` 用于普通查询，不要把所有阶段都绑到同一个超时上
- 确认远程 bridge 地址可访问，再重试 `run`

### `status` 返回 `success`，但同时带有 `warnings`

说明生成已经成功，但某些输出在自动下载回本机时失败了。  
优先处理：

- 增大 `download_timeout_ms`
- 检查本机临时目录权限和磁盘空间
- 重新调用一次 `status` 或 `history`，让 skill 再次尝试下载输出

### `未知参数`

说明传入了 schema 之外的字段。  
只使用 `registry --agent` 返回的 alias。

### `缺少必填参数`

说明 workflow 需要的 exposed args 没传齐。
