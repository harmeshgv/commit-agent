"""Provider registry mapping provider keys to adapter callables."""

from __future__ import annotations

from typing import Callable, TypedDict

from providers.groq_provider import generate as groq_generate
from providers.groq_provider import list_models as groq_models
from providers.ollama import generate as ollama_generate
from providers.ollama import list_models as ollama_models


class ProviderEntry(TypedDict):
    """Registry record for one provider backend.

    Input contract:
    - `generate`: callable accepting `(prompt, model)`.
    - `list_models`: callable returning available model ids.

    Output contract:
    - Uniform callable signatures across providers.

    Side effects:
    - None.
    """

    generate: Callable[[str, str], str]
    list_models: Callable[[], list[str]]


PROVIDERS: dict[str, ProviderEntry] = {
    "ollama": {
        "generate": ollama_generate,
        "list_models": ollama_models,
    },
    "groq": {
        "generate": groq_generate,
        "list_models": groq_models,
    },
}
