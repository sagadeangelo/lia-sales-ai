@echo off
title LIA SALES AI

echo ==========================================
echo 🚀 INICIANDO LIA SALES AI
echo ==========================================
echo.

REM ==========================================
REM IR A BACKEND
REM ==========================================

cd /d "%~dp0backend"

REM ==========================================
REM ACTIVAR ENTORNO VIRTUAL
REM ==========================================

call venv\Scripts\activate

REM ==========================================
REM MOSTRAR INFO
REM ==========================================

echo ✅ Entorno virtual activo
echo ✅ Backend iniciado
echo.
echo ==========================================
echo 🌐 API:
echo http://127.0.0.1:8000
echo ==========================================
echo.

REM ==========================================
REM INICIAR UVICORN
REM ==========================================

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause