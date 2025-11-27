import math
import requests


URL = "http://localhost:8000/v1/completions" # TODO: Make configurable


def compute_confidence(choice):
    if "logprobs" not in choice or choice["logprobs"] is None:
        return 0.0
    logprobs = choice["logprobs"].get("token_logprobs", [])
    if not logprobs:
        return 0.0
    avg_logprob = sum(logprobs) / len(logprobs)
    return math.exp(avg_logprob)


def run(model_name, provider, prompt):
    payload = {
        "model": f"{provider}/{model_name}",
        "prompt": prompt,
        "max_tokens": 128,
        "temperature": 0.2,
        "logprobs": 1
    }
    try:
        resp = requests.post(URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        confidence = compute_confidence(data["choices"][0])
        text = data["choices"][0]["text"].strip()
        usage = data.get("usage", {})
        return {
            "response_text": text,
            "confidence": confidence,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "failed": 0
        }
    except Exception as e:
        print(f"[ERROR] {model_name} failed: {e}")
        return {
            "response_text": "",
            "confidence": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "failed": 1
        }
