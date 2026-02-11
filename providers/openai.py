"""OpenAI provider adapter skeleton.

Input contract:
- Expose `list_models()` and `generate(prompt, model)` compatible with registry.

Output contract:
- Return model IDs and raw generated text.

Side effects:
- Network I/O when implemented.
"""

from __future__ import annotations


def list_models() -> list[str]:
    """List OpenAI model identifiers.

    Input contract:
    - None.

    Output contract:
    - Returns list of model IDs.

    Side effects:
    - None in skeleton form.
    """

    raise NotImplementedError("OpenAI provider is not implemented.")


def generate(prompt: str, model: str) -> str:
    """Generate response text using an OpenAI model.

    Input contract:
    - `prompt` must be fully prepared prompt text.
    - `model` must be valid provider model id.

    Output contract:
    - Returns raw text response.

    Side effects:
    - None in skeleton form.
    """

    _ = (prompt, model)
    raise NotImplementedError("OpenAI provider is not implemented.")
