# 🧠 HyRA — Hybrid Routing Agent Framework

**HyRA** (Hybrid Routing Agent Framework) is a modular, agent-driven system for managing large language model routing, verification, and capability tracking across multiple open-source LLMs.
This repository contains the base **API service**, development setup, and containerized environment for the framework.

---

## 🚀 Overview

HyRA provides a foundation for:
- **Routing** queries across multiple models (RouterAgent)
- **Verifying** and scoring outputs (VerifierAgent)
- **Tracking** metrics like latency, accuracy, and cost (Registry)
- **Serving** results via a FastAPI interface (API Service)

This setup includes:
- 🐍 Python 3.12
- ⚡ FastAPI + Uvicorn
- 🧩 Dependency management via [`uv`](https://github.com/astral-sh/uv)
- 🐳 Docker + Compose for container orchestration

---

## 🏗️ Project Structure

```
hybrid-routing-agents-framework/
├── api/                 # FastAPI entrypoint and routes
│   └── server.py
├── agents/              # Router / Verifier / Inference agents
├── registry/            # Model registry and database logic
├── services/            # Business logic and service layer
├── scripts/             # Setup / data loading / utils
├── Dockerfile           # Build definition for API service
├── docker-compose.yml   # Compose setup for local dev
├── pyproject.toml       # Project dependencies (uv-managed)
├── uv.lock              # Locked dependency versions
├── .dockerignore
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone and enter the repo
```bash
git clone <your-repo-url>
cd hybrid-routing-agents-framework
```

---

### 2️⃣ Install `uv` (ultrafast package manager)
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```
Verify:
```bash
uv --version
```

---

### 3️⃣ Create and activate virtual environment
```bash
uv venv
.venv\Scripts\activate     # on Windows
# or
source .venv/bin/activate  # on Linux/Mac
```

---

### 4️⃣ Sync dependencies
```bash
uv sync
```

---

### 5️⃣ Run API locally
```bash
uv run uvicorn api.server:app --reload
```
Then visit:
- [http://localhost:8000](http://localhost:8000)
- [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)

---

## 🐳 Docker Setup

### Build and run using Docker Compose
```bash
docker compose up --build
```

### Run detached (background)
```bash
docker compose up -d
```

Then visit:
- [http://localhost:8000](http://localhost:8000)

To stop containers:
```bash
docker compose down
```

---

## 🧰 Development Commands

| Task | Command |
|------|----------|
| Format code | `uv run black .` |
| Sort imports | `uv run isort .` |
| Run tests | `uv run pytest` |

---

## 🌐 Environment Variables

You can define these in a `.env` file (not tracked by Git):

```bash
ENV=dev
DATABASE_URL=postgresql://user:pass@db:5432/hyra_db
```

---

## 🧩 Maintainers
**Umar Ahmed Thameem Ahmed**
CS Graduate Student, University of Colorado Boulder
📧 `umar.ahmed.t.30@gmail.com`

---