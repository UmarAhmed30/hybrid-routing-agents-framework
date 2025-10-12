from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import time

from agents.inference_agent import InferenceAgent

app = FastAPI(title="HyRA - vLLM API", version="0.1.0")

class GenerateRequest(BaseModel):
    prompt: str = Field(..., example="Write a haiku about the moon.")
    max_new_tokens: Optional[int] = 128
    temperature: Optional[float] = 0.7
    top_k: Optional[int] = None
    top_p: Optional[float] = None

class GenerateResponse(BaseModel):
    model: str
    backend: str
    generated_text: str
    latency_ms: int

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/v1/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    agent = InferenceAgent.get()
    start = time.time()
    try:
        text = agent.generate(
            prompt=req.prompt,
            max_new_tokens=req.max_new_tokens,
            temperature=req.temperature,
            top_k=req.top_k,
            top_p=req.top_p,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    latency = int((time.time() - start) * 1000)
    return GenerateResponse(
        model=agent.model_id,
        backend=agent.backend,
        generated_text=text,
        latency_ms=latency,
    )
