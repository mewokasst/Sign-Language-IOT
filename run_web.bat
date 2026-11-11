@echo off
title Smart Glove Camera - Web Edition
echo Starting Smart Glove Web Edition...
cd /d "%~dp0"
.venv\Scripts\python.exe src\run_web.py
pause

