# ✅ **Recommended Schema (PostgreSQL)**

Below is the minimal but complete design:

---

## **1. `models` table**

Stores static metadata about each model.

```sql
CREATE TABLE models (
    id SERIAL PRIMARY KEY,
    model_name TEXT UNIQUE NOT NULL,
    provider TEXT,
    description TEXT,
    cost FLOAT,
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
    accuracy_score FLOAT,
    fluency_score FLOAT,
    latency_ms FLOAT,
    failure_count BIGINT DEFAULT 0,
    confidence FLOAT,
    tokens_per_query FLOAT,
    usage_count BIGINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE (model_id, domain_id)
);
```

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

```sql
INSERT INTO models (model_name, provider, cost) VALUES
('Qwen2.5-1.5B-Instruct', 'Qwen', 1.0),
('Qwen2.5-3B-Instruct', 'Qwen', 2.0),
('DeepSeek-R1-Distill-Qwen-1.5B', 'deepseek-ai', 1.0),
('TinyLlama-1.1B-Chat-v1.0', 'TinyLlama', 0.7),
('deepseek-math-7b-instruct', 'deepseek-ai', 5.0);
```

```sql
INSERT INTO domains (name) VALUES
('Math & Numerical Reasoning'),
('Logic & Deductive Reasoning'),
('General Knowledge'),
('Summarization'),
('Instruction Following'),
('Classification'),
('Code / Technical Reasoning'),
('Safety & Compliance'),
('Open-Ended Q&A / Conversational Quality'),
('Stress / Edge Cases');
```

.\cloud-sql-proxy.exe lab7-476520:us-central1:hyra --port=5433

\l

\c hyra

\dt

\d models

pg_dump -U postgres -h 127.0.0.1 -p 5433 -d hyra -F c -f hyra_backup.dump

pg_restore -U postgres -h 127.0.0.1 -p 5433 -d hyra_v2 hyra_backup.dump