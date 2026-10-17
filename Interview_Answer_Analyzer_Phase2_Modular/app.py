"""Flask application entry point. Each team module is imported through clear interfaces."""
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from database.db import init_db, get_db
from analyzer.analysis import analyze_answer
from analyzer.history import get_history, undo_latest, clear_history
from appointments.booking import list_professors, list_appointments, create_appointment, set_status, save_feedback

app = Flask(__name__)

@app.route("/")
def index(): return render_template("index.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or request.form
    question = str(data.get("question", "")).strip(); answer = str(data.get("answer", "")).strip()
    if not question or not answer: return jsonify({"error": "Please enter both an interview question and your answer."}), 400
    score, feedback, word_count = analyze_answer(question, answer)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db() as conn:
        cur = conn.execute("INSERT INTO analyses (question, answer, score, feedback, created_at) VALUES (?, ?, ?, ?, ?)", (question, answer, score, "\n".join(feedback), created_at))
        analysis_id = cur.lastrowid
    return jsonify({"id": analysis_id, "question": question, "answer": answer, "score": score, "feedback": feedback, "word_count": word_count, "created_at": created_at})

@app.route("/api/history", methods=["GET"])
def history(): return jsonify(get_history())

@app.route("/api/undo", methods=["POST"])
def undo():
    if not undo_latest(): return jsonify({"message": "There is no analysis to undo."}), 404
    return jsonify({"message": "The latest analysis was removed."})

@app.route("/api/clear-history", methods=["POST"])
def clear():
    clear_history(); return jsonify({"message": "History cleared."})

@app.route("/api/professors", methods=["GET"])
def professors(): return jsonify(list_professors())

@app.route("/api/appointments", methods=["GET"])
def appointments(): return jsonify(list_appointments())

@app.route("/api/appointments", methods=["POST"])
def book():
    data = request.get_json(silent=True) or {}
    result, error, status = create_appointment(data)
    if error: return jsonify({"error": error}), status
    return jsonify({"message": "Appointment request submitted. Wait for the professor to confirm it.", **result}), status

@app.route("/api/appointments/<int:appointment_id>/status", methods=["PATCH"])
def appointment_status(appointment_id):
    data = request.get_json(silent=True) or {}
    ok, message, status = set_status(appointment_id, data.get("status", ""))
    if not ok: return jsonify({"error": message}), status
    return jsonify({"message": f"Appointment marked as {message.lower()}.", "status": message})

@app.route("/api/appointments/<int:appointment_id>/feedback", methods=["PATCH"])
def appointment_feedback(appointment_id):
    data = request.get_json(silent=True) or {}
    ok, message, status = save_feedback(appointment_id, data.get("professor_feedback", ""))
    if not ok: return jsonify({"error": message}), status
    return jsonify({"message": message})

init_db()
if __name__ == "__main__":
    # Debug mode is intended only for local development.
    app.run(debug=True)
