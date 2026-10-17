"""Database-backed answer history. Latest-first removal follows Stack/LIFO behaviour."""
from database.db import get_db

def get_history():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT 20").fetchall()
    return [{"id": r["id"], "question": r["question"], "answer": r["answer"], "score": r["score"],
             "feedback": r["feedback"].split("\n"), "created_at": r["created_at"]} for r in rows]

def undo_latest():
    """Remove the newest saved analysis, like popping the top of a stack."""
    with get_db() as conn:
        row = conn.execute("SELECT id FROM analyses ORDER BY id DESC LIMIT 1").fetchone()
        if row is None: return False
        conn.execute("DELETE FROM analyses WHERE id = ?", (row["id"],))
    return True

def clear_history():
    with get_db() as conn: conn.execute("DELETE FROM analyses")
