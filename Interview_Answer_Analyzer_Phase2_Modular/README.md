# Interview Answer Analyzer — Phase 2 (Modular GitHub Version)

A student project with rule-based interview-answer feedback, answer history using Stack/LIFO behaviour, and professor appointment booking with meeting links.

## Run locally
1. Install Python 3.10 or newer.
2. In this folder run `python -m venv .venv` and activate it.
3. Run `pip install -r requirements.txt`.
4. Run `python app.py`.
5. Open `http://127.0.0.1:5000`.

SQLite database is created automatically on first run. Professor profiles are demo data. Jitsi links are demo meeting links; authentication and role-based permissions are not implemented, so do not use this version for private real interviews.

## Four-person work split

### 1. Navjot Singh — Frontend
Files: `templates/index.html`, `static/css/style.css`, `static/js/app.js`
Work: page layout, forms, booking interface, display results, responsive styling.

### 2. Dheeraj Singh — Backend and integration
Files: `app.py`, `database/db.py`
Work: Flask routes, request/response handling, database initialization, connect modules. Coordinate API contracts with all members.

### 3. Akbar Abdur Rehman — Answer analysis
Files: `analyzer/analysis.py` and `tests/test_analysis.py`
Work: rule-based checks, scoring, feedback wording, analysis tests.

### 4. Chitransh Khurana — Stack history and appointments
Files: `analyzer/history.py`, `appointments/booking.py`
Work: history/undo using LIFO behaviour, booking validation, conflict checks, status/feedback workflow.

## GitHub workflow
Each member should create a feature branch, edit only their assigned files where possible, commit changes, push the branch, and open a Pull Request into `main`. Pull the latest `main` before starting work. Do not commit the SQLite database or virtual environment.

Suggested branches: `feature/frontend`, `feature/backend`, `feature/answer-analysis`, `feature/appointments-history`.

## Important limitation
The demo appointment status and feedback endpoints are not protected by user authentication. Add login and authorization before treating professor actions as private or production-ready.
