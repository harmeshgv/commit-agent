from rich.console import Console
from rich.prompt import Prompt
from agent.agent import run_agent
from providers.registry import PROVIDERS

console = Console()


def select_option(title, options):
    console.print(f"\n[bold]{title}[/bold]")
    for i, opt in enumerate(options, 1):
        console.print(f"  {i}) {opt}")
    choice = Prompt.ask("Select", choices=[str(i) for i in range(1, len(options) + 1)])
    return options[int(choice) - 1]


def main():
    strategy = select_option(
        "Prompting strategy", ["zero-shot", "structured", "few-shot"]
    )

    provider = select_option("Model provider", list(PROVIDERS.keys()))

    try:
        models = PROVIDERS[provider]["list_models"]()
    except Exception:
        console.print("[red]Ollama not running or unreachable[/red]")
        return

    if not models:
        console.print("[red]No models found for this provider[/red]")
        return

    model = select_option(f"Available models for {provider}", models)

    user_hint = Prompt.ask("Extra intent (optional)", default="")

    run_agent(
        strategy=strategy,
        provider=provider,
        model=model,
        user_hint=user_hint or None,
    )


if __name__ == "__main__":
    main()
