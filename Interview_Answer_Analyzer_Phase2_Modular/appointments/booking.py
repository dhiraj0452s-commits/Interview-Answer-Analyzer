"""Professor appointments and feedback, owned by the booking module team member."""
from datetime import datetime
import re
import sqlite3
from database.db import get_db

PROFESSORS = [
    {"id": 1, "name": "Dr. A. Sharma", "specialization": "HR and Behavioural Interviews"},
    {"id": 2, "name": "Prof. R. Mehta", "specialization": "Technical Interviews"},
    {"id": 3, "name": "Dr. P. Verma", "specialization": "Communication and Soft Skills"},
]

def list_professors(): return PROFESSORS

def list_appointments():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM appointments ORDER BY interview_date, interview_time").fetchall()
    names = {p["id"]: p["name"] for p in PROFESSORS}
    result = []
    for row in rows:
        item = dict(row); item["professor_name"] = names.get(item["professor_id"], "Professor"); result.append(item)
    return result

def create_appointment(data):
    name = str(data.get("student_name", "")).strip(); email = str(data.get("student_email", "")).strip()
    purpose = str(data.get("purpose", "")).strip(); day = str(data.get("interview_date", "")).strip()
    time = str(data.get("interview_time", "")).strip()
    try:
        professor_id = int(data.get("professor_id", 0))
        professor = next((p for p in PROFESSORS if p["id"] == professor_id), None)
        start = datetime.strptime(f"{day} {time}", "%Y-%m-%d %H:%M")
    except (ValueError, TypeError): return None, "Choose a valid professor, date, and time.", 400
    if not all([name, email, purpose]) or not professor: return None, "Please complete every booking field.", 400
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email): return None, "Enter a valid email address.", 400
    if start <= datetime.now(): return None, "Choose a future date and time.", 400
    # Demo meeting URL. For a real service, use authenticated meeting creation.
    room = f"InterviewPractice-{professor_id}-{start.strftime('%Y%m%d%H%M')}-{abs(hash(email)) % 100000}"
    link = f"https://meet.jit.si/{room}"
    try:
        with get_db() as conn:
            cur = conn.execute("""INSERT INTO appointments
                (student_name, student_email, professor_id, interview_date, interview_time, purpose, meeting_link, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?)""",
                (name, email, professor_id, day, time, purpose, link, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            appointment_id = cur.lastrowid
    except sqlite3.IntegrityError: return None, "That professor already has a booking at this date and time. Please choose another slot.", 409
    return {"id": appointment_id, "meeting_link": link, "status": "Pending"}, None, 201

def set_status(appointment_id, status):
    status = str(status).strip().title()
    if status not in {"Accepted", "Rejected", "Completed"}: return False, "Status must be Accepted, Rejected, or Completed.", 400
    with get_db() as conn:
        cur = conn.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
        if cur.rowcount == 0: return False, "Appointment not found.", 404
    return True, status, 200

def save_feedback(appointment_id, feedback):
    feedback = str(feedback).strip()
    if not feedback: return False, "Please enter feedback before saving.", 400
    with get_db() as conn:
        cur = conn.execute("UPDATE appointments SET professor_feedback = ?, status = 'Completed' WHERE id = ?", (feedback, appointment_id))
        if cur.rowcount == 0: return False, "Appointment not found.", 404
    return True, "Interview feedback saved.", 200
