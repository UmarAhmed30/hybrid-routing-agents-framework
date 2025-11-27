import os
import sys
from pathlib import Path
import time
import json
import requests
import math
import psycopg2
from psycopg2.extras import RealDictCursor

sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.evaluator import judge_accuracy, judge_fluency
from db.client import get_connection

VLLM_URL = "http://localhost:8000/v1/completions"

MODELS = [
    # "Qwen2.5-1.5B-Instruct",
    # "Qwen2.5-3B-Instruct",
    # "DeepSeek-R1-Distill-Qwen-1.5B",
    # "TinyLlama-1.1B-Chat-v1.0",
    # "deepseek-math-7b-instruct",
    # "Phi-3-mini-4k-instruct",
    "Qwen2.5-0.5B-Instruct"
]

def get_model_row(conn, model_name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM models WHERE model_name = %s", (model_name,))
    row = cur.fetchone()
    if not row:
        raise Exception(f"Model '{model_name}' not found in models table.")
    return row


def get_existing_metrics(conn, model_id, domain_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT *
        FROM model_metrics
        WHERE model_id = %s AND domain_id = %s
    """, (model_id, domain_id))
    return cur.fetchone()


def insert_new_metrics(
    conn, model_id, domain_id,
    accuracy, fluency, latency_ms,
    confidence, tokens, failure_count
):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO model_metrics
        (model_id, domain_id, accuracy_score, fluency_score, latency_ms,
        confidence, tokens_per_query, usage_count, failure_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 1, %s)
    """, (model_id, domain_id, accuracy, fluency, latency_ms, confidence, tokens, failure_count))
    conn.commit()


def update_metrics_rolling(
    conn, existing, model_id, domain_id,
    new_accuracy, new_fluency, new_latency,
    new_confidence, new_tokens, failure_inc
):

    old_usage = existing["usage_count"]
    new_usage = old_usage + 1

    accuracy = (existing["accuracy_score"] * old_usage + new_accuracy) / new_usage
    fluency  = (existing["fluency_score"] * old_usage + new_fluency) / new_usage
    latency  = (existing["latency_ms"] * old_usage + new_latency) / new_usage
    conf     = (existing["confidence"] * old_usage + new_confidence) / new_usage
    tokens   = (existing["tokens_per_query"] * old_usage + new_tokens) / new_usage

    cur = conn.cursor()
    cur.execute("""
        UPDATE model_metrics
        SET accuracy_score = %s,
            fluency_score = %s,
            latency_ms = %s,
            confidence = %s,
            tokens_per_query = %s,
            usage_count = usage_count + 1,
            failure_count = failure_count + %s,
            last_updated = NOW()
        WHERE model_id = %s AND domain_id = %s
    """, (accuracy, fluency, latency, conf, tokens, failure_inc,model_id, domain_id))
    conn.commit()

def compute_confidence(choice):
    if "logprobs" not in choice or choice["logprobs"] is None:
        return 0.0
    logprobs = choice["logprobs"].get("token_logprobs", [])
    if not logprobs:
        return 0.0
    avg_logprob = sum(logprobs) / len(logprobs)
    return math.exp(avg_logprob)

def query_model(model_name, provider, prompt):
    payload = {
        "model": f"{provider}/{model_name}",
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


def benchmark(conn, model_name, domain_id, question, expected_answer):
    model_row = get_model_row(conn, model_name)
    model_id = model_row["id"]
    provider = model_row["provider"]

    t1 = time.time()
    result = query_model(model_name, provider, question)
    t2 = time.time()

    latency_ms = (t2 - t1) * 1000
    response_text = result["response_text"]

    accuracy = judge_accuracy(domain_id, question, expected_answer, response_text)
    fluency = judge_fluency(response_text)
    tokens = result["total_tokens"]
    confidence = result["confidence"]
    failures = result["failed"]

    existing = get_existing_metrics(conn, model_id, domain_id)

    if existing is None:
        insert_new_metrics(
            conn, model_id, domain_id,
            accuracy, fluency, latency_ms,
            confidence, tokens, failures
        )
    else:
        update_metrics_rolling(
            conn, existing, model_id, domain_id,
            accuracy, fluency, latency_ms,
            confidence, tokens, failures
        )


def main():
    conn = get_connection()
    eval_set = json.load(open("eval_set.json"))

    for item in eval_set:
        domain_id = item["domain"]
        q = item["q"]
        a = item["a"]

        for model in MODELS:
            try:
                benchmark(conn, model, domain_id, q, a)
            except Exception as e:
                print(f"[ERROR] Benchmarking {model} failed for question {q}: {e}")
                continue
        time.sleep(20)

    conn.close()
    print("[DONE] Metrics updated in PostgreSQL.")


if __name__ == "__main__":
    t1 = time.time()
    main()
    print("[TOTAL TIME]", time.time() - t1)
