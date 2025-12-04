# HyRA: Hybrid Router Agent System for LLMs

**HyRA** (Hybrid Routing Agent Framework) is a modular, agent-driven system for managing LLM routing, verification, and capability tracking across multiple open-source LLMs.

---

## ⚙️ Setup Instructions

### 1️⃣ Clone and enter the repo
```bash
git clone https://github.com/UmarAhmed30/hybrid-routing-agents-framework.git
cd hybrid-routing-agents-framework
```

### 2️⃣ Install required Python packages
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure env variables (Refer env.example)

### 4️⃣ Setup PostgreSQL DB (Refer docs\db-schema.md)

### 5️⃣ Start desired model inference APIs (Refer docs\VLLM.md and docs\ollama.md)

### 6️⃣ Run Flask API
```bash
cd server
python server.py
```

### 7️⃣ Run Web Application
```bash
cd front
npm install
npm run dev
```

---
