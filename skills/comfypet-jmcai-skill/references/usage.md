# 图片 / 视频工作流使用参考

## 图片 workflow

典型步骤：

1. 用 `registry --agent` 找到 `output_modalities` 包含 `image` 的 workflow
2. 填写必填文本参数
3. 若 schema 中包含 `image` 字段：
   - 本机直连 bridge 时，传本机绝对路径
   - 远程 bridge 时，仍然传当前机器的本机绝对路径，skill 会自动上传
4. 调用 `run`
5. 用 `status` 读取图片输出路径；远程 bridge 场景会自动下载到当前机器

示例：

```bash
python scripts/jmcai_skill.py run --workflow demo-image --args '{"prompt_1":"a clean product photo","image_6":"C:\\Users\\name\\Pictures\\input.png"}'
```

## 视频 workflow

典型步骤：

1. 用 `registry --agent` 找到 `output_modalities` 包含 `video` 的 workflow
2. 填写必填文本参数
3. 调用 `run`
4. 用 `status` 读取视频输出路径

示例：

```bash
python scripts/jmcai_skill.py run --workflow demo-video --args '{"prompt_1":"a cinematic cat video"}'
```

## 常见错误

- `No enabled workflows are currently exposed by Workflow Bridge.`
  说明桌面端当前没有公开可用 workflow

- `Cannot reach Workflow Bridge`
  说明 bridge 不可达，优先检查桌面端是否已启动

- `Bridge upload response did not include upload_id.`
  说明远程桌面端 bridge 版本过低或未正确升级到新上传接口

- `未知参数`
  说明传入了 schema 之外的字段

- `缺少必填参数`
  说明必填 alias 没传齐
