import os
import sys
from pathlib import Path
import time
import json
import requests
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.evaluator import judge_accuracy, judge_fluency

VLLM_URL = "http://localhost:8000/v1/completions"
MODELS = [
    "Qwen/Qwen2.5-1.5B-Instruct",
    # "Qwen/Qwen2.5-3B-Instruct",
    # "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    # "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    # "deepseek-ai/deepseek-math-7b-instruct"
]

results = []

def load_eval_set():
    with open("eval_set.json", "r") as f:
        data = json.load(f)
    return data

def compute_confidence(choice):
    if "logprobs" not in choice or choice["logprobs"] is None:
        return None
    logprobs = choice["logprobs"].get("token_logprobs", [])
    if not logprobs:
        return None
    avg_logprob = sum(logprobs) / len(logprobs)
    return math.exp(avg_logprob)

def query_model(model_name, prompt):
    payload = {
        "model": model_name,
        "prompt": prompt,
        "max_tokens": 128,
        "temperature": 0.2,
        "logprobs": 1
    }
    try:
        resp = requests.post(VLLM_URL, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        confidence = compute_confidence(data["choices"][0])
        text = data["choices"][0]["text"].strip()
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        return {
            "response_text": text,
            "confidence": confidence,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    except Exception as e:
        print(f"[ERROR] Model {model_name} failed: {e}")
        return {
            "response_text": "",
            "confidence": 0.0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }

def benchmark(domain, question, expected_answer):
    for model in MODELS:
        try:
            t1 = time.time()
            result = query_model(model, question)
            t2 = time.time()

            response_text = result["response_text"]
            latency_ms = (t2 - t1) * 1000

            accuracy = judge_accuracy(domain, question, expected_answer, response_text)
            fluency = judge_fluency(response_text)

            prompt_tokens = result["prompt_tokens"]
            completion_tokens = result["completion_tokens"]
            total_tokens = result["total_tokens"]
            confidence = result["confidence"]
            tokens_per_query = total_tokens

            results.append({
                "model_name": model,
                "domain": domain,
                "question": question,
                "expected_answer": expected_answer,
                "model_response": response_text,
                "accuracy_score": accuracy,
                "fluency_score": fluency,
                "latency_ms": latency_ms,
                "tokens_per_query": tokens_per_query,
                "cost": 0.0,
                "failure_count": 1,
                "confidence": confidence,
                "usage_count": 1,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            time.sleep(10)
        except Exception as e:
            print(f"[ERROR] Benchmarking model {model} failed for {question}: {e}")
            continue

def main():
    eval_set = load_eval_set()
    for item in eval_set:
        benchmark(domain=item["domain"], question=item["q"], expected_answer=item["a"])
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("[DONE] Saved metrics to results.json")


if __name__ == "__main__":
    t1 = time.time()
    main()
    print(f"[TOTAL TIME] {time.time() - t1} seconds")
