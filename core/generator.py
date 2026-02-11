"""Generation layer for commit-message candidates.

This module owns prompt composition and provider calls. It must never validate
policy/rule constraints; validation belongs to `core.validator`.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.logger import debug_log
from core.types import CommitMessage, DiffContext, GeneratorOutput
from providers.registry import PROVIDERS


def load_prompt(strategy: str) -> str:
    """Load a prompt template by strategy name.

    Input contract:
    - `strategy` maps to `<prompt_dir>/<strategy>.txt`.

    Output contract:
    - Returns template text.

    Side effects:
    - Reads a file from disk.
    """

    prompt_dir = Path("prompts")
    candidates = [
        prompt_dir / f"{strategy}.txt",
        prompt_dir / f"{strategy.replace('-', '_')}.txt",
    ]
    for prompt_file in candidates:
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
    raise FileNotFoundError(f"Prompt strategy file not found for: {strategy}")


def build_prompt(
    template: str,
    context: DiffContext,
    intent: str | None,
    constraints: dict[str, Any] | None,
) -> str:
    """Compose provider prompt from template and diff context.

    Input contract:
    - `template` is raw prompt template text.
    - `context` contains diff/status metadata from analyzer.
    - `intent` and `constraints` are optional guidance hints.

    Output contract:
    - Returns a fully formatted prompt string.

    Side effects:
    - None.
    """

    constraints_text = json.dumps(constraints or {}, sort_keys=True)
    return (
        f"{template}\n\n"
        f"Intent: {intent or ''}\n"
        f"Constraints: {constraints_text}\n"
        f"Status:\n{context.status}\n\n"
        f"Diff:\n{context.diff}\n"
    )


def call_provider(provider: str, model: str, prompt: str) -> str:
    """Call a registered provider to generate a raw model response.

    Input contract:
    - `provider` must exist in `providers.registry.PROVIDERS`.
    - `model` must be valid for the selected provider.
    - `prompt` is opaque text payload.

    Output contract:
    - Returns raw response text from provider.

    Side effects:
    - Performs network I/O via provider implementation.
    """

    if provider not in PROVIDERS:
        raise KeyError(f"Unknown provider: {provider}")
    return PROVIDERS[provider]["generate"](prompt, model)


def sanitize_output(raw: str) -> str:
    """Strip markdown fences/noise around JSON output.

    Input contract:
    - `raw` is untrusted model response text.

    Output contract:
    - Returns text likely to be JSON.

    Side effects:
    - None.
    """

    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def safe_parse_json(text: str) -> dict[str, Any] | None:
    """Parse JSON safely without raising to callers.

    Input contract:
    - `text` should be JSON object text.

    Output contract:
    - Returns decoded dict on success, else `None`.

    Side effects:
    - None.
    """

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def normalize(parsed: dict[str, Any]) -> CommitMessage | None:
    """Normalize decoded JSON object into `CommitMessage`.

    Input contract:
    - `parsed` may contain keys: type, scope, subject, body.

    Output contract:
    - Returns `CommitMessage` when minimal schema is satisfiable.

    Side effects:
    - None.
    """

    subject = parsed.get("subject")
    if subject is not None and not isinstance(subject, str):
        return None
    return CommitMessage(
        type=parsed.get("type") if isinstance(parsed.get("type"), str) else None,
        scope=parsed.get("scope") if isinstance(parsed.get("scope"), str) else None,
        subject=subject,
        body=parsed.get("body") if isinstance(parsed.get("body"), str) else None,
        word_count=None,
    )


def generate_commit(
    context: DiffContext,
    prompt_strategy: str,
    provider_name: str,
    model: str,
    intent: str | None,
    constraints: dict[str, Any] | None,
    feedback: str | None = None,
    debug: bool = False,
) -> GeneratorOutput:
    """Generate a commit candidate from diff context and prompt strategy.

    Input contract:
    - `context` must come from analyzer.
    - `prompt_strategy` selects prompt template.
    - `provider_name` and `model` identify generation backend.
    - `intent`, `constraints`, and `feedback` are optional hints.

    Output contract:
    - Returns `GeneratorOutput` with parsed commit or normalized error code.

    Side effects:
    - Reads prompt templates.
    - Calls external providers.
    - Emits debug logs when `debug=True`.
    """

    try:
        template = load_prompt(prompt_strategy)
        prompt = build_prompt(template, context, intent, constraints)
        if feedback:
            prompt = f"{prompt}\n\nFeedback:\n{feedback}"
        raw = call_provider(provider_name, model, prompt)
    except Exception as exc:  # noqa: BLE001
        return GeneratorOutput(commit=None, error="provider_error", meta={"reason": str(exc)})

    cleaned = sanitize_output(raw)
    parsed = safe_parse_json(cleaned)
    if parsed is None:
        return GeneratorOutput(commit=None, error="invalid_json", meta={})

    commit = normalize(parsed)
    if commit is None:
        return GeneratorOutput(commit=None, error="invalid_schema", meta={})

    debug_log(debug, "generator_success", {"provider": provider_name, "model": model})
    return GeneratorOutput(commit=commit, error=None, meta={"provider": provider_name, "model": model})
