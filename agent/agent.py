from agent.analyzer import analyze_diff
from agent.generator import generate_commit
from agent.validator import validate_commit


def run_agent(strategy, provider, model, user_hint):
    context = analyze_diff()

    result = generate_commit(
        context=context,
        strategy=strategy,
        provider=provider,
        model=model,
        user_hint=user_hint,
    )

    validated = validate_commit(result)

    print("\nProposed commit:\n")
    print(validated["subject"])
    if validated.get("body"):
        print("\n" + validated["body"])
