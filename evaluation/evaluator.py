import os
import requests
from google import genai
from dotenv import load_dotenv

os.abspath(os.path.join(os.path.dirname(__file__), '..'))

from evaluation.prompts import FLUENCY_JUDGE_PROMPT, ACCURARY_JUDGE_PROMPT, SUBJECTIVE_DOMAIN_ACCURACY_JUDGE_PROMPT

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "gemini-2.5-flash"
SUBJECTIVE_DOMAINS = ["Open-Ended Q&A / Conversational Quality", "Stress / Edge Cases"]

def call_model(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    return response.text

def judge_fluency(output):
    prompt = FLUENCY_JUDGE_PROMPT.format(output=output)
    return call_model(prompt)

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
    return call_model(prompt)

def main():
    domain = "Math & Numerical Reasoning"
    q = "What is 17 * 23?"
    expected = "391"
    output = "Please explain step by step.\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q"
    print(judge_accuracy(q, expected, output))
    print(judge_fluency(output))

if __name__ == "__main__":
    main()
