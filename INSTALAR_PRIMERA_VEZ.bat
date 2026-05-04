@echo off
chcp 65001 >nul
title Cabina Solar - Instalación inicial
color 0A

echo ============================================
echo   CABINA SOLAR - INSTALACIÓN INICIAL
echo ============================================
echo.

REM ── Verificar Python ──────────────────────────────────
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

REM ── Verificar pip ─────────────────────────────────────
pip --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] pip no está disponible.
    echo Reinstalá Python marcando "Add Python to PATH".
    pause
    exit /b 1
)
echo [OK] pip encontrado.

REM ── Buscar psql (PostgreSQL) ───────────────────────────
echo.
echo Buscando PostgreSQL...
set PSQL_PATH=
for /d %%d in ("C:\Program Files\PostgreSQL\*") do (
    if exist "%%d\bin\psql.exe" set PSQL_PATH=%%d\bin
)
if "%PSQL_PATH%"=="" (
    color 0C
    echo [ERROR] No se encontró PostgreSQL instalado.
    echo.
    echo Por favor instalalo desde:
    echo   https://www.postgresql.org/download/windows/
    echo.
    echo Durante la instalación anotá bien la contraseña
    echo que le ponés al usuario "postgres".
    echo.
    pause
    exit /b 1
)
echo [OK] PostgreSQL encontrado en: %PSQL_PATH%

REM ── Pedir datos de conexión ────────────────────────────
echo.
echo ============================================
echo   CONFIGURACIÓN DE BASE DE DATOS
echo ============================================
echo.
echo Se usará el usuario "postgres" de PostgreSQL.
echo (Es el que creaste al instalar PostgreSQL)
echo.
set /p PG_PASS=Ingresá la contraseña de PostgreSQL: 
set /p DB_NAME=Nombre de la base de datos [cabina_solar]: 
if "%DB_NAME%"=="" set DB_NAME=cabina_solar

REM ── Crear la base de datos ─────────────────────────────
echo.
echo Creando base de datos "%DB_NAME%"...
set PGPASSWORD=%PG_PASS%
"%PSQL_PATH%\psql.exe" -U postgres -c "CREATE DATABASE %DB_NAME%;" 2>nul
if errorlevel 1 (
    echo [AVISO] La base de datos ya existe o hubo un error.
    echo         Si ya existe, se continuará igual.
) else (
    echo [OK] Base de datos "%DB_NAME%" creada.
)

REM ── Crear entorno virtual ──────────────────────────────
echo.
echo Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo [OK] Entorno virtual creado.
) else (
    echo [OK] El entorno virtual ya existe, se omite.
)

REM ── Instalar dependencias ──────────────────────────────
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

REM ── Crear archivo .env automáticamente ───────────────────
echo.
if not exist ".env" (
    echo Creando archivo .env...
    (
        echo DATABASE_URL=postgresql://postgres:%PG_PASS%@localhost:5432/%DB_NAME%
        echo SECRET_KEY=cabina-solar-clave-secreta-%RANDOM%%RANDOM%
    ) > .env
    echo [OK] Archivo .env creado automáticamente.
) else (
    echo [OK] Archivo .env ya existe, no se sobreescribe.
)

REM ── Aplicar migraciones ───────────────────────────────
echo.
echo Aplicando migraciones de base de datos...
set FLASK_APP=run.py
flask db upgrade
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] No se pudieron aplicar las migraciones.
    echo Verificá que la contraseña de PostgreSQL sea correcta
    echo y que el servicio de PostgreSQL esté corriendo.
    echo.
    pause
    exit /b 1
)
echo [OK] Base de datos lista.

echo.
echo ============================================
echo   INSTALACIÓN COMPLETADA CON ÉXITO ✓
echo ============================================
echo.
echo Para iniciar la aplicación usá el archivo:
echo   INICIAR_APP.bat
echo.
pause
