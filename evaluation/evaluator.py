import requests

def judge_accuracy(q, expected, output, judge_model="Qwen/Qwen2.5-3B-Instruct"):
    print(output)
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

    r = requests.post(
        "http://localhost:8000/v1/completions",
        json={
            "model": judge_model,
            "prompt": prompt,
            "max_tokens": 100
        }
    )
    response = r.json()["choices"][0]["text"].strip()
    return response

if __name__ == "__main__":
    response = judge_accuracy(
        "What is 17 * 23?",
        "391",
        "Please explain step by step.\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q: What is 17 * 23?\n\n**P: 391.\n\n**Q"
    )
    print(response)