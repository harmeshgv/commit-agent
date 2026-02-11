"""Production application orchestration adapters."""

from __future__ import annotations

from config.loader import ProdConfig
from core.engine import run_once
from core.types import EngineResult


def run_agent(config: ProdConfig, user_hint: str | None, debug: bool = False) -> EngineResult:
    """Execute one production run from structured configuration.

    Input contract:
    - `config` is loaded from `config/prod.yaml`.
    - `user_hint` is optional intent text supplied by caller.
    - `debug` controls debug logging in the engine.

    Output contract:
    - Returns one `EngineResult` from primary or fallback target.

    Side effects:
    - Invokes engine pipeline (analyzer/generator/provider/validator).
    """

    return run_once(config=config, intent=user_hint, debug=debug)
