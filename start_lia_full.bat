@echo off
title LIA TRAIN FULL STACK

echo ==========================================
echo 🚀 INICIANDO LIA TRAIN FULL STACK
echo ==========================================
echo.

REM ==========================================
REM ABRIR DOCKER DESKTOP
REM ==========================================

echo 🐳 Abriendo Docker Desktop...

start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

timeout /t 10

REM ==========================================
REM ABRIR LM STUDIO
REM ==========================================

echo 🧠 Abriendo LM Studio...

start "" "%LOCALAPPDATA%\Programs\LM Studio\LM Studio.exe"

timeout /t 8

REM ==========================================
REM INICIAR CLOUDFLARE TUNNEL
REM ==========================================

echo ☁️ Iniciando Cloudflare Tunnel...

start "Cloudflare Tunnel" cmd /k "cd /d C:\cloudflared && cloudflared.exe tunnel run"

timeout /t 5

REM ==========================================
REM IR AL BACKEND
REM ==========================================

cd /d "%~dp0backend"

REM ==========================================
REM ACTIVAR VENV
REM ==========================================

call venv\Scripts\activate

echo ✅ Entorno virtual activo
echo.

REM ==========================================
REM ABRIR SWAGGER LOCAL
REM ==========================================

start http://127.0.0.1:8000/docs

REM ==========================================
REM INICIAR FASTAPI
REM ==========================================

echo ==========================================
echo 🚀 INICIANDO API
echo ==========================================
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause