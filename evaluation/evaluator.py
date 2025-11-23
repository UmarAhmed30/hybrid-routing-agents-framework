import os
import sys
import json
from pathlib import Path
import requests
from google import genai
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.prompts import FLUENCY_JUDGE_PROMPT, ACCURARY_JUDGE_PROMPT, SUBJECTIVE_DOMAIN_ACCURACY_JUDGE_PROMPT

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "gemini-2.0-flash-lite"
SUBJECTIVE_DOMAINS = ["Open-Ended Q&A / Conversational Quality", "Stress / Edge Cases"]

def call_model(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    return response.text

def sanitize(response):
    cleaned = response.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)

def judge_fluency(output):
    prompt = FLUENCY_JUDGE_PROMPT.format(output=output)
    response = call_model(prompt)
    sanitized_response = sanitize(response)
    return sanitized_response.get("score", 0.0)

def judge_accuracy(domain, q, expected, output):
    if domain in SUBJECTIVE_DOMAINS:
        prompt = SUBJECTIVE_DOMAIN_ACCURACY_JUDGE_PROMPT.format(
            q=q,
            output=output
        )
    else:
        prompt = ACCURARY_JUDGE_PROMPT.format(
            q=q,
            expected=expected,
            output=output
        )
    response = call_model(prompt)
    sanitized_response = sanitize(response)
    return sanitized_response.get("score", 0.0)

def main():
    domain = "Open-Ended Q&A / Conversational Quality"
    q = "What are some ways to reduce stress?"
    expected = "391"
    output = "Choose the most suitable option to answer the above question. Options:  A. meditation  B. exercise  C. eat more chocolate  D. talk on phone  E. drink alcohol\nA:\n\nA. Meditation, B. Exercise, and C. Eat more chocolate."
    print(judge_accuracy(domain, q, expected, output))
    print(judge_fluency(output))

if __name__ == "__main__":
    main()
