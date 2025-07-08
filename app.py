import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)
DB_PATH = 'reviews.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Простая функция для определения настроения
POSITIVE = ['хорош', 'люблю']
NEGATIVE = ['плохо', 'ненавиж']

def detect_sentiment(text):
    text_lower = text.lower()
    if any(word in text_lower for word in POSITIVE):
        return 'positive'
    if any(word in text_lower for word in NEGATIVE):
        return 'negative'
    return 'neutral'

@app.before_first_request
def setup():
    init_db()

@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text'}), 400
    text = data['text']
    sentiment = detect_sentiment(text)
    created_at = datetime.utcnow().isoformat()
    conn = get_db_connection()
    cur = conn.execute(
        'INSERT INTO reviews (text, sentiment, created_at) VALUES (?, ?, ?)',
        (text, sentiment, created_at)
    )
    review_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({
        'id': review_id,
        'text': text,
        'sentiment': sentiment,
        'created_at': created_at
    }), 201

@app.route('/reviews', methods=['GET'])
def get_reviews():
    sentiment = request.args.get('sentiment')
    conn = get_db_connection()
    if sentiment:
        rows = conn.execute('SELECT * FROM reviews WHERE sentiment = ?', (sentiment,)).fetchall()
    else:
        rows = conn.execute('SELECT * FROM reviews').fetchall()
    conn.close()
    result = [
        {
            'id': row['id'],
            'text': row['text'],
            'sentiment': row['sentiment'],
            'created_at': row['created_at']
        } for row in rows
    ]
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True) 