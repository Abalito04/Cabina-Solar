@echo off
chcp 1252 >nul
title Cabina Solar - Recuperar Contrasena
color 0E

echo ============================================
echo   CABINA SOLAR - RECUPERAR CONTRASENA
echo ============================================
echo.

cd /d %~dp0

REM -- Verificar entorno virtual --
if not exist "venv\Scripts\python.exe" (
    color 0C
    echo [ERROR] No se encontro el entorno virtual.
    echo Primero ejecuta INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

REM -- Verificar .env --
if not exist ".env" (
    color 0C
    echo [ERROR] No se encontro el archivo .env
    echo Primero ejecuta INSTALAR_PRIMERA_VEZ.bat
    echo.
    pause
    exit /b 1
)

echo Este script te permite cambiar la contrasena de cualquier
echo usuario sin necesidad de entrar a la aplicacion.
echo.

REM -- Pedir datos --
set /p TARGET_USER=Nombre de usuario a recuperar (Enter = Admin): 
if "%TARGET_USER%"=="" set TARGET_USER=Admin

set /p NEW_PASS=Nueva contrasena: 
if "%NEW_PASS%"=="" (
    color 0C
    echo [ERROR] La contrasena no puede estar vacia.
    pause
    exit /b 1
)

set /p CONFIRM_PASS=Confirma la contrasena: 
if not "%NEW_PASS%"=="%CONFIRM_PASS%" (
    color 0C
    echo.
    echo [ERROR] Las contrasenias no coinciden. Intenta de nuevo.
    echo.
    pause
    exit /b 1
)

REM -- Generar y ejecutar script temporal --
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

venv\Scripts\python.exe _reset_temp.py
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] No se pudo actualizar la contrasena.
    echo Verifica que el nombre de usuario sea correcto.
    echo.
    del _reset_temp.py >nul 2>&1
    pause
    exit /b 1
)

del _reset_temp.py >nul 2>&1

echo.
echo ============================================
echo   CONTRASENA ACTUALIZADA CON EXITO
echo ============================================
echo.
echo   Usuario:          %TARGET_USER%
echo   Nueva contrasena: %NEW_PASS%
echo.
echo Ahora podes iniciar la app con INICIAR_APP.bat
echo.
pause
