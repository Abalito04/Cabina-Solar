@echo off
chcp 65001 >nul
title Cabina Solar - Instalación inicial
color 0A

echo ============================================
echo   CABINA SOLAR - INSTALACIÓN INICIAL
echo ============================================
echo.

REM ── Verificar Python ──────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python no está instalado.
    echo.
    echo Por favor instalá Python desde:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalación marcá la
    echo opción "Add Python to PATH".
    echo.
    pause
    exit /b 1
)
echo [OK] Python encontrado.

REM ── Verificar pip ─────────────────────────────
pip --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] pip no está disponible.
    echo Reinstalá Python marcando "Add Python to PATH".
    pause
    exit /b 1
)
echo [OK] pip encontrado.

REM ── Crear entorno virtual ─────────────────────
echo.
echo Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo [OK] Entorno virtual creado.
) else (
    echo [OK] El entorno virtual ya existe, se omite.
)

REM ── Activar entorno e instalar dependencias ───
echo.
echo Instalando dependencias (puede tardar unos minutos)...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] Hubo un problema instalando las dependencias.
    echo Revisá tu conexión a internet e intentá de nuevo.
    pause
    exit /b 1
)
echo.
echo [OK] Dependencias instaladas correctamente.

REM ── Verificar archivo .env ────────────────────
echo.
if not exist ".env" (
    echo [AVISO] No se encontró el archivo .env
    echo.
    echo Creando archivo .env de ejemplo...
    echo Editalo con tus datos de base de datos antes de iniciar la app.
    echo.
    (
        echo # Configuración de Cabina Solar
        echo # Editá estos valores con tus datos reales
        echo.
        echo DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/cabina_solar
        echo SECRET_KEY=cambia-esto-por-una-clave-secreta-larga
    ) > .env
    echo [OK] Archivo .env creado. Abrilo y completá los datos.
    echo.
    notepad .env
) else (
    echo [OK] Archivo .env encontrado.
)

REM ── Ejecutar migraciones ──────────────────────
echo.
echo Aplicando migraciones de base de datos...
set FLASK_APP=run.py
flask db upgrade
if errorlevel 1 (
    color 0E
    echo.
    echo [AVISO] No se pudieron aplicar las migraciones.
    echo Verificá que PostgreSQL esté corriendo y que los
    echo datos en el archivo .env sean correctos.
    echo.
) else (
    echo [OK] Base de datos lista.
)

echo.
echo ============================================
echo   INSTALACIÓN COMPLETADA
echo ============================================
echo.
echo Para iniciar la aplicación usá el archivo:
echo   INICIAR_APP.bat
echo.
pause
