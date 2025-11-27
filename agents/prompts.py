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