import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.gemini.client import GeminiClient
from db.client import get_connection
from agents.prompts import DOMAIN_CLASSIFIER_PROMPT

gemini_client = GeminiClient()

def classify(prompt):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM domains")
        domains_list = [row['name'] for row in cur.fetchall()]
        formatted_domains = "\n- ".join(domains_list)
        system_prompt = DOMAIN_CLASSIFIER_PROMPT.format(
            domains=formatted_domains,
            prompt=prompt
        )
        return gemini_client.generate_content(system_prompt).strip()
    except Exception as e:
        print("Error during domain classification:", e)
        return "Open-Ended Q&A / Conversational Quality"

def main():
    test_prompt = "How can I ensure my online accounts are secure?"
    classification = classify(test_prompt)
    print(f"Classified Domain: {classification}")

if __name__ == "__main__":
    main()
