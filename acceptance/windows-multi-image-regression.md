# Windows 多图 Workflow 回归清单

- 验收日期：2026-04-03
- 适用仓库：`comfypet-jmcai-skill-pack`
- 适用 skill：`comfypet-jmcai-skill`
- 适用 workflow：`qwen-edit-2`
- 本地 bridge：`http://localhost:32100`
- 远程 bridge：`http://100.112.24.33:32100`

## 目的

- 验证多图 workflow 在本地和远程 bridge 场景下均可正常运行。
- 验证远程多图上传、同图去重复用、结果自动下载、单点错误拦截链路。
- 作为后续版本发布前的固定回归清单。

## 前置条件

- Windows 机器已安装 Python 3。
- 本地 JMCAI 桌面端已启动，并暴露 `qwen-edit-2`。
- 远程 JMCAI 桌面端 `100.112.24.33:32100` 已启动，并暴露 `qwen-edit-2`。
- 本地测试素材已准备：
  - `C:\Users\cdall\Pictures\test1.png`
  - `C:\Users\cdall\Pictures\test2.png`

## 临时配置

### 本地配置

```powershell
@'
{
  "bridge_url": "http://localhost:32100",
  "request_timeout_ms": 15000,
  "min_bridge_version": "1.1.0"
}
'@ | Set-Content "$env:TEMP\jmcai-local-config.json" -Encoding utf8
```

### 远程配置

```powershell
@'
{
  "bridge_url": "http://100.112.24.33:32100",
  "request_timeout_ms": 15000,
  "upload_timeout_ms": 120000,
  "download_timeout_ms": 120000,
  "network_retry_count": 1,
  "retry_backoff_ms": 1500,
  "min_bridge_version": "1.1.0"
}
'@ | Set-Content "$env:TEMP\jmcai-remote-multi-config.json" -Encoding utf8
```

## 回归场景

### 1. 本地双图正向

```powershell
$payload = [ordered]@{
  image_3 = 'C:/Users/cdall/Pictures/test2.png'
  image_39 = 'C:/Users/cdall/Pictures/test1.png'
  提示词 = '请结合两张图片内容进行自然编辑，保持主体清晰并输出白天效果。'
} | ConvertTo-Json -Compress

python skills/comfypet-jmcai-skill/jmcai_skill.py --config "$env:TEMP\jmcai-local-config.json" run --workflow qwen-edit-2 --args $payload
```

验收标准：

- 返回 `id`
- `status` 最终为 `success`
- `args.image_3` 和 `args.image_39` 仍是本机绝对路径
- 输出文件位于本机桌面端输出目录

### 2. 远程双图正向

```powershell
$payload = [ordered]@{
  image_3 = 'C:/Users/cdall/Pictures/test2.png'
  image_39 = 'C:/Users/cdall/Pictures/test1.png'
  提示词 = '请结合两张图片内容进行自然编辑，保持主体清晰并输出白天效果。'
} | ConvertTo-Json -Compress

python skills/comfypet-jmcai-skill/jmcai_skill.py --config "$env:TEMP\jmcai-remote-multi-config.json" run --workflow qwen-edit-2 --args $payload
```

验收标准：

- 返回 `id`
- `status` 最终为 `success`
- `run.args.image_3` 和 `run.args.image_39` 都被改写为 `upload:...`
- 输出文件自动下载到 `%TEMP%\jmcai-skill-downloads\<run_id>\...`

### 3. 远程同图复用

```powershell
$payload = [ordered]@{
  image_3 = 'C:/Users/cdall/Pictures/test1.png'
  image_39 = 'C:/Users/cdall/Pictures/test1.png'
  提示词 = '请结合两张图片内容进行自然编辑，保持主体清晰并输出白天效果。'
} | ConvertTo-Json -Compress

python skills/comfypet-jmcai-skill/jmcai_skill.py --config "$env:TEMP\jmcai-remote-multi-config.json" run --workflow qwen-edit-2 --args $payload
```

验收标准：

- `run.args.image_3` 和 `run.args.image_39` 都被改写为 `upload:...`
- 优先期望两个字段使用同一个 upload token
- `status` 最终为 `success`

### 4. 第二张图路径不存在

```powershell
$payload = [ordered]@{
  image_3 = 'C:/Users/cdall/Pictures/test1.png'
  image_39 = 'C:/Users/cdall/Pictures/not-exists.png'
  提示词 = '请结合两张图片内容进行自然编辑，保持主体清晰并输出白天效果。'
} | ConvertTo-Json -Compress

python skills/comfypet-jmcai-skill/jmcai_skill.py --config "$env:TEMP\jmcai-remote-multi-config.json" run --workflow qwen-edit-2 --args $payload
```

验收标准：

- 直接返回 JSON 错误
- 错误消息明确指出不存在的图片路径
- 不出现 traceback

### 5. 第二张图非白名单扩展名

```powershell
$payload = [ordered]@{
  image_3 = 'C:/Users/cdall/Pictures/test1.png'
  image_39 = 'C:/Users/cdall/Desktop/AG/comfypet-jmcai-skill-pack/README.md'
  提示词 = '请结合两张图片内容进行自然编辑，保持主体清晰并输出白天效果。'
} | ConvertTo-Json -Compress

python skills/comfypet-jmcai-skill/jmcai_skill.py --config "$env:TEMP\jmcai-remote-multi-config.json" run --workflow qwen-edit-2 --args $payload
```

验收标准：

- 直接返回 JSON 错误
- 错误消息明确指出 `.md` 不允许上传
- 第一张图的既有校验逻辑不受影响

## 建议轮询方式

```powershell
$runId = '<run_id>'
do {
  Start-Sleep -Seconds 5
  $status = python skills/comfypet-jmcai-skill/jmcai_skill.py --config "$env:TEMP\jmcai-remote-multi-config.json" status --run-id $runId | ConvertFrom-Json
  $status.status
} while ($status.status -in @('queued', 'running'))

$status | ConvertTo-Json -Depth 10
```

重点关注：

- `status`
- `args`
- `resolved_args`
- `outputs`
- `warnings`

## 最近一次执行结果

- 2026-04-03 本地双图正向通过：run id `bd3622ae-63a9-4dae-bc47-949367c71a3e`
- 2026-04-03 远程双图正向通过：run id `bb7381d9-f3c0-46ac-a71f-3d13930c82a4`
- 2026-04-03 远程同图复用通过：run id `8dd70555-c00b-4ad1-a822-8f70992b75b3`
- 2026-04-03 第二张图路径不存在拦截通过
- 2026-04-03 第二张图非白名单扩展名拦截通过

## 结论口径

- 如果以上 5 项均通过，可以对外表述：
  - “多图 workflow 在本地与远程 bridge 场景下均已通过回归验证。”
  - “远程多图上传、同图去重复用、结果自动下载与错误拦截链路均已验证。”
