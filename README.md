# Commit Agent

Experimental standalone AI agent for generating structured, consistent git commit messages from diffs. Built for prompt, agent, and framework experimentation.

## Overview

This project is a Python-based AI agent that automates the creation of git commit messages. It analyzes the git diff and status to generate a commit message that follows the Conventional Commits specification. The agent is designed to be a framework for experimenting with different large language models (LLMs), prompt strategies, and configurations.

## Features

-   **Conventional Commits:** Generates commit messages that adhere to the Conventional Commits specification.
-   **Multiple Providers:** Supports multiple LLM providers, including Groq and Ollama.
-   **Configurable:** Easily configurable through YAML files for both production and lab modes.
-   **Lab Mode:** A dedicated lab mode for running experiments and comparing the performance of different models and strategies.
-   **Colored Logging:** Informative and visually appealing colored logs for both normal and debug modes.

## Getting Started

### Prerequisites

-   Python 3.10+
-   `uv` installed (`https://docs.astral.sh/uv/`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/commit-agent.git
    cd commit-agent
    ```

2.  **Create environment and install dependencies with `uv`:**
    ```bash
    uv venv
    uv sync
    ```

3.  **Install development tools (optional):**
    ```bash
    uv sync --extra dev
    ```
4.  **Set up environment variables:**
    -   Create a `.env` file in the root of the project.
    -   Add your `GROQ_API_KEY` to the `.env` file:
        ```
        GROQ_API_KEY=your-groq-api-key
        ```

## Usage

### Production Mode

To run the agent in production mode, use the following command:

```bash
uv run python -m prod.cli
```

This will use the configuration from `config/prod.yaml` to generate a commit message for the current git diff.

### Lab Mode

To run the agent in lab mode, which is designed for experiments, you can use the `run_lab.py` script:

```bash
uv run python run_lab.py
```

This will run the batch experiment defined in `config/lab.yaml` and save the results to `eval/runs.jsonl`.

To see a comparison of the lab run results, you can use the `show_comparison.py` script:

```bash
uv run python show_comparison.py
```

## Evaluation

The score for each configuration is calculated using the following formula:

```
score = (valid_rate * 100.0) - (retry_rate * 20.0) - (average_latency / 1000.0)
```

-   **`valid_rate`**: The percentage of runs that produced a valid commit message.
-   **`retry_rate`**: The average number of retries per run.
-   **`average_latency`**: The average time (in milliseconds) taken to generate a commit message.

This formula prioritizes correctness (higher `valid_rate`), followed by stability (lower `retry_rate`), and then efficiency (lower `average_latency`).

| Model                               | Provider | Valid Rate | Retry Rate | Avg Latency (ms) | Score  |
| ----------------------------------- | -------- | ---------- | ---------- | ---------------- | ------ |
| llama-3.3-70b-versatile (zero_shot) | groq     | 0.67       | 1.50       | 939              | 35.73  |
| llama-3.1-8b-instant (structured)   | groq     | 0.50       | 1.67       | 745              | 15.92  |
| llama-3.3-70b-versatile (structured)  | groq     | 0.50       | 2.00       | 1624             | 8.38   |
| llama-3.1-8b-instant (zero_shot)    | groq     | 0.33       | 2.67       | 588              | -20.59 |
| llama3 (zero_shot)                  | ollama   | 0.00       | 3.00       | 9                | -60.01 |

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

When contributing, please follow these guidelines:

1.  **Fork the repository** and create your branch from `main`.
2.  **Install the development dependencies** (`uv sync --extra dev`).
3.  **Make your changes** and add tests for them.
4.  **Run the tests** (`uv run pytest`).
5.  **Lint your code** (`uv run ruff check .`).
6.  **Format your code** (`uv run ruff format .`).
7.  **Submit a pull request** with a clear description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
