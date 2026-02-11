"""Shared type definitions for the commit-agent architecture.

All cross-layer data contracts are defined here to keep module boundaries explicit
and avoid ad-hoc dictionary payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

JSONDict = dict[str, Any]
ProviderName = str
ModelName = str
PromptStrategy = str


@dataclass(slots=True)
class DiffContext:
    """Immutable snapshot of staged git state used by generation.

    Input contract:
    - `diff` must be unified diff text for staged changes.
    - `status` must be raw `git status --short` output.
    - `files_changed` must list staged file paths.
    - `insertions` and `deletions` must be non-negative counts.

    Output contract:
    - Represents analyzer output consumed by the generator.

    Side effects:
    - None.
    """

    diff: str
    status: str
    files_changed: list[str]
    insertions: int
    deletions: int


@dataclass(slots=True)
class CommitMessage:
    """Structured commit message produced by generation.

    Input contract:
    - `type`, `scope`, `subject`, `body` are optional textual segments.
    - `word_count` is optional and is populated by validator/engine.

    Output contract:
    - Canonical commit payload used by validator, logger, and CLI.

    Side effects:
    - None.
    """

    type: str | None
    scope: str | None
    subject: str | None
    body: str | None
    word_count: int | None = None


@dataclass(slots=True)
class GeneratorOutput:
    """Result from generator layer before validation.

    Input contract:
    - `commit` contains a parsed structured message when generation succeeds.
    - `error` is set to a normalized generator error code when generation fails.
    - `meta` stores provider/model/strategy latency and debug metadata.

    Output contract:
    - Single-attempt generation payload for engine orchestration.

    Side effects:
    - None.
    """

    commit: CommitMessage | None
    error: Literal["invalid_json", "invalid_schema", "provider_error", "unknown"] | None
    meta: JSONDict = field(default_factory=dict)


@dataclass(slots=True)
class ValidationResult:
    """Validation-only response from validator layer.

    Input contract:
    - `violations` lists schema/rule violations, empty when valid.
    - `word_count` is derived from commit content when available.

    Output contract:
    - Contains no retry, orchestration, or provider state.

    Side effects:
    - None.
    """

    violations: list[str] = field(default_factory=list)
    word_count: int | None = None


@dataclass(slots=True)
class EngineResult:
    """Top-level orchestration result returned by the engine.

    Input contract:
    - `commit` may be absent when generation/validation fails.
    - `violations` aggregates validator findings.
    - `retries` is the number of extra generation attempts performed by engine.
    - `latency_ms` is end-to-end runtime in milliseconds.
    - `error` is optional terminal error code.
    - `meta` stores stable machine-readable telemetry.

    Output contract:
    - Single payload for CLI and logger.

    Side effects:
    - None.
    """

    commit: CommitMessage | None
    violations: list[str]
    retries: int
    latency_ms: int
    error: str | None
    meta: JSONDict = field(default_factory=dict)


@dataclass(slots=True)
class RunLogRecord:
    """Stable machine-readable run log schema.

    Input contract:
    - Every field must be JSON-serializable.

    Output contract:
    - Serialized as one JSON object per line in run logs.

    Side effects:
    - None.
    """

    schema_version: Literal["1.0"]
    timestamp_utc: str
    provider: str | None
    model: str | None
    strategy: str | None
    valid: bool
    violations: list[str]
    retries: int
    latency_ms: int
    word_count: int | None
