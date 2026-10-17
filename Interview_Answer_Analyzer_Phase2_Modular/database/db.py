"""Database helpers shared by all project modules."""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "interview_analyzer.db"

def get_db():
    """Open SQLite and return rows that can be accessed by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the project tables if they do not exist yet."""
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT NOT NULL, answer TEXT NOT NULL,
            score INTEGER NOT NULL, feedback TEXT NOT NULL, created_at TEXT NOT NULL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_name TEXT NOT NULL, student_email TEXT NOT NULL,
            professor_id INTEGER NOT NULL, interview_date TEXT NOT NULL, interview_time TEXT NOT NULL,
            purpose TEXT NOT NULL, meeting_link TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending',
            professor_feedback TEXT DEFAULT '', created_at TEXT NOT NULL,
            UNIQUE(professor_id, interview_date, interview_time))""")
