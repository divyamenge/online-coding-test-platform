# Online Coding Test Platform

A Django-based platform where admins can create Python tests, students can attempt timed exams, and the system shows score-based rankings on a leaderboard.

## Features
- Admin login and dashboard
- Create, edit, and delete tests
- Add MCQ and coding questions
- Set duration and total marks
- Student registration and login
- Timed test attempts
- Auto-scoring for MCQ answers
- Results page with correct answers
- Leaderboard with top 10 performers
- MySQL-ready configuration
- Security-first design: no direct execution of submitted Python code on the server

## Tech Stack
- Python
- Django
- MySQL
- HTML / CSS / Bootstrap
- JavaScript

## Project structure
- `coding_platform/` — Django project settings and URLs
- `exam/` — models, views, forms, admin, app logic
- `templates/` — HTML pages
- `static/` — CSS and static assets

## Local setup
1. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

2. Install requirements:
   pip install -r requirements.txt

3. Apply migrations:
   python manage.py migrate

4. Create an admin user:
   python manage.py createsuperuser

5. Run the app:
   python manage.py runserver

6. Open:
   http://127.0.0.1:8000/

## MySQL configuration
If you want to use MySQL, set:
- `USE_MYSQL=True`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

Example in `.env` or environment variables.

## Secure code evaluation note
The system follows the required security guidance: submitted Python code is not executed directly on the Django server. For real production use, connect to a sandboxed execution service or isolated container environment for code evaluation.

## GitHub
Repository: https://github.com/divyamenge/online-coding-test-platform

## Deployment
This project can be deployed on Render, Railway, PythonAnywhere, or a VPS. For production, configure environment variables and a managed MySQL database.
