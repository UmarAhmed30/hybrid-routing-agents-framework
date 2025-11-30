import sys
import json
from pathlib import Path
from threading import Thread
import uuid

# Add parent directory to path so we can import evaluation module
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.router.router import route

app = Flask(__name__)
CORS(app)

# Store active sessions and their logs
sessions = {}

@app.route('/api/start_session', methods=['POST'])
def start_session():
    """Create a new routing session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'logs': [],
        'result': None,
        'status': 'pending',
        'error': None
    }
    return jsonify({'session_id': session_id})

@app.route('/api/get_logs/<session_id>', methods=['GET'])
def get_logs(session_id):
    """Poll for logs and result"""
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    return jsonify({
        'logs': session['logs'],
        'status': session['status'],
        'result': session['result'],
        'error': session['error']
    })

@app.route('/api/start_routing', methods=['POST'])
def start_routing():
    """Start routing process for a session"""
    data = request.json
    query = data.get('query')
    session_id = data.get('session_id')
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    def event_callback(msg):
        # Add log to session
        sessions[session_id]['logs'].append(msg)
        print(f"[LOG] {msg}")
    
    def router_thread_func():
        try:
            result = route(query, event_callback=event_callback)
            sessions[session_id]['result'] = result
            sessions[session_id]['status'] = 'complete'
        except Exception as e:
            sessions[session_id]['error'] = str(e)
            sessions[session_id]['status'] = 'error'
    
    # Run routing in background thread
    thread = Thread(target=router_thread_func, daemon=True)
    thread.start()
    
    sessions[session_id]['status'] = 'running'
    return jsonify({'status': 'started'})

@app.route('/api/generate_answer', methods=['POST'])
def generate_answer():
    """Legacy endpoint for backward compatibility"""
    data = request.json
    query = data.get('query')
    
    try:
        def dummy_callback(msg):
            pass
        
        result = route(query, event_callback=dummy_callback)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False)