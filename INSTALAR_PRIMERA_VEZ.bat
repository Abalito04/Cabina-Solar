@echo off
chcp 1252 >nul
title Cabina Solar - Instalacion inicial
color 0A

echo ============================================
echo   CABINA SOLAR - INSTALACION INICIAL
echo ============================================
echo.

REM -- Verificar Python --
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python no esta instalado.
    echo.
    echo Por favor instala Python desde:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANTE: Durante la instalacion marca la
    echo opcion "Add Python to PATH".
    echo.
    pause
    exit /b 1
)
echo [OK] Python encontrado.

REM -- Verificar pip --
pip --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] pip no esta disponible.
    echo Reinstala Python marcando "Add Python to PATH".
    pause
    exit /b 1
)
echo [OK] pip encontrado.

REM -- Buscar PostgreSQL --
echo.
echo Buscando PostgreSQL...
set PSQL_PATH=
for /d %%d in ("C:\Program Files\PostgreSQL\*") do (
    if exist "%%d\bin\psql.exe" set PSQL_PATH=%%d\bin
)
if "%PSQL_PATH%"=="" (
    color 0C
    echo [ERROR] No se encontro PostgreSQL instalado.
    echo.
    echo Por favor instalalo desde:
    echo   https://www.postgresql.org/download/windows/
    echo.
    echo Durante la instalacion anota bien la contrasena
    echo que le pones al usuario "postgres".
    echo.
    pause
    exit /b 1
)
echo [OK] PostgreSQL encontrado en: %PSQL_PATH%

REM -- Pedir datos de PostgreSQL --
echo.
echo ============================================
echo   CONFIGURACION DE BASE DE DATOS
echo ============================================
echo.
echo Se usara el usuario "postgres" de PostgreSQL.
echo (Es el que creaste al instalar PostgreSQL)
echo.
set /p PG_PASS=Ingresa la contrasena de PostgreSQL: 
set /p DB_NAME=Nombre de la base de datos (Enter = cabina_solar): 
if "%DB_NAME%"=="" set DB_NAME=cabina_solar

REM -- Pedir datos del admin de la app --
echo.
echo ============================================
echo   USUARIO ADMINISTRADOR DE LA APP
echo ============================================
echo.
echo Este es el usuario con el que vas a entrar a Cabina Solar.
echo.
set /p ADMIN_USER=Nombre de usuario (Enter = Admin): 
if "%ADMIN_USER%"=="" set ADMIN_USER=Admin
set /p ADMIN_PASS=Contrasena para el administrador: 
if "%ADMIN_PASS%"=="" (
    color 0E
    echo [AVISO] No ingresaste contrasena. Se usara "Admin1234" por defecto.
    set ADMIN_PASS=Admin1234
)

REM -- Crear la base de datos --
echo.
echo Creando base de datos "%DB_NAME%"...
set PGPASSWORD=%PG_PASS%
"%PSQL_PATH%\psql.exe" -U postgres -c "CREATE DATABASE %DB_NAME%;" 2>nul
if errorlevel 1 (
    echo [AVISO] La base de datos ya existe o hubo un error. Se continua igual.
) else (
    echo [OK] Base de datos "%DB_NAME%" creada.
)

REM -- Crear entorno virtual --
echo.
echo Creando entorno virtual...
if not exist "venv" (
    python -m venv venv
    echo [OK] Entorno virtual creado.
) else (
    echo [OK] El entorno virtual ya existe, se omite.
)

REM -- Instalar dependencias --
echo.
echo Instalando dependencias (puede tardar unos minutos)...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] Hubo un problema instalando las dependencias.
    echo Revisa tu conexion a internet e intenta de nuevo.
    pause
    exit /b 1
)
echo.
echo [OK] Dependencias instaladas correctamente.

REM -- Crear archivo .env --
echo.
if not exist ".env" (
    echo Creando archivo .env...
    (
        echo DATABASE_URL=postgresql://postgres:%PG_PASS%@localhost:5432/%DB_NAME%
        echo SECRET_KEY=cabina-solar-clave-secreta-%RANDOM%%RANDOM%
    ) > .env
    echo [OK] Archivo .env creado automaticamente.
) else (
    echo [OK] Archivo .env ya existe, no se sobreescribe.
)

REM -- Aplicar migraciones --
echo.
echo Aplicando migraciones de base de datos...
set FLASK_APP=run.py
flask db upgrade
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] No se pudieron aplicar las migraciones.
    echo Verifica que la contrasena de PostgreSQL sea correcta
    echo y que el servicio de PostgreSQL este corriendo.
    echo.
    pause
    exit /b 1
)
echo [OK] Base de datos lista.

REM -- Crear usuario admin --
echo.
echo Creando usuario administrador...
(
    echo from dotenv import load_dotenv
    echo load_dotenv^(^)
    echo from app import create_app
    echo from app.extensions import db
    echo from app.models import Empresa, User
    echo app = create_app^(^)
    echo with app.app_context^(^):
    echo     if not Empresa.query.first^(^):
    echo         empresa = Empresa^(nombre='Cabina Solar', slug='cabina-solar', activa=True^)
    echo         db.session.add^(empresa^)
    echo         db.session.flush^(^)
    echo     else:
    echo         empresa = Empresa.query.first^(^)
    echo     if not User.query.filter_by^(username='%ADMIN_USER%'^).first^(^):
    echo         user = User^(empresa_id=empresa.id, username='%ADMIN_USER%', es_admin=True^)
    echo         user.set_password^('%ADMIN_PASS%'^)
    echo         db.session.add^(user^)
    echo         db.session.commit^(^)
    echo         print^('Usuario creado correctamente'^)
    echo     else:
    echo         print^('El usuario ya existe, se omite'^)
) > _seed_temp.py
python _seed_temp.py
if errorlevel 1 (
    color 0C
    echo.
    echo [ERROR] No se pudo crear el usuario administrador.
    del _seed_temp.py >nul 2>&1
    pause
    exit /b 1
)
del _seed_temp.py >nul 2>&1
echo [OK] Usuario "%ADMIN_USER%" creado.

echo.
echo ============================================
echo   INSTALACION COMPLETADA CON EXITO
echo ============================================
echo.
echo Datos de acceso a la aplicacion:
echo   Usuario:    %ADMIN_USER%
echo   Contrasena: %ADMIN_PASS%
echo.
echo Para iniciar la aplicacion usa el archivo:
echo   INICIAR_APP.bat
echo.
pause
