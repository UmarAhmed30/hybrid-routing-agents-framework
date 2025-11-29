import sys
import flask
import time
from pathlib import Path

# Add parent directory to path so we can import evaluation module
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.router.router import route

app = flask.Flask(__name__)

@app.route('/api/generate_answer', methods=['POST'])
def generate_answer_endpoint():
    data = flask.request.json
    question = data.get('query')

    t1 = time.time()
    result = route(question)
    t2 = time.time()
    print(f"[ROUTER] Total routing time: {(t2 - t1)*1000:.2f} ms")
    print(result)
    return flask.jsonify({
        "answer": result["output"],
        "metrics": result["metrics"],
        "verified": result["verified"]
    })

if __name__ == '__main__':
    app.run(host='localhost', port=5000)