import os
import requests
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-2.5-flash"

def call_model(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    return response.text

def judge_fluency(output):
    prompt = f"""
        You are a fluency evaluation model. Score how fluent, clear, and grammatically correct the text is.

        Rules:
        - Fluency refers to readability, clarity, and grammatical correctness.
        - Ignore factual accuracy or correctness.
        - Ignore whether the answer is right or wrong.
        - Score 1.0 for very clear, natural, and grammatical text.
        - Score 0.6-0.9 for mostly fluent text with minor issues.
        - Score 0.3-0.6 for unclear, awkward, or error-filled text.
        - Score 0.0-0.3 only for text that is very hard to read.

        Return ONLY this JSON object:
        {{
        "score": <number between 0 and 1>,
        "reason": "<short reason>"
        }}

        Text to evaluate:
        "{output}"

        Return the JSON:
    """
    return call_model(prompt)


def judge_accuracy(q, expected, output):
    prompt = f"""
        You are an evaluation model. Score how correct the model's answer is.

        Rules:
        - Only the presence and correctness of the expected answer matters.
        - Ignore formatting differences, punctuation, or extra explanation.
        - If the expected answer appears clearly anywhere, score close to 1.0.
        - If it is partially correct or unclear, score between 0.3 and 0.7.
        - If the expected answer is missing or wrong, score 0.0.

        Return ONLY a JSON object:
        {{
        "score": <number between 0 and 1>,
        "reason": "<short reason>"
        }}

        Evaluate:

        Question: "{q}"
        Expected Answer: "{expected}"
        Model Output: "{output}"

        Return the JSON:
    """
    return call_model(prompt)

if __name__ == "__main__":
    q = "What is 17 * 23?"
    expected = "391"
    output = "Please explain step by step.\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q"
    print(judge_accuracy(q, expected, output))
    print(judge_fluency(output))
