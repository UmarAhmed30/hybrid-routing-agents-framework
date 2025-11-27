import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.gemini.client import GeminiClient
from db.client import get_connection
from agents.prompts import VERIFIER_PROMPT

gemini_client = GeminiClient()

def verify(model_output, expected_output):
    try:
        system_prompt = VERIFIER_PROMPT.format(
            model_output=model_output,
            expected_output=expected_output
        )
        return bool(gemini_client.generate_content(system_prompt).strip().lower() == "true")
    except Exception as e:
        print("Error during verification:", e)
        return False

def main():
    model_output = "12"
    expected_output = "12 or maybe 13"
    is_correct = verify(model_output, expected_output)
    print(f"Verification Result: {is_correct}")

if __name__ == "__main__":
    main()
