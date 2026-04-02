#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

VERSION = "1.2.1"
DESKTOP_APP_URL = "https://github.com/allen-Jmc/comfypet-jmcai-Dist"
DEFAULT_CONFIG = {
    "bridge_url": "http://127.0.0.1:32100",
    "request_timeout_ms": 15000,
    "min_bridge_version": "1.1.0",
}

# 智能路径寻址：确保加载 config.json 或资源文件时使用绝对路径
SKILL_ROOT = Path(__file__).resolve().parent
LOOPBACK_BRIDGE_HOSTS = {"127.0.0.1", "localhost", "::1"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

class RequestFailure(Exception):
    def __init__(self, message: str, payload: Any) -> None:
        super().__init__(message)
        self.message = message
        self.payload = payload

# ==========================================
# Dual-Mode: Registry 暴露与解耦配置加载
# ==========================================

def load_config(explicit_path: str | None = None) -> dict[str, Any]:
    """解耦配置加载逻辑，支持无参调用（默认搜寻 SKILL_ROOT）"""
    config_path = Path(explicit_path).resolve() if explicit_path else SKILL_ROOT / "config.json"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
            return {**DEFAULT_CONFIG, **loaded}

    example_path = SKILL_ROOT / "config.example.json"
    if example_path.exists():
        with example_path.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
            return {**DEFAULT_CONFIG, **loaded}

    return dict(DEFAULT_CONFIG)

def registry() -> dict[str, Any]:
    """
    显式暴露的 Registry 入口：
    供 Agent 框架 (如 OpenClaw) 导入模块时直接调用 `import jmcai_skill; jmcai_skill.registry()` 获取技能元数据。
    """
    config = load_config()
    return registry_command(config, _agent_mode=True)

# ==========================================
# CLI 入口与路由
# ==========================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="JMCAI Comfypet Skill CLI")
    parser.add_argument("--config", default=None, help="Path to config.json")
    parser.add_argument("--version", action="version", version=f"jmcai-skill {VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    registry_parser = subparsers.add_parser("registry", help="List available workflows")
    registry_parser.add_argument("--agent", action="store_true", help="Machine-readable output")

    run_parser = subparsers.add_parser("run", help="Submit a workflow run")
    run_parser.add_argument("--workflow", required=True, help="Workflow ID")
    run_parser.add_argument("--args", required=True, help="JSON args")
    run_parser.add_argument("--target", default=None, help="Optional target ID")

    status_parser = subparsers.add_parser("status", help="Fetch run status")
    status_parser.add_argument("--run-id", required=True, help="Run ID")

    history_parser = subparsers.add_parser("history", help="Fetch workflow history")
    history_parser.add_argument("--workflow", required=True, help="Workflow ID")
    history_parser.add_argument("--limit", type=int, default=None, help="Optional history size")

    subparsers.add_parser("doctor", help="Validate bridge and workflow metadata")

    args = parser.parse_args(argv)
    config = load_config(args.config)

    if args.command == "registry":
        emit(registry_command(config, args.agent))
        return 0

    if args.command == "run":
        emit(run_command(config, args.workflow, args.args, args.target))
        return 0

    if args.command == "status":
        emit(status_command(config, args.run_id))
        return 0

    if args.command == "history":
        emit(history_command(config, args.workflow, args.limit))
        return 0

    if args.command == "doctor":
        result = doctor_command(config)
        emit(result)
        return 0 if result.get("status") == "success" else 1

    return 1

# ==========================================
# 核心功能实现
# ==========================================

def registry_command(config: dict[str, Any], _agent_mode: bool) -> dict[str, Any]:
    health = request_json(config, "GET", "/api/v1/health")
    workflows_payload = request_json(config, "GET", "/api/v1/workflows")
    workflows = [normalize_workflow(workflow) for workflow in workflows_payload.get("workflows", [])]
    return {
        "status": "success",
        "bridge_version": health.get("bridge_version"),
        "desktop_app": health.get("desktop_app"),
        "capabilities": list(health.get("capabilities", [])),
        "workflow_count": len(workflows),
        "workflows": workflows,
    }


def run_command(
    config: dict[str, Any],
    workflow_id: str,
    raw_args: str,
    target_id: str | None,
) -> dict[str, Any]:
    try:
        parsed_args = json.loads(raw_args)
    except json.JSONDecodeError as error:
        return {"status": "error", "message": f"Invalid args JSON: {error}"}

    if not isinstance(parsed_args, dict):
        return {"status": "error", "message": "Args JSON must be an object."}

    prepared_args = prepare_run_args(config, workflow_id, parsed_args)
    if prepared_args.get("status") == "error":
        return prepared_args

    payload: dict[str, Any] = {"args": parsed_args}
    if "args" in prepared_args:
        payload["args"] = prepared_args["args"]
    if target_id:
        payload["target_id"] = target_id

    try:
        response = request_json(
            config,
            "POST",
            f"/api/v1/workflows/{urllib.parse.quote(workflow_id)}/runs",
            payload,
        )
    except RequestFailure as error:
        return {"status": "error", "message": error.message, "details": error.payload}

    return normalize_run(response)


def status_command(config: dict[str, Any], run_id: str) -> dict[str, Any]:
    try:
        response = request_json(config, "GET", f"/api/v1/runs/{urllib.parse.quote(run_id)}")
    except RequestFailure as error:
        return {"status": "error", "message": error.message, "details": error.payload}

    return localize_run_outputs(config, normalize_run(response))


def history_command(config: dict[str, Any], workflow_id: str, limit: int | None) -> dict[str, Any]:
    try:
        response = request_json(
            config,
            "GET",
            f"/api/v1/workflows/{urllib.parse.quote(workflow_id)}/history",
        )
    except RequestFailure as error:
        return {"status": "error", "message": error.message, "details": error.payload}

    history = [normalize_run(item) for item in response.get("history", [])]
    if limit is not None and limit >= 0:
        history = history[:limit]

    history = [localize_run_outputs(config, run) for run in history]
    return {"status": "success", "workflow_id": workflow_id, "history": history}


def doctor_command(config: dict[str, Any]) -> dict[str, Any]:
    problems: list[str] = []
    warnings: list[str] = []

    try:
        health = request_json(config, "GET", "/api/v1/health")
    except RequestFailure as error:
        msg = error.message
        if is_loopback_bridge(config):
            msg += f"\n[HINT] JMCAI Desktop App might not be running. Download it at: {DESKTOP_APP_URL}"
        return {
            "status": "error",
            "bridge_url": config["bridge_url"],
            "problems": [msg],
            "warnings": [],
        }

    bridge_version = str(health.get("bridge_version", "0.0.0"))
    min_bridge_version = str(config.get("min_bridge_version", DEFAULT_CONFIG["min_bridge_version"]))
    if compare_versions(bridge_version, min_bridge_version) < 0:
        problems.append(
            f"Bridge version {bridge_version} is lower than required {min_bridge_version}. Please upgrade JMCAI desktop app."
        )

    try:
        workflows_payload = request_json(config, "GET", "/api/v1/workflows")
    except RequestFailure as error:
        problems.append(error.message)
        workflows_payload = {"workflows": []}

    workflows = [normalize_workflow(item) for item in workflows_payload.get("workflows", [])]
    if not workflows:
        problems.append("No enabled workflows are currently exposed by Workflow Bridge.")

    workflows_with_default_target = 0
    for workflow in workflows:
        missing_fields = []
        if not workflow.get("summary"):
            missing_fields.append("summary")
        if not workflow.get("schema"):
            missing_fields.append("schema")
        if not workflow.get("input_modalities"):
            missing_fields.append("input_modalities")
        if not workflow.get("output_modalities"):
            missing_fields.append("output_modalities")
        if missing_fields:
            problems.append(
                f"Workflow '{workflow.get('id', 'unknown')}' is missing metadata fields: {', '.join(missing_fields)}."
            )

        default_target_id = workflow.get("default_target_id")
        available_targets = workflow.get("available_targets", [])
        if not default_target_id:
            warnings.append(f"Workflow '{workflow.get('id', 'unknown')}' has no default target.")
            continue

        target = next((item for item in available_targets if item.get("id") == default_target_id), None)
        if not target:
            warnings.append(
                f"Workflow '{workflow.get('id', 'unknown')}' default target '{default_target_id}' is not in available_targets."
            )
            continue

        if not target.get("available", False):
            warnings.append(
                f"Workflow '{workflow.get('id', 'unknown')}' default target '{default_target_id}' is not currently available."
            )
            continue

        workflows_with_default_target += 1

    if workflows and workflows_with_default_target == 0:
        problems.append("No workflow currently has an available default target.")

    return {
        "status": "success" if not problems else "error",
        "bridge_url": config["bridge_url"],
        "bridge_version": bridge_version,
        "min_bridge_version": min_bridge_version,
        "desktop_app": health.get("desktop_app"),
        "capabilities": list(health.get("capabilities", [])),
        "workflow_count": len(workflows),
        "problems": problems,
        "warnings": warnings,
    }


def normalize_workflow(payload: dict[str, Any]) -> dict[str, Any]:
    schema = []
    for field in payload.get("schema", []):
        if not isinstance(field, dict):
            continue
        schema.append(
            {
                "alias": field.get("alias", ""),
                "type": field.get("type", "string"),
                "required": bool(field.get("required", False)),
                "description": field.get("description", ""),
                "default_value": field.get("default_value"),
                "choices": list(field.get("choices", [])),
                "min": field.get("min"),
                "max": field.get("max"),
            }
        )

    available_targets = []
    for target in payload.get("available_targets", []):
        if not isinstance(target, dict):
            continue
        available_targets.append(
            {
                "id": target.get("id", ""),
                "name": target.get("name", ""),
                "type": target.get("type", ""),
                "available": bool(target.get("available", False)),
            }
        )

    return {
        "id": payload.get("id", ""),
        "name": payload.get("name", ""),
        "description": payload.get("description", ""),
        "summary": payload.get("summary") or payload.get("description", ""),
        "tags": list(payload.get("tags", [])),
        "input_modalities": list(payload.get("input_modalities", [])),
        "output_modalities": list(payload.get("output_modalities", [])),
        "example_prompts": list(payload.get("example_prompts", [])),
        "default_target_id": payload.get("default_target_id"),
        "schema": schema,
        "available_targets": available_targets,
    }


def normalize_run(payload: dict[str, Any]) -> dict[str, Any]:
    outputs = []
    raw_outputs = payload.get("outputs", [])
    if isinstance(raw_outputs, list):
        for output in raw_outputs:
            if isinstance(output, str):
                outputs.append(normalize_legacy_output(output))
                continue
            if not isinstance(output, dict):
                continue
            path_value = str(output.get("path", ""))
            outputs.append(
                {
                    "path": path_value,
                    "download_path": output.get("download_path") or output.get("downloadPath"),
                    "media_kind": output.get("media_kind") or output.get("mediaKind") or infer_media_kind(path_value),
                    "file_name": output.get("file_name") or output.get("fileName") or Path(path_value).name,
                    "mime_type": output.get("mime_type") or output.get("mimeType"),
                }
            )

    return {
        "id": payload.get("id", ""),
        "workflow_id": payload.get("workflow_id") or payload.get("workflowId", ""),
        "workflow_name": payload.get("workflow_name") or payload.get("workflowName", ""),
        "target_id": payload.get("target_id") or payload.get("targetId", ""),
        "target_name": payload.get("target_name") or payload.get("targetName", ""),
        "target_type": payload.get("target_type") or payload.get("targetType", ""),
        "status": payload.get("status", ""),
        "args": payload.get("args", {}),
        "resolved_args": payload.get("resolved_args") or payload.get("resolvedArgs", {}),
        "outputs": outputs,
        "prompt_id": payload.get("prompt_id") or payload.get("promptId"),
        "error_message": payload.get("error_message") or payload.get("errorMessage"),
        "queued_at": payload.get("queued_at") or payload.get("queuedAt"),
        "started_at": payload.get("started_at") or payload.get("startedAt"),
        "finished_at": payload.get("finished_at") or payload.get("finishedAt"),
        "duration_ms": payload.get("duration_ms") or payload.get("durationMs"),
    }


def normalize_legacy_output(path_value: str) -> dict[str, Any]:
    return {
        "path": path_value,
        "media_kind": infer_media_kind(path_value),
        "file_name": Path(path_value).name,
        "mime_type": None,
    }


def infer_media_kind(path_value: str) -> str:
    suffix = Path(path_value).suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
        return "image"
    if suffix in {".mp4", ".webm", ".mov", ".avi", ".gif"}:
        return "video"
    return "file"


def request_json(
    config: dict[str, Any],
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = f"{str(config['bridge_url']).rstrip('/')}{path}"
    request_body = None
    headers = {"Accept": "application/json"}
    if body is not None:
        request_body = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=request_body, method=method, headers=headers)
    timeout_seconds = max(float(config.get("request_timeout_ms", 15000)) / 1000.0, 1.0)

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise RequestFailure("Bridge returned non-object JSON.", {"payload": payload})
            return payload
    except urllib.error.HTTPError as error:
        try:
            payload = json.loads(error.read().decode("utf-8"))
        except Exception:
            payload = {"message": f"Bridge HTTP {error.code}"}
        message = payload.get("message") if isinstance(payload, dict) else None
        raise RequestFailure(str(message or f"Bridge HTTP {error.code}"), payload)
    except urllib.error.URLError as error:
        msg = f"Cannot reach Workflow Bridge at {url}: {error.reason}"
        if is_loopback_bridge(config):
            msg += f" (Is JMCAI Desktop App running? Download: {DESKTOP_APP_URL})"
        raise RequestFailure(msg, None)


def request_bytes(config: dict[str, Any], path: str) -> tuple[bytes, dict[str, str]]:
    url = build_bridge_url(config, path)
    request = urllib.request.Request(url, method="GET", headers={"Accept": "*/*"})
    timeout_seconds = max(float(config.get("request_timeout_ms", 15000)) / 1000.0, 1.0)

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.read(), headers
    except urllib.error.HTTPError as error:
        try:
            payload = json.loads(error.read().decode("utf-8"))
        except Exception:
            payload = {"message": f"Bridge HTTP {error.code}"}
        message = payload.get("message") if isinstance(payload, dict) else None
        raise RequestFailure(str(message or f"Bridge HTTP {error.code}"), payload)
    except urllib.error.URLError as error:
        msg = f"Cannot reach Workflow Bridge at {url}: {error.reason}"
        if is_loopback_bridge(config):
            msg += f" (Is JMCAI Desktop App running? Download: {DESKTOP_APP_URL})"
        raise RequestFailure(msg, None)


def prepare_run_args(
    config: dict[str, Any], workflow_id: str, parsed_args: dict[str, Any]
) -> dict[str, Any]:
    if is_loopback_bridge(config):
        return {"status": "success", "args": parsed_args}

    try:
        workflows_payload = request_json(config, "GET", "/api/v1/workflows")
    except RequestFailure as error:
        return {"status": "error", "message": error.message, "details": error.payload}

    workflow = next(
        (
            item
            for item in workflows_payload.get("workflows", [])
            if isinstance(item, dict) and item.get("id") == workflow_id
        ),
        None,
    )
    if workflow is None:
        return {"status": "error", "message": f"Workflow '{workflow_id}' not found in bridge registry."}

    schema = workflow.get("schema", [])
    image_aliases = {
        field.get("alias", "")
        for field in schema
        if isinstance(field, dict) and field.get("type") == "image" and field.get("alias")
    }
    if not image_aliases:
        return {"status": "success", "args": parsed_args}

    uploaded_by_path: dict[str, str] = {}
    next_args = dict(parsed_args)

    for alias in image_aliases:
        raw_value = next_args.get(alias)
        if not isinstance(raw_value, str):
            continue
        value = raw_value.strip()
        if not value or value.startswith("upload:") or not looks_like_absolute_path(value):
            continue
        if not os.path.exists(value):
            return {"status": "error", "message": f"Image file does not exist on this machine: {value}"}
        upload_token = uploaded_by_path.get(value)
        if not upload_token:
            upload_result = upload_local_file(config, value)
            if upload_result.get("status") == "error":
                return upload_result
            upload_token = f"upload:{upload_result['upload_id']}"
            uploaded_by_path[value] = upload_token
        next_args[alias] = upload_token

    return {"status": "success", "args": next_args}


def upload_local_file(config: dict[str, Any], local_path: str) -> dict[str, Any]:
    file_path = Path(local_path)
    mime_type = mimetypes.guess_type(file_path.name)[0]
    try:
        content_base64 = base64.b64encode(file_path.read_bytes()).decode("ascii")
    except OSError as error:
        return {"status": "error", "message": f"Failed to read local file: {error}"}

    payload = {
        "file_name": file_path.name,
        "content_base64": content_base64,
    }
    if mime_type:
        payload["mime_type"] = mime_type

    try:
        response = request_json(config, "POST", "/api/v1/uploads", payload)
    except RequestFailure as error:
        return {"status": "error", "message": error.message, "details": error.payload}

    upload_id = response.get("upload_id")
    if not isinstance(upload_id, str) or not upload_id:
        return {"status": "error", "message": "Bridge upload response did not include upload_id."}

    return {"status": "success", "upload_id": upload_id}


def localize_run_outputs(config: dict[str, Any], run_payload: dict[str, Any]) -> dict[str, Any]:
    if is_loopback_bridge(config) or run_payload.get("status") != "success":
        return run_payload

    outputs = run_payload.get("outputs", [])
    if not isinstance(outputs, list):
        return run_payload

    localized_outputs = []
    for output in outputs:
        if not isinstance(output, dict):
            localized_outputs.append(output)
            continue
        localized_outputs.append(localize_output_asset(config, run_payload.get("id", ""), output))

    return {
        **run_payload,
        "outputs": localized_outputs,
    }


def localize_output_asset(config: dict[str, Any], run_id: str, output: dict[str, Any]) -> dict[str, Any]:
    download_path = output.get("download_path")
    file_name = str(output.get("file_name") or Path(str(output.get("path", ""))).name or "output.bin")
    if not isinstance(download_path, str) or not download_path:
        return output

    download_dir = Path(tempfile.gettempdir()) / "jmcai-skill-downloads" / str(run_id or "run")
    download_dir.mkdir(parents=True, exist_ok=True)
    destination = download_dir / sanitize_file_name(file_name)

    if not destination.exists():
        try:
            content, headers = request_bytes(config, download_path)
            destination.write_bytes(content)
            mime_type = output.get("mime_type")
            if not mime_type and "content-type" in headers:
                mime_type = headers["content-type"]
                output = {**output, "mime_type": mime_type}
        except RequestFailure:
            return output

    return {
        **output,
        "path": str(destination),
    }


def build_bridge_url(config: dict[str, Any], path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{str(config['bridge_url']).rstrip('/')}{path}"


def is_loopback_bridge(config: dict[str, Any]) -> bool:
    parsed = urllib.parse.urlparse(str(config.get("bridge_url", "")))
    host = (parsed.hostname or "").lower()
    return host in LOOPBACK_BRIDGE_HOSTS


def looks_like_absolute_path(value: str) -> bool:
    normalized = value.strip()
    if not normalized:
        return False
    return (
        Path(normalized).is_absolute()
        or normalized.startswith("\\\\")
        or (len(normalized) > 2 and normalized[1] == ":" and normalized[2] in {"\\", "/"})
    )


def sanitize_file_name(file_name: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_", "."} else "-" for char in file_name)
    cleaned = cleaned.strip("-.")
    return cleaned or "output.bin"


def compare_versions(left: str, right: str) -> int:
    left_parts = [safe_int(part) for part in left.split(".")]
    right_parts = [safe_int(part) for part in right.split(".")]
    max_len = max(len(left_parts), len(right_parts))
    left_parts.extend([0] * (max_len - len(left_parts)))
    right_parts.extend([0] * (max_len - len(right_parts)))

    for left_part, right_part in zip(left_parts, right_parts):
        if left_part < right_part:
            return -1
        if left_part > right_part:
            return 1

    return 0


def safe_int(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
