@echo off
echo Starting Backend Server...
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app:app --reload"

echo Starting Frontend Server...
start cmd /k "cd frontend && npm run dev -- --open"

echo Fake News & Phishing Detection System is starting!
