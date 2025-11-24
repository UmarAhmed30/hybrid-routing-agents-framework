Here is a **clean, scalable, production-quality DB schema** for storing **per-model, per-domain, per-metric** performance values — including *accuracy, confidence, latency, cost, usage_count*, etc.

This schema works for:

✔ Routing / model selection
✔ Tracking metrics over time
✔ Storing benchmark datasets per domain
✔ Aggregating scores dynamically
✔ Updating metrics after each query

---

# ✅ **Recommended Schema (PostgreSQL)**

Below is the minimal but complete design:

---

## **1. `models` table**

Stores static metadata about each model.

```sql
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    model_name TEXT UNIQUE NOT NULL,
    provider TEXT,                -- e.g. "openai", "google", "ollama"
    context_length INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## **2. `domains` table**

Defines domains such as MATH, CODING, MEDICAL, GENERAL, etc.

```sql
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);
```

---

## **3. `domain_benchmarks` table** (optional but highly recommended)

Stores gold-standard dataset per domain.

```sql
CREATE TABLE domain_benchmarks (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id),
    prompt TEXT NOT NULL,
    expected_answer TEXT,
    difficulty INTEGER DEFAULT 1,
    tags TEXT[]
);
```

Use these prompts to measure accuracy.

---

## **4. `model_metrics` table (LATEST metrics)**

Stores the **latest aggregated metrics** per model per domain.

```sql
CREATE TABLE model_metrics (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id),
    domain_id INTEGER REFERENCES domains(id),

    accuracy FLOAT,              -- computed from benchmark results
    latency_ms FLOAT,
    cost_per_query FLOAT,
    failure_rate FLOAT,
    confidence FLOAT,
    variance FLOAT,
    avg_output_length FLOAT,
    tokens_per_query FLOAT,

    usage_count BIGINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),

    UNIQUE (model_id, domain_id)
);
```

This matches what you showed in your screenshot.

---

## **5. `model_metric_events` table (raw logs)**

This is *critical*: every query produces data that is later aggregated into `model_metrics`.

```sql
CREATE TABLE model_metric_events (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id),
    domain_id INTEGER REFERENCES domains(id),

    latency_ms FLOAT,
    tokens_input INTEGER,
    tokens_output INTEGER,
    cost FLOAT,
    success BOOLEAN,
    confidence FLOAT,
    
    -- if benchmark query:
    benchmark_id INTEGER REFERENCES domain_benchmarks(id),
    correct BOOLEAN,

    created_at TIMESTAMP DEFAULT NOW()
);
```

You compute aggregated metrics from this table.

---

# 🎯 **How to Compute Metrics**

## **1. Accuracy (per model per domain)**

Accuracy is computed using **benchmark queries only**:

```sql
SELECT 
    AVG(CASE WHEN correct THEN 1 ELSE 0 END) AS accuracy
FROM model_metric_events
WHERE model_id = $MODEL_ID AND domain_id = $DOMAIN_ID AND benchmark_id IS NOT NULL;
```

---

## **2. Latency**

```sql
SELECT AVG(latency_ms)
FROM model_metric_events
WHERE model_id=$MODEL_ID AND domain_id=$DOMAIN_ID;
```

---

## **3. Confidence**

Use mean or weighted mean:

```sql
SELECT AVG(confidence)
FROM model_metric_events
WHERE model_id=$MODEL_ID AND domain_id=$DOMAIN_ID;
```

---

## **4. Failure Rate**

```sql
SELECT 1 - AVG(CASE WHEN success THEN 1 ELSE 0 END)
FROM model_metric_events
WHERE model_id=$MODEL_ID AND domain_id=$DOMAIN_ID;
```

---

## **5. Variance**

```sql
SELECT VARIANCE(latency_ms)
FROM model_metric_events
WHERE model_id=$MODEL_ID AND domain_id=$DOMAIN_ID;
```

---

## **6. Usage Count**

```sql
SELECT COUNT(*)
FROM model_metric_events
WHERE model_id=$MODEL_ID AND domain_id=$DOMAIN_ID;
```

---

# 🧠 **Flow of a Real Query**

Every time a user query occurs:

### **Router → Inference Agent → Verifier Agent**

You produce a log entry like:

```json
{
  "model_id": 12,
  "domain": "coding",
  "latency_ms": 720.4,
  "tokens_input": 140,
  "tokens_output": 201,
  "success": true,
  "confidence": 0.82,
  "cost": 0.0002
}
```

This becomes a row in `model_metric_events`.

A background cron job recomputes aggregates and updates `model_metrics`.

---

# ⭐ Final Schema Diagram (simplified)

```
models 1---* model_metrics *---1 domains
models 1---* model_metric_events *---1 domains
domains 1---* domain_benchmarks
domain_benchmarks 1---* model_metric_events
```

---

# If you want, I can also generate:

✅ Full SQL migrations
✅ SQLAlchemy ORM models
✅ FastAPI API endpoints (`POST metrics/update`, `GET model-ranking`, etc.)
✅ Benchmark runner script to populate metrics
✅ A dashboard (React or Streamlit)

Would you like those?
