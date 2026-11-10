"""生成任务正文。默认用 Qoder 当前模型，也可以改成其他兼容接口。"""

import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request


def generate_text(system, user, model_config=None):
    config = model_config or {}
    provider = (config.get("provider") or "qoder").strip().lower()
    if provider == "qoder":
        return _qoder_text(system, user, (config.get("model") or "").strip())
    if provider == "openai":
        return _openai_text(system, user, config)
    if provider == "anthropic":
        return _anthropic_text(system, user, config)
    raise RuntimeError("不支持的模型 provider：%s，可用 qoder、openai、anthropic" % provider)


def _qoder_text(system, user, model):
    executable = shutil.which("qodercli")
    if not executable:
        raise RuntimeError("没有找到 qodercli。请安装并登录 Qoder CLI，或把模型 provider 改成 openai / anthropic")
    print("正在调用 Qoder 模型（%s），响应完成前不会有正文" % (model or "auto"), flush=True)
    command = [
        executable,
        "-p",
        "--permission-mode",
        "dont_ask",
        "--reasoning-effort",
        "low",
        "--tools",
        "",
        "--output-format",
        "text",
        "--max-output-tokens",
        "4096",
        "--system-prompt",
        system,
    ]
    if model:
        command.extend(["-m", model])
    command.append("--")
    command.append(user)
    try:
        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Qoder 模型超时") from error
    output = (completed.stdout or "").strip()
    error_text = (completed.stderr or "").strip()
    if completed.returncode != 0:
        detail = error_text or output or "无输出"
        if "Not logged in" in detail or "未登录" in detail:
            raise RuntimeError("Qoder CLI 未登录。请先执行 qodercli login，或在模型配置里改用其他模型")
        raise RuntimeError("Qoder 模型调用失败：%s" % detail)
    if not output:
        raise RuntimeError("Qoder 模型没有返回正文：%s" % error_text)
    return output


def _openai_text(system, user, config):
    base_url = (config.get("baseUrl") or "").rstrip("/")
    api_key = config.get("apiKey") or os.environ.get("QINCHUAN_MODEL_API_KEY") or ""
    model = (config.get("model") or "").strip()
    if not base_url or not api_key or not model:
        raise RuntimeError("openai 模型需要 baseUrl、apiKey 和 model")
    url = base_url if base_url.endswith("/chat/completions") else base_url + "/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "temperature": 0.2,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"content-type": "application/json", "authorization": "Bearer " + api_key},
    )
    payload = _read_json(request)
    choices = payload.get("choices") or []
    message = (choices[0].get("message") or {}) if choices else {}
    text = (message.get("content") or "").strip()
    if not text:
        raise RuntimeError("模型没有返回正文：%s" % payload)
    return text


def _anthropic_text(system, user, config):
    base_url = (config.get("baseUrl") or "").rstrip("/")
    api_key = config.get("apiKey") or os.environ.get("QINCHUAN_MODEL_API_KEY") or ""
    model = (config.get("model") or "").strip()
    if not base_url or not api_key or not model:
        raise RuntimeError("anthropic 模型需要 baseUrl、apiKey 和 model")
    url = base_url if base_url.endswith("/messages") else base_url + "/v1/messages"
    body = json.dumps(
        {
            "model": model,
            "max_tokens": 4096,
            "thinking": {"type": "disabled"},
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "content-type": "application/json",
            "authorization": "Bearer " + api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    payload = _read_json(request)
    texts = [
        block.get("text", "")
        for block in payload.get("content") or []
        if block.get("type") == "text" and block.get("text")
    ]
    text = "\n".join(texts).strip()
    if not text:
        raise RuntimeError("模型没有返回正文：%s" % payload)
    return text


def _read_json(request):
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError("大模型调用失败：%s %s" % (error.code, detail)) from error
