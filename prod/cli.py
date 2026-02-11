"""Production CLI entrypoint.

CLI loads structured production config and delegates execution to prod app.
"""

from __future__ import annotations

import argparse
from typing import Any

from rich.console import Console

from config.loader import load_prod_config
from prod.app import run_agent

console = Console()


def main() -> None:
    """Run one production execution from YAML configuration.

    Input contract:
    - `--config` points to production YAML path.
    - `--intent` is optional user intent text.
    - `--debug` toggles debug logs.

    Output contract:
    - Returns `None`; prints structured summary to terminal.

    Side effects:
    - Reads config file.
    - Runs engine through production app.
    - Writes summary to terminal.
    """

    parser = argparse.ArgumentParser(description="Commit Agent")
    parser.add_argument(
        "--config",
        default="config/prod.yaml",
        help="Path to production YAML config.",
    )
    parser.add_argument(
        "--intent",
        default=None,
        help="Optional user intent for commit generation.",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
    args = parser.parse_args()

    config = load_prod_config(args.config)
    result = run_agent(config=config, user_hint=args.intent, debug=args.debug)

    payload: dict[str, Any] = {
        "error": result.error,
        "retries": result.retries,
        "violations": result.violations,
        "meta": result.meta,
    }
    if result.commit:
        payload["subject"] = result.commit.subject
        payload["word_count"] = result.commit.word_count
        if result.commit.body:
            payload["body"] = result.commit.body
    console.print(payload)


if __name__ == "__main__":
    main()
