@echo off
chcp 1252 >nul
title Cabina Solar - Servidor
color 0A

echo ============================================
echo   CABINA SOLAR - INICIANDO SERVIDOR
echo ============================================
echo.

REM -- Verificar entorno virtual --
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo [ERROR] No se encontro el entorno virtual.
    echo.
    echo Primero ejecuta INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

REM -- Verificar .env --
if not exist ".env" (
    color 0C
    echo [ERROR] No se encontro el archivo .env
    echo.
    echo Primero ejecuta INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

REM -- Activar entorno virtual --
call venv\Scripts\activate.bat

REM -- Mostrar URLs de acceso --
echo [OK] Entorno listo.
echo.
echo La aplicacion estara disponible en:
echo   http://localhost:5000
echo.
echo Para acceder desde otro dispositivo en la misma red usa:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    goto :found_ip
)
:found_ip
set ip=%ip: =%
echo   http://%ip%:5000
echo.
echo Cierra esta ventana para apagar el servidor.
echo ============================================
echo.

set FLASK_APP=run.py
python run.py

echo.
echo [INFO] Servidor detenido.
pause
