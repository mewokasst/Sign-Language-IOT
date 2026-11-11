@echo off
title Smart Glove Camera - Desktop App
echo Starting Smart Glove Desktop Camera App...
cd /d "%~dp0"
.venv\Scripts\python.exe src\run_app.py
pause

