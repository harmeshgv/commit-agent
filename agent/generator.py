from pathlib import Path
from providers.ollama import generate as ollama_generate

PROMPT_DIR = Path("prompting")


def load_prompt(strategy):
    path = PROMPT_DIR / f"{strategy}.txt"
    return path.read_text()


def generate_commit(context, strategy, provider, model, user_hint):
    prompt_template = load_prompt(strategy)

    prompt = prompt_template.format(
        diff=context["diff"], status=context["status"], user_hint=user_hint or "None"
    )

    response = ollama_generate(prompt, model=model)

    return {
        "subject": response.strip().split("\n")[0],
        "body": "\n".join(response.strip().split("\n")[1:]) or None,
        "meta": {
            "strategy": strategy,
            "provider": provider,
            "model": model,
        },
    }
