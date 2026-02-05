from providers import ollama

# later: groq, openai

PROVIDERS = {
    "ollama": {
        "list_models": ollama.list_models,
        "generate": ollama.generate,
    },
    # "groq": {...}
}
