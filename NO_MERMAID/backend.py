from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
import json
import time
import re
import requests
from datetime import datetime

app = Flask(__name__, template_folder='templates')
DB_PATH = "conversations.db"
OLLAMA_URL = "http://localhost:11434/api/generate"

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  query TEXT NOT NULL,
                  response_json TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def call_ollama(prompt):
    system_prompt = """You are a diagram generator. Generate a diagram specification in JSON format.
The user will describe a diagram (may have typos). Generate nodes and connections.

Respond ONLY with valid JSON, no other text. Format:
{
  "nodes": [
    {"id": "node1", "label": "Label", "color": "#color"}
  ],
  "connections": [
    {"from": "node1", "to": "node2", "label": "optional label"}
  ]
}

Use these colors: #ff6b6b, #4ecdc4, #ffe66d, #95e1d3, #dda0dd, #87ceeb, #f0e68c
Keep labels short. Position nodes in a logical layout.
If unclear, create a simple conceptual diagram."""

    full_prompt = f"{system_prompt}\n\nUser request: {prompt}"

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120
        )
        return response.json().get("response", "{}")
    except Exception as e:
        return json.dumps({"error": str(e)})

def parse_ollama_response(response):
    try:
        data = json.loads(response)
        return data
    except json.JSONDecodeError:
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
    return {"nodes": [], "connections": [], "error": "Could not parse diagram"}

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    response = call_ollama(query)
    diagram = parse_ollama_response(response)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (query, response_json) VALUES (?, ?)",
              (query, json.dumps(diagram)))
    conn.commit()
    diagram['id'] = c.lastrowid
    conn.close()
    
    return jsonify(diagram)

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, query, created_at FROM conversations ORDER BY created_at DESC LIMIT 20")
    rows = c.fetchall()
    conn.close()
    
    history = [{"id": row[0], "query": row[1], "created_at": row[2]} for row in rows]
    return jsonify(history)

@app.route('/history/<int:conv_id>', methods=['GET'])
def get_conversation(conv_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT query, response_json FROM conversations WHERE id = ?", (conv_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({"error": "Not found"}), 404
    
    return jsonify({"query": row[0], "diagram": json.loads(row[1])})

@app.route('/clear', methods=['POST'])
def clear_history():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM conversations")
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)