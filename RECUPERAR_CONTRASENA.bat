@echo off
chcp 65001 >nul
title Cabina Solar - Recuperar Contraseña
color 0E

echo ============================================
echo   CABINA SOLAR - RECUPERAR CONTRASEÑA
echo ============================================
echo.

REM ── Verificar que existe el entorno virtual ─────────────
if not exist "venv\Scripts\activate.bat" (
    color 0C
    echo [ERROR] No se encontró el entorno virtual.
    echo Primero ejecutá INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

REM ── Verificar que existe .env ─────────────────────────
if not exist ".env" (
    color 0C
    echo [ERROR] No se encontró el archivo .env
    echo Primero ejecutá INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

echo Este script te permite cambiar la contraseña de cualquier
echo usuario sin necesidad de entrar a la aplicación.
echo.

REM ── Pedir datos ─────────────────────────────────
set /p TARGET_USER=Nombre de usuario a recuperar [Admin]: 
if "%TARGET_USER%"=="" set TARGET_USER=Admin

set /p NEW_PASS=Nueva contraseña: 
if "%NEW_PASS%"=="" (
    color 0C
    echo [ERROR] La contraseña no puede estar vacía.
    pause
    exit /b 1
)

set /p CONFIRM_PASS=Confirmá la contraseña: 
if not "%NEW_PASS%"=="%CONFIRM_PASS%" (
    color 0C
    echo.
    echo [ERROR] Las contraseñas no coinciden. Intentá de nuevo.
    echo.
    pause
    exit /b 1
)

REM ── Activar entorno y generar script temporal ────────────
call venv\Scripts\activate.bat

(
    echo from dotenv import load_dotenv
    echo load_dotenv^(^)
    echo from app import create_app
    echo from app.models import User
    echo app = create_app^(^)
    echo with app.app_context^(^):
    echo     user = User.query.filter_by^(username='%TARGET_USER%'^).first^(^)
    echo     if not user:
    echo         print^('[ERROR] No se encontro el usuario: %TARGET_USER%'^)
    echo         exit^(1^)
    echo     user.set_password^('%NEW_PASS%'^)
    echo     from app.extensions import db
    echo     db.session.commit^(^)
    echo     print^('Contrasena actualizada correctamente'^)
) > _reset_temp.py

python _reset_temp.py
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] No se pudo actualizar la contraseña.
    echo Verificá que el nombre de usuario sea correcto.
    echo.
    del _reset_temp.py >nul 2>&1
    pause
    exit /b 1
)

del _reset_temp.py >nul 2>&1

echo.
echo ============================================
echo   CONTRASEÑA ACTUALIZADA CON ÉXITO ✓
echo ============================================
echo.
echo   Usuario:         %TARGET_USER%
echo   Nueva contraseña: %NEW_PASS%
echo.
echo Ahora podés iniciar la app con INICIAR_APP.bat
echo y entrar con los nuevos datos.
echo.
pause
