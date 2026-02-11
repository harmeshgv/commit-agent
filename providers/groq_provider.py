"""Groq provider adapter.

This module performs provider transport only and does not own prompt strategy
or model defaults.
"""

from __future__ import annotations

import os

import requests

GROQ_MODELS_URL = "https://api.groq.com/openai/v1/models"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"

EXCLUDED_MODEL_KEYWORDS = (
    "whisper",
    "guard",
    "safeguard",
    "prompt-guard",
    "orpheus",
)


def _auth_headers(api_key: str) -> dict[str, str]:
    """Build Groq API request headers.

    Input contract:
    - `api_key` is a non-empty Groq API key string.

    Output contract:
    - Returns headers required for Groq API requests.

    Side effects:
    - None.
    """

    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def list_models() -> list[str]:
    """List available Groq model identifiers.

    Input contract:
    - Uses `GROQ_API_KEY` from environment.

    Output contract:
    - Returns sorted model ID list filtered by excluded keywords.

    Side effects:
    - Performs HTTP GET request when API key is present.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return []

    try:
        response = requests.get(GROQ_MODELS_URL, headers=_auth_headers(api_key), timeout=10)
        response.raise_for_status()
        data = response.json().get("data", [])
    except requests.RequestException:
        return []

    available_ids: list[str] = []
    for model in data:
        model_id = model.get("id")
        if not isinstance(model_id, str):
            continue
        lowered = model_id.lower()
        if any(keyword in lowered for keyword in EXCLUDED_MODEL_KEYWORDS):
            continue
        available_ids.append(model_id)

    return sorted(set(available_ids))


def generate(prompt: str, model: str) -> str:
    """Generate completion text via Groq chat-completions API.

    Input contract:
    - `prompt` is fully composed upstream prompt text.
    - `model` is a model ID accepted by Groq API.

    Output contract:
    - Returns assistant message content as string.

    Side effects:
    - Performs HTTP POST request.
    """

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }
    response = requests.post(
        GROQ_CHAT_URL,
        headers=_auth_headers(api_key),
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    text = data["choices"][0]["message"]["content"]
    if not isinstance(text, str):
        raise ValueError("Invalid Groq response payload.")
    return text
