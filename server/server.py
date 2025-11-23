import sys
import flask
import requests
from pathlib import Path

# Add parent directory to path so we can import evaluation module
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.evaluator import judge_accuracy

app = flask.Flask(__name__)

@app.route('/api/generate_anwser', methods=['POST'])
def generate_anwser_endpoint():
    data = flask.request.json
    question = data.get('query')

    # TODO:
    # To search in DB (model registry) for model info later. 
    # It will select the best model in the domin.

    ans = inference(
        model="llama3", # to use the desired model from the registry
        messages=[{"role":"user","content": question}],
        max_tokens=200
    )

    exp_ans = inference(
        model="llama3", # to change to Gemini model when available
        messages=[{"role":"user","content": question}],
        max_tokens=200
    )

    accuracy = judge_accuracy(
        q=question,
        expected=exp_ans.get('message', {}).get('content'),
        output=ans.get('message', {}).get('content'),
        judge_model="llama3"
    )

    print("Accuracy Evaluation:", accuracy)

    return flask.jsonify(ans)

def inference(model="llama3", messages=None, max_tokens=200):
    r = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": model,
            "stream": False,
            "messages": messages,
            "max_tokens": max_tokens
        }
    )
    response = r.json()
    return response

if __name__ == '__main__':
    app.run(host='localhost', port=5000)