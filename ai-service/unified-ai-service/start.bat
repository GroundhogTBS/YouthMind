@echo off
echo Starting YouthMind AI Service...
cd /d %~dp0
pip install fastapi uvicorn pydantic pydantic-settings python-dotenv openai python-jose -q
python main.py
pause
