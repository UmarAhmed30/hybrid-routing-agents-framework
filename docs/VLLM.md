# vLLM CPU Environment Setup

This document provides model options, recommended parameters, Docker build/run commands, and example `curl` requests for testing inference through the OpenAI-compatible vLLM server.

---

## 📌 Supported Models & Parameters

| Model Name | Parameter for `--model` | Size | DType | Notes |
|-----------|--------------------------|------|--------|-------|
| **Qwen2.5 1.5B Instruct** | `Qwen/Qwen2.5-1.5B-Instruct` | 1.5B | bfloat16 | Good general-purpose CPU model |
| **Qwen2.5 3B Instruct** | `Qwen/Qwen2.5-3B-Instruct` | 3B | bfloat16 | Larger, better reasoning |
| **DeepSeek Math 1.5B** | `Deepseek-AI/DeepSeek-Math-1.5B` | 1.5B | bfloat16 | Math/logic specialized |
| **TinyLlama Chat** | `TinyLlama/TinyLlama-1.1B-Chat-v1.0` | 1.1B | bfloat16 | Very lightweight |

---

## 🛠️ Build the Docker Image

```bash
docker build -f docker/Dockerfile.cpu \
  --build-arg VLLM_CPU_AVX512BF16=false \
  --build-arg VLLM_CPU_AVX512VNNI=false \
  --build-arg VLLM_CPU_DISABLE_AVX512=false \
  --tag vllm-cpu-env \
  --target vllm-openai .

```

---

## 📌 Supported Models & Parameters

Below are one-command Docker runs for each model.

### 1️⃣ Qwen 2.5 – 1.5B Instruct

#### Run Server

Linux/WSL:

```bash
docker run --rm --security-opt seccomp=unconfined \
  --cap-add SYS_NICE --shm-size=4g -p 8000:8000 \
  vllm-cpu-env --model=Qwen/Qwen2.5-1.5B-Instruct --dtype=bfloat16
```

Windows:

```bash
docker run --rm --security-opt seccomp=unconfined --cap-add SYS_NICE --shm-size=4g -p 8000:8000 vllm-cpu-env --model=Qwen/Qwen2.5-1.5B-Instruct --dtype=bfloat16
```

#### Example Curl

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-1.5B-Instruct",
    "prompt": "Q: What is 2+2?\nA:",
    "max_tokens": 100,
    "logprobs": 5
}'
```

### 2️⃣ Qwen 2.5 – 3B Instruct

#### Run Server

Linux/WSL:

```bash
docker run --rm --security-opt seccomp=unconfined \
  --cap-add SYS_NICE --shm-size=4g -p 8000:8000 \
  vllm-cpu-env --model=Qwen/Qwen2.5-3B-Instruct --dtype=bfloat16
```

Windows:

```bash
docker run --rm --security-opt seccomp=unconfined --cap-add SYS_NICE --shm-size=4g -p 8000:8000 vllm-cpu-env --model=Qwen/Qwen2.5-3B-Instruct --dtype=bfloat16
```

#### Example Curl

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-3B-Instruct",
    "prompt": "Q: What is 2+2?\nA:",
    "max_tokens": 100
}'
```

### 3️⃣ DeepSeek-R1-Distill-Qwen-1.5B

#### Run Server

Linux/WSL:

```bash
docker run --rm --security-opt seccomp=unconfined \
  --cap-add SYS_NICE --shm-size=4g -p 8000:8000 \
  vllm-cpu-env --model=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --dtype=bfloat16
```

Windows:

```bash
docker run --rm --security-opt seccomp=unconfined --cap-add SYS_NICE --shm-size=4g -p 8000:8000 vllm-cpu-env --model=deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B --dtype=bfloat16
```

#### Example Curl

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    "prompt": "Q: What is 2+2?\nA:",
    "max_tokens": 100
}'
```

### 4️⃣ TinyLlama 1.1B Chat

#### Run Server

Linux/WSL:

```bash
docker run --rm --security-opt seccomp=unconfined \
  --cap-add SYS_NICE --shm-size=4g -p 8000:8000 \
  vllm-cpu-env --model=TinyLlama/TinyLlama-1.1B-Chat-v1.0 --dtype=bfloat16
```

Windows:

```bash
docker run --rm --security-opt seccomp=unconfined --cap-add SYS_NICE --shm-size=4g -p 8000:8000 vllm-cpu-env --model=TinyLlama/TinyLlama-1.1B-Chat-v1.0 --dtype=bfloat16
```

#### Example Curl

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "prompt": "Q: What is 2+2?\nA:",
    "max_tokens": 100
}'
```

### 5️⃣ microsoft/Phi-3-mini-4k-instruct

#### Run Server

Linux/WSL:

```bash
docker run --rm --security-opt seccomp=unconfined \
  --cap-add SYS_NICE --shm-size=4g -p 8000:8000 \
  vllm-cpu-env --model=microsoft/Phi-3-mini-4k-instruct --dtype=bfloat16
```

Windows:

```bash
docker run --rm --security-opt seccomp=unconfined --cap-add SYS_NICE --shm-size=4g -p 8000:8000 vllm-cpu-env --model=microsoft/Phi-3-mini-4k-instruct --dtype=bfloat16
```

#### Example Curl

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "microsoft/Phi-3-mini-4k-instruct",
    "prompt": "Q: What is 2+2?\nA:",
    "max_tokens": 100
}'
```

### 6️⃣ Qwen/Qwen2.5-0.5B-Instruct

#### Run Server

Linux/WSL:

```bash
docker run --rm --security-opt seccomp=unconfined \
  --cap-add SYS_NICE --shm-size=4g -p 8000:8000 \
  vllm-cpu-env --model=Qwen/Qwen2.5-0.5B-Instruct --dtype=bfloat16
```

Windows:

```bash
docker run --rm --security-opt seccomp=unconfined --cap-add SYS_NICE --shm-size=4g -p 8000:8000 vllm-cpu-env --model=Qwen/Qwen2.5-0.5B-Instruct --dtype=bfloat16
```

#### Example Curl

```bash
curl http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen2.5-0.5B-Instruct",
    "prompt": "Q: What is 2+2?\nA:",
    "max_tokens": 100
}'
```
