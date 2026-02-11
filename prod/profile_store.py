"""Profile storage adapter for CLI defaults.

This module owns JSON persistence details so CLI never parses JSON directly.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MAIN_PROFILE_PATH = Path("config/main_profile.json")


def load_main_profile(path: Path = MAIN_PROFILE_PATH) -> dict[str, Any]:
    """Load persisted default profile data.

    Input contract:
    - `path` points to a JSON profile file.

    Output contract:
    - Returns dictionary payload. Empty dict when missing/invalid.

    Side effects:
    - Reads from filesystem.
    """

    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}
