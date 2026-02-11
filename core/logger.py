"""Logging utilities for machine-readable run records.

Logger functions are side-effect-only and must never control flow decisions.
"""

from __future__ import annotations

import datetime
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from core.types import EngineResult, RunLogRecord


def debug_log(enabled: bool, event: str, payload: dict[str, Any]) -> None:
    """Emit a structured debug log line when enabled.

    Input contract:
    - `enabled`: toggles emission.
    - `event`: short event name.
    - `payload`: JSON-serializable details.

    Output contract:
    - No return value.

    Side effects:
    - Writes one JSON line to stdout when enabled.
    """

    if not enabled:
        return
    record = {"event": event, "payload": payload}
    print(json.dumps(record, sort_keys=True))


class RunLogger:
    """Append `EngineResult` records to JSONL using a stable schema.

    Input contract:
    - `log_path` is a writable file path.

    Output contract:
    - Produces one JSON object per line.

    Side effects:
    - Creates parent directories and writes to filesystem.
    """

    def __init__(self, log_path: str = "eval/runs.jsonl") -> None:
        """Initialize logger with target JSONL path.

        Input contract:
        - `log_path` is relative or absolute file path string.

        Output contract:
        - Ready-to-use `RunLogger` instance.

        Side effects:
        - None.
        """

        self.log_path = Path(log_path)

    def log_run(self, result: EngineResult) -> None:
        """Serialize and append one result row.

        Input contract:
        - `result` must conform to `EngineResult`.

        Output contract:
        - No return value.

        Side effects:
        - Appends one JSON line to configured file path.
        """

        payload = self._serialize_result(result)
        self._append_jsonl(payload)

    def _serialize_result(self, result: EngineResult) -> dict[str, Any]:
        """Convert `EngineResult` into stable schema payload.

        Input contract:
        - `result` contains execution metadata and optional commit.

        Output contract:
        - JSON-serializable dictionary with fixed keys.

        Side effects:
        - None.
        """

        record = RunLogRecord(
            schema_version="1.0",
            timestamp_utc=datetime.datetime.now(datetime.UTC).isoformat(),
            provider=result.meta.get("provider"),
            model=result.meta.get("model"),
            strategy=result.meta.get("strategy"),
            valid=len(result.violations) == 0 and result.error is None,
            violations=list(result.violations),
            retries=result.retries,
            latency_ms=result.latency_ms,
            word_count=result.commit.word_count if result.commit else None,
        )
        return asdict(record)

    def _append_jsonl(self, payload: dict[str, Any]) -> None:
        """Append one payload object to JSONL file.

        Input contract:
        - `payload` is JSON-serializable mapping.

        Output contract:
        - No return value.

        Side effects:
        - Writes to `self.log_path`.
        """

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, sort_keys=True) + "\n")
