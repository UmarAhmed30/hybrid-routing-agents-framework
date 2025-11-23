FLUENCY_JUDGE_PROMPT = """
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

ACCURARY_JUDGE_PROMPT = """
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

SUBJECTIVE_DOMAIN_ACCURACY_JUDGE_PROMPT = """
    You are an evaluation model for subjective or open-ended questions.
    Your task is to judge whether the model's answer makes reasonable sense, even if there is no single correct answer.

    Rules:
    - The answer does NOT need to match any specific expected output.
    - If the answer is coherent, relevant, and meaningfully responds to the question, score between 0.8 and 1.0.
    - If the answer is somewhat relevant but incomplete, generic, or shallow, score between 0.4 and 0.8.
    - If the answer is vague, minimally relevant, or weakly connected to the question, score between 0.2 and 0.4.
    - If the answer is nonsensical, off-topic, or meaningless, score between 0.0 and 0.2.
    - Ignore grammar, fluency, factual accuracy, or depth. This score is ONLY about whether it “makes sense” for the question.

    Return ONLY this JSON object:
    {{
    "score": <number between 0 and 1>,
    "reason": "<short reason>"
    }}

    Evaluate:
    Question: "{q}"
    Model Output: "{output}"

    Return the JSON:
"""