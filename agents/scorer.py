import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from db.client import get_connection

conn = get_connection()

def normalize_latency(latency_ms, min_ms=300, max_ms=1500):
    # 1.0 = fast, 0.0 = slow
    latency_clamped = max(min(latency_ms, max_ms), min_ms)
    return (max_ms - latency_clamped) / (max_ms - min_ms)

def compute_score(row, weights):
    lat_norm = normalize_latency(row["latency_ms"])
    quality_score = (
        weights["accuracy"]   * row["accuracy_score"] +
        weights["fluency"]    * row["fluency_score"] +
        weights["confidence"] * row["confidence"] +
        weights["latency"]    * lat_norm
    )
    cost_factor = 1.0 / (1.0 + row["cost"])
    return quality_score * cost_factor


def get_best_model(domain_id, config):
    weights = config["weights"]
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            m.id, m.model_name, m.cost,
            COALESCE(mm.accuracy_score, 0.5) AS accuracy_score,
            COALESCE(mm.fluency_score, 0.5) AS fluency_score,
            COALESCE(mm.confidence, 0.5) AS confidence,
            COALESCE(mm.latency_ms, 1000) AS latency_ms
        FROM models m
        LEFT JOIN model_metrics mm
            ON mm.model_id = m.id AND mm.domain_id = %s;
    """, (domain_id,))
    rows = cur.fetchall()
    scored = []
    for row in rows:
        model_id = row["id"]
        model_name = row["model_name"]
        metrics = {
            "accuracy_score": row["accuracy_score"],
            "fluency_score": row["fluency_score"],
            "confidence": row["confidence"],
            "latency_ms": row["latency_ms"],
            "cost": row["cost"]
        }
        score = compute_score(metrics, weights)
        scored.append((score, model_id, model_name))
    scored.sort(reverse=True, key=lambda x: x[0])
    best_score, best_model_id, best_model_name = scored[0]
    print(f"[SCORER] Best model = {best_model_name} (score={best_score:.4f})")
    return best_model_id

def main():
    domain_id = 1
    config = {
        "weights": {
            "accuracy": 0.50,
            "confidence": 0.20,
            "fluency": 0.20,
            "latency": 0.10,
        },
        "penalties": {
            "verification_fail_multiplier": 0.85
        }
    }
    get_best_model(domain_id, config)

if __name__ == "__main__":
    main()
