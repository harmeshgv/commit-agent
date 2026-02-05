import requests
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def list_models():
    r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=10)
    r.raise_for_status()

    models = []
    for m in r.json().get("models", []):
        # name looks like: llama3:latest
        models.append(m["name"])
    return models


def generate(prompt, model):
    payload = {"model": model, "prompt": prompt, "stream": False}

    r = requests.post(f"{OLLAMA_HOST}/api/generate", json=payload, timeout=60)
    r.raise_for_status()

    return r.json()["response"]
