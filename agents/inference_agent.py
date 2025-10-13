# agents/inference_agent.py
"""
InferenceAgent: manages a single-model vLLM backend for text generation.
Future versions of HyRA can register multiple such agents and route between them.
"""
# --- Safe patch for CPU-only Torch builds (no Inductor) ---
# import os

# os.environ["CUDA_VISIBLE_DEVICES"] = ""
# os.environ["VLLM_USE_CUDA"] = "0"          # disables CUDA entirely
# os.environ["VLLM_GPU_MEMORY_UTILIZATION"] = "0.6"  # (optional)

import torch
import types
from dotenv import load_dotenv
load_dotenv()

_instance = None

if not hasattr(torch, "_inductor"):
    torch._inductor = types.SimpleNamespace(config=types.SimpleNamespace())
elif not hasattr(torch._inductor, "config"):
    torch._inductor.config = types.SimpleNamespace()

if not hasattr(torch._inductor.config, "compile_threads"):
    torch._inductor.config.compile_threads = 1
# -----------------------------------------------------------

from vllm import LLM, SamplingParams
import os

MAX_NEW_TOKENS = int(os.getenv("HYRA_MAX_NEW_TOKENS", 128))

class InferenceAgent:
    def __init__(self, model_id=None, backend="vllm"):
        self.model_id = model_id or os.getenv("HYRA_MODEL_ID", "facebook/opt-125m")
        self.backend = backend
        self.llm = None
        self._loaded = False
        self.default_sampling = None

    @classmethod
    def get(cls):
        global _instance
        if _instance is None:
            _instance = cls()
            _instance.load_model()
        return _instance

    def load_model(self):
        if self.backend != "vllm":
            raise RuntimeError("Only vLLM backend supported here.")
        try:
            from vllm import LLM, SamplingParams
        except ImportError:
            raise RuntimeError(
                "vLLM not installed — run `uv pip install vllm` inside your .venv"
            )

        device_type = os.environ.get("VLLM_DEVICE", "cpu").lower()

        print(f"[INFO] Loading model {self.model_id} on {device_type.upper()} ...")

        # Disable CUDA if not usable
        if device_type == "cuda" and not torch.cuda.is_available():
            print("[WARN] CUDA not available; falling back to CPU.")
            device_type = "cpu"

        # os.environ["VLLM_ATTENTION_BACKEND"] = "FLASH_ATTN"  # optional, more efficient
        # os.environ["VLLM_GPU_MEMORY_UTILIZATION"] = "0.7"
        # os.environ["VLLM_USE_CUDA"] = "0"

        # Load LLM (force CPU for MX150)
        self.llm = LLM(
            model=self.model_id,
            dtype="float32" if device_type == "cpu" else "auto",
            tensor_parallel_size=1,
        )

        self.default_sampling = SamplingParams(
            temperature=0.7,
            max_tokens=MAX_NEW_TOKENS,
        )
        self._loaded = True

    def get_info(self):
        return {
            "model_id": self.model_id,
            "backend": self.backend,
            "loaded": self._loaded,
        }


    def generate(self, prompt: str, max_new_tokens=None, temperature=None, top_k=None, top_p=None):
        if not self._loaded:
            self.load_model()

        sampling = SamplingParams(
            temperature=temperature or self.default_sampling.temperature,
            max_tokens=max_new_tokens or self.default_sampling.max_tokens,
            top_k=top_k,
            top_p=top_p,
        )
        outputs = self.llm.generate([prompt], sampling)
        return outputs[0].outputs[0].text.strip()
