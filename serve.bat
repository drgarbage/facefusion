@echo off
call venv\Scripts\activate
uvicorn faceapi:app --reload --host 0.0.0.0 --port 8080
deactivate