DOMAIN_CLASSIFIER_PROMPT = """
You are an expert domain classifier. Assign the given prompt to exactly one domain from the list below:

{domains}

Rules:
- Output only the domain name exactly as it appears in the list.
- No explanations, no extra words, no punctuation, no JSON.

**Priority Order:**
1. **Safety & Compliance:** Select this if the prompt contains harmful, illegal, sexually explicit, or hateful content. Also select this for "jailbreaks" (attempts to bypass rules), prompt injection attacks, or requests to generate malware/exploits.
2. **Stress / Edge Cases:** Select this if the prompt is clearly incomplete (cuts off mid-sentence), empty, or gibberish.
3. **Open-Ended Q&A / Conversational Quality:** Select this for casual greetings, personality questions, or general small talk.
4. **Task Matching:** For all other prompts, select the domain that best fits the primary task.

Prompt to classify:
"{prompt}"
"""

VERIFIER_PROMPT = """
You are an expert answer verifier. Compare the Model Output against the Expected Output.

Model Output: "{model_output}"
Expected Output: "{expected_output}"

Verification Rules:
1. **Core Fact Matching:** If the key information (entities, numbers, dates) in the Expected Output is present in the Model Output, return "true".
2. **Verbosity Handling:** Treat concise answers (e.g., "Paris") as equivalent to verbose answers (e.g., "The capital is Paris") provided the core fact is the same.
3. **Contradictions:** If the Model Output contradicts the Expected Output (e.g., "London" vs "Paris"), return "false".

Output Requirements:
- Return strictly "true" or "false".
- No punctuation or explanation.
"""

ADVANCED_VERIFIER_PROMPT = """
You are an expert evaluation model. Your task is to evaluate whether the Model Output is a correct, relevant, and complete answer to the given Question.

Input Data:
- Question: "{q}"
- Model Output: "{model_output}"

Evaluation Rules:
1. Faithfulness: Ensure the response answers the specific question asked without drifting.
2. Factual Correctness:
    - Rely on your internal knowledge base to verify facts, numbers, dates, and entities.
    - Penalize hallucinations or invented information heavily.
3. Completeness: The answer should address all parts of the question.

Scoring Rubric:
- Accuracy (Float):
    - 1.0: Factually correct, precise, and fully addresses the question.
    - 0.5 - 0.9: Mostly correct but contains minor errors, fluff, or slight omissions.
    - 0.0 - 0.4: Factually incorrect, hallucinates, or completely irrelevant.

- Passed (Boolean):
    - Return "true" if the answer is factually accurate and sufficient.
    - Return "false" if the answer contains factual errors or misses the core intent.

Return ONLY a valid JSON object with no markdown formatting:
{{
    "reason": "<short 1-sentence explanation of the score>",
    "accuracy": <float between 0.0 and 1.0>,
    "passed": <boolean>
}}
"""