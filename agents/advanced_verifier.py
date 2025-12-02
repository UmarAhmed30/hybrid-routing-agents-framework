import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.gemini.client import GeminiClient
from db.client import get_connection
from agents.prompts import ADVANCED_VERIFIER_PROMPT

gemini_client = GeminiClient()

async def verify(prompt, model_output):
    try:
        system_prompt = ADVANCED_VERIFIER_PROMPT.format(
            q=prompt,
            model_output=model_output,
        )
        response = await asyncio.to_thread(gemini_client.generate_content, system_prompt)
        print(response)
        cleaned_response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned_response)
        return {
            "accuracy": float(data.get("accuracy", 0.0)),
            "passed": str(data.get("passed", "false")).lower() == "true"
        }
    except Exception as e:
        print("Error during verification:", e)
        return {
            "accuracy": 0.0,
            "passed": False,
        }

async def _demo():
    prompt = "What is 6 multiplied by 2?"
    model_output = "12"
    expected_output = "12 or maybe 13"
    result = await verify(prompt, model_output, expected_output)
    print(f"Verification Result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
