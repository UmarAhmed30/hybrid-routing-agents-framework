# --- GPU-ready dev Dockerfile ---
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

# Install Python 3.10 and tools
RUN apt-get update && apt-get install -y \
    python3 python3-venv python3-dev python3-pip git curl \
    && python3 -m pip install --upgrade pip \
    && pip install uv \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files only (these rarely change)
COPY pyproject.toml uv.lock README.md ./

ENV UV_PYTHON=python3
RUN uv sync --frozen --no-dev

# Preload model dependencies so you don't rebuild often
# RUN python3 -c "import torch, transformers, vllm"

# Environment variables
ENV HYRA_MODEL_ID="facebook/opt-125m"
ENV VLLM_DEVICE="cuda"

EXPOSE 8000

# Hot-reload mode
CMD ["uv", "run", "uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
