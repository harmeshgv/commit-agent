"""Provider adapter contracts.

Providers are transport adapters only. They must not perform prompt-template
selection or business-policy decisions.
"""

from __future__ import annotations

from typing import Protocol


class Provider(Protocol):
    """Provider contract used by the registry.

    Input contract:
    - Implementations must expose `list_models` and `generate`.

    Output contract:
    - `list_models` returns model identifiers.
    - `generate` returns raw model text.

    Side effects:
    - Typically network I/O.
    """

    def list_models(self) -> list[str]:
        """Return available model identifiers for this provider."""

    def generate(self, prompt: str, model: str) -> str:
        """Generate text for a fully-prepared prompt payload."""
