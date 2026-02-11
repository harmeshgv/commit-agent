"""Ollama provider adapter.

This module only handles API transport for already-built prompt text.
"""

from __future__ import annotations

import os

import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "8192"))
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))


def list_models() -> list[str]:
    """List model identifiers available from Ollama host.

    Input contract:
    - Reads `OLLAMA_HOST` environment configuration.

    Output contract:
    - Returns model name list.

    Side effects:
    - Performs HTTP GET request.
    """

    response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
    response.raise_for_status()
    models = response.json().get("models", [])
    return [entry["name"] for entry in models if isinstance(entry.get("name"), str)]


def generate(prompt: str, model: str) -> str:
    """Generate completion text from Ollama.

    Input contract:
    - `prompt` is already composed by generator layer.
    - `model` is a valid Ollama model identifier.

    Output contract:
    - Returns raw response text from Ollama.

    Side effects:
    - Performs HTTP POST request.
    """

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_ctx": OLLAMA_NUM_CTX},
    }
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    body = response.json()
    text = body.get("response")
    if not isinstance(text, str):
        raise ValueError("Invalid Ollama response payload.")
    return text
