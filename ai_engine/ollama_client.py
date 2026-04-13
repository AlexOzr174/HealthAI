"""HTTP-клиент к локальному Ollama (/api/chat, /api/tags)."""
from __future__ import annotations

import json
from typing import Any, Dict, Generator, List, Optional

import requests


def ollama_list_models(base_url: str, timeout: float = 5.0) -> List[str]:
    url = base_url.rstrip("/") + "/api/tags"
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        out: List[str] = []
        for m in data.get("models") or []:
            name = (m or {}).get("name")
            if name:
                out.append(name)
        return out
    except Exception:
        return []


def ollama_has_model(base_url: str, model: str, timeout: float = 5.0) -> bool:
    want = (model or "").strip()
    if not want:
        return False
    names = ollama_list_models(base_url, timeout=timeout)
    if want in names:
        return True
    return any(n == want or n.startswith(want + ":") for n in names)


def ollama_chat(
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
    options: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    url = base_url.rstrip("/") + "/api/chat"
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
    }
    if options:
        payload["options"] = options
    try:
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        msg = data.get("message") or {}
        content = msg.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()
    except Exception:
        pass
    return None


def ollama_chat_stream(
    base_url: str,
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
    options: Optional[Dict[str, Any]] = None,
) -> Generator[str, None, None]:
    """Потоковый /api/chat (stream: true), отдаёт только дельты текста ассистента."""
    url = base_url.rstrip("/") + "/api/chat"
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    if options:
        payload["options"] = options
    try:
        with requests.post(
            url,
            json=payload,
            stream=True,
            timeout=timeout,
        ) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if data.get("done"):
                    break
                msg = data.get("message") or {}
                content = msg.get("content") or ""
                if isinstance(content, str) and content:
                    yield content
    except Exception:
        return
