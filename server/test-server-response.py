import requests

def req_answer():
    print("Requesting answer from server...")
    r = requests.post(
        "http://localhost:5000/api/generate_anwser",
        json={
            "query": "What is 17 * 23?"
        }
    )
    response = r.json()
    print("Received response:", response)
    return response

if __name__ == "__main__":
    req_answer()