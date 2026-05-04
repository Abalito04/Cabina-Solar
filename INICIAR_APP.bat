@echo off
chcp 65001 >nul
title Cabina Solar - Servidor
color 0A

echo ============================================
echo   CABINA SOLAR - INICIANDO SERVIDOR
echo ============================================
echo.

REM ── Verificar que existe el entorno virtual ───
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo [ERROR] No se encontró el entorno virtual.
    echo.
    echo Primero ejecutá INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

REM ── Verificar que existe .env ─────────────────
if not exist ".env" (
    color 0C
    echo [ERROR] No se encontró el archivo .env
    echo.
    echo Primero ejecutá INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

REM ── Activar entorno virtual ───────────────────
call venv\Scripts\activate.bat

REM ── Iniciar servidor ──────────────────────────
echo [OK] Entorno listo.
echo.
echo La aplicación estará disponible en:
echo   http://localhost:5000
echo.
echo Para acceder desde otro dispositivo en la misma red usá:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    goto :found_ip
)
:found_ip
set ip=%ip: =%
echo   http://%ip%:5000
echo.
echo Cerrá esta ventana para apagar el servidor.
echo ============================================
echo.

set FLASK_APP=run.py
python run.py

echo.
echo [INFO] Servidor detenido.
pause
