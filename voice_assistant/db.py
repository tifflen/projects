import sqlite3
import datetime
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'assistant.db')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            source TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()


def save_transcript(text, source='unknown'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO transcripts (text, source, created_at) VALUES (?, ?, ?)',
              (text, source, datetime.datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def list_transcripts(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, text, source, created_at FROM transcripts ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
