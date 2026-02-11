"""Validation layer for commit message rules.

This module only validates and annotates commit payloads. It must not perform
retries, provider calls, or orchestration.
"""

from __future__ import annotations

import re
from typing import Any

from core.types import CommitMessage, ValidationResult


CONVENTIONAL_TYPE_PATTERN = re.compile(r"^[a-z]+$")


def _validate_presence(commit: CommitMessage) -> list[str]:
    """Validate required commit fields.

    Input contract:
    - `commit` is a normalized structured commit payload.

    Output contract:
    - Returns violation messages for missing required fields.

    Side effects:
    - None.
    """

    violations: list[str] = []
    if not commit.subject:
        violations.append("subject_missing")
    return violations


def _validate_subject_length(commit: CommitMessage) -> list[str]:
    """Validate conventional subject line length constraints.

    Input contract:
    - `commit.subject` may be `None`.

    Output contract:
    - Returns violations when subject is present but too long.

    Side effects:
    - None.
    """

    if not commit.subject:
        return []
    return ["subject_too_long"] if len(commit.subject) > 72 else []


def _compute_word_count(commit: CommitMessage) -> int:
    """Compute total word count for subject+body.

    Input contract:
    - `commit` fields may be `None`.

    Output contract:
    - Returns non-negative integer word count.

    Side effects:
    - None.
    """

    text = " ".join(part for part in [commit.subject, commit.body] if part)
    return len(text.split()) if text else 0


def _validate_length_constraints(
    word_count: int,
    constraints: dict[str, Any],
) -> list[str]:
    """Validate configured min/max word constraints.

    Input contract:
    - `word_count` must be non-negative.
    - `constraints` may include integer `min` and `max`.

    Output contract:
    - Returns violations when bounds are breached.

    Side effects:
    - None.
    """

    violations: list[str] = []
    min_words = constraints.get("min")
    max_words = constraints.get("max")

    if isinstance(min_words, int) and word_count < min_words:
        violations.append("word_count_below_min")
    if isinstance(max_words, int) and word_count > max_words:
        violations.append("word_count_above_max")
    return violations


def _validate_conventional_format(commit: CommitMessage) -> list[str]:
    """Validate conventional-commit compatible type format.

    Input contract:
    - `commit.type` may be `None`.

    Output contract:
    - Returns violations when provided type has invalid format.

    Side effects:
    - None.
    """

    if commit.type is None:
        return []
    if not CONVENTIONAL_TYPE_PATTERN.match(commit.type):
        return ["invalid_type_format"]
    return []


def validate_commit(commit: CommitMessage, constraints: dict[str, Any]) -> ValidationResult:
    """Run deterministic commit validation checks.

    Input contract:
    - `commit` is structured generator output.
    - `constraints` configures validation limits.

    Output contract:
    - Returns `ValidationResult` only; no retry or engine metadata.

    Side effects:
    - None.
    """

    violations: list[str] = []
    violations.extend(_validate_presence(commit))
    violations.extend(_validate_subject_length(commit))
    violations.extend(_validate_conventional_format(commit))

    word_count = _compute_word_count(commit)
    violations.extend(_validate_length_constraints(word_count, constraints))
    return ValidationResult(violations=violations, word_count=word_count)
