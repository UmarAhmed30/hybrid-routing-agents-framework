import sys
import time
import asyncio
from pathlib import Path
from functools import lru_cache

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from langfuse_config.tracer import langfuse

from utils.router.config import load_config
from utils.gemini.client import GeminiClient

from db.client import get_connection

from agents.domain_classifier import classify as raw_classify
from agents.scorer import get_best_model
from agents.advanced_verifier import verify as advanced_verify
from agents.inference import run

from evaluation.evaluator import judge_fluency

config = load_config()
gemini_client = GeminiClient()

@lru_cache(maxsize=5000)
def classify(prompt: str):
    return raw_classify(prompt)


def update_metrics(conn, model_id, domain_id, metrics, passed):
    penalties = config["penalties"]
    multiplier = penalties["verification_fail_multiplier"]

    cur = conn.cursor()
    cur.execute("""
        SELECT accuracy_score, fluency_score, latency_ms, confidence,
        tokens_per_query, usage_count, failure_count
        FROM model_metrics
        WHERE model_id = %s AND domain_id = %s;
    """, (model_id, domain_id))
    existing = cur.fetchone()

    new_accuracy  = metrics["accuracy"]
    new_fluency   = metrics["fluency"]
    new_latency   = metrics["latency_ms"]
    new_conf      = metrics["confidence"]
    new_tokens    = metrics["tokens"]
    new_failures  = 0

    if passed:
        # reward model by updating rolling averages
        old_acc = existing["accuracy_score"]
        old_flu = existing["fluency_score"]
        old_lat = existing["latency_ms"]
        old_conf= existing["confidence"]
        old_tokens = existing["tokens_per_query"]
        old_usage = existing["usage_count"]
        old_failures = existing["failure_count"]

        new_usage = old_usage + 1
        updated_acc   = (old_acc   * old_usage + new_accuracy) / new_usage
        updated_flu   = (old_flu   * old_usage + new_fluency) / new_usage
        updated_lat   = (old_lat   * old_usage + new_latency) / new_usage
        updated_conf  = (old_conf  * old_usage + new_conf) / new_usage
        updated_tokens= (old_tokens* old_usage + new_tokens) / new_usage
        cur.execute("""
            UPDATE model_metrics
            SET accuracy_score   = %s,
                fluency_score    = %s,
                latency_ms       = %s,
                confidence       = %s,
                tokens_per_query = %s,
                usage_count      = usage_count + 1,
                last_updated     = NOW()
            WHERE model_id = %s AND domain_id = %s;
        """, (
            updated_acc, updated_flu, updated_lat,
            updated_conf, updated_tokens,
            model_id, domain_id
        ))
    else:
        # penalize model by multiplying existing scores
        cur.execute("""
            UPDATE model_metrics
            SET accuracy_score = accuracy_score * %s,
                fluency_score  = fluency_score  * %s,
                confidence     = confidence     * %s,
                failure_count  = failure_count + 1,
                last_updated   = NOW()
            WHERE model_id = %s AND domain_id = %s;
        """, (
            multiplier, multiplier, multiplier,
            model_id, domain_id
        ))
    conn.commit()
    cur.close()


def route(prompt, event_callback=None):
    trace = langfuse.start_span(
        name="route",
        input=prompt,
        metadata={"prompt": prompt}
    )

    def log_event(message):
        print(message)
        if event_callback:
            event_callback(message)

    # Domain Classification
    domain = classify(prompt)
    log_msg = f"[ROUTER] Classified domain = {domain}"
    log_event(log_msg)
    domain_span = trace.start_span(
        name="domain_classification",
        input=prompt
    )
    domain_span.update(output=domain)
    domain_span.end()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM domains WHERE name = %s;", (domain,))
    row = cur.fetchone()
    if not row:
        raise Exception(f"Unknown domain '{domain}'")
    domain_id = row['id']

    # Model Selection
    model_id = get_best_model(domain_id, config)
    cur.execute("SELECT model_name, provider FROM models WHERE id = %s", (model_id,))
    row = cur.fetchone()
    model_name, provider = row['model_name'], row['provider']
    log_msg = f"[ROUTER] Selected model = {model_name}"
    log_event(log_msg)
    model_span = trace.start_span(
        name="model_selection"
    )
    model_span.update(output={"model_id": model_id, "model_name": model_name, "provider": provider})
    model_span.end()


    # Inference
    log_msg = f"[ROUTER] Starting inference with {model_name}..."
    log_event(log_msg)
    t1 = time.time()
    inference_span = trace.start_span(name="inference", input={"prompt": prompt, "model": model_name})
    result = run(model_name, provider, prompt)
    t2 = time.time()


    latency_ms = (t2 - t1) * 1000
    inference_span.update(output=result)
    inference_span.end()
    
    log_msg = f"[ROUTER] Inference completed in {latency_ms:.2f}ms"
    log_event(log_msg)

    text = result["response_text"]
    confidence = result["confidence"]
    tokens = result["total_tokens"]
    
    log_msg = f"[ROUTER] Response: {text[:100]}..." if len(text) > 100 else f"[ROUTER] Response: {text}"
    log_event(log_msg)

    print(f"[INFERENCE] Total inference time: {latency_ms:.2f} ms")

    async def evaluate_parallel():
        task_verify = asyncio.create_task(
            advanced_verify(prompt, text)
        )
        task_fluency = asyncio.create_task(
            judge_fluency(text)
        )
        verify_result = await task_verify
        fluency_score = await task_fluency
        return verify_result, fluency_score

    verify_span = trace.start_span(name="verification_and_fluency")
    verify_result, fluency_score = asyncio.run(evaluate_parallel())

    accuracy = verify_result["accuracy"]
    fluency = fluency_score
    passed = verify_result["passed"]
    verify_span.update(
        output={
            "accuracy": accuracy,
            "fluency": fluency,
            "passed": passed
        }
    )
    verify_span.end()

    metrics = {
        "accuracy": accuracy,
        "fluency": fluency,
        "confidence": confidence,
        "latency_ms": latency_ms,
        "tokens": tokens
    }

    eval_span = trace.start_span(name="metrics_summary")
    eval_span.update(output=metrics)
    eval_span.end()


    # Update metrics (reward or penalize)
    update_metrics(conn, model_id, domain_id, metrics, passed)

    trace.end()

    conn.close()

    return {
        "domain": domain,
        "model": model_name,
        "provider": provider,
        "output": text,
        "metrics": metrics,
        "verified": passed
    }


if __name__ == "__main__":
    t1 = time.time()
    result = route("What is a vowel?")
    t2 = time.time()
    print(f"[ROUTER] Total routing time: {(t2 - t1)*1000:.2f} ms")
    print(result)
