# Cabina Solar — Sistema de Gestión

Sistema web multi-tenant desarrollado en Flask para administrar clientes, venta de paquetes de sesiones, turnos y control de pagos en un centro de bronceado / cabina solar.

🌐 **Producción**: [cabina-solar-production.up.railway.app](https://cabina-solar-production.up.railway.app)

## 🚀 Funcionalidades

- **Multi-tenant**: Cada empresa tiene su propio espacio de datos aislado con login individual
- **Gestión de Clientes**: Alta, edición y detalle completo por empresa
- **Control de Sesiones**: Cálculo automático de sesiones restantes; no permite turnos si el cliente no tiene saldo
- **Catálogo de Productos**: Paquetes de sesiones configurables con nombre, descripción, cantidad y precio
- **Gestión de Ventas y Pagos**: Registro de ventas, medios de pago (efectivo, transferencia, tarjeta) y control de deudas
- **Control de Turnos**: Cambio rápido de estado (Pendiente → Realizado / Cancelado) con descuento/devolución automática de sesiones
- **Dashboard**: Resumen del día con turnos, ingresos, clientes con deuda y últimos registros
- **Exportación a Excel**: Reporte completo con hojas de clientes, ventas, pagos, turnos y medios de pago
- **PWA**: Instalable en celular como app nativa desde Chrome

## 🛠️ Tecnologías

- **Backend**: Python 3.13 + Flask
- **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo local)
- **ORM**: Flask-SQLAlchemy + Flask-Migrate (Alembic)
- **Autenticación**: Flask-Login
- **Frontend**: HTML5, Jinja2, Bootstrap 5
- **Servidor**: Gunicorn
- **Hosting**: Railway

## 🔒 Seguridad

- Protección CSRF en todos los formularios (Flask-WTF)
- Rate limiting en login: máximo 5 intentos por minuto (Flask-Limiter)
- Cookies de sesión seguras: `SECURE`, `HTTPONLY`, `SAMESITE=Lax`
- Timeout de sesión automático a las 8 horas de inactividad
- Validación de inputs del lado del servidor en todas las rutas
- Variables de entorno obligatorias: la app no arranca sin `SECRET_KEY` ni `DATABASE_URL`
- Páginas de error personalizadas (403, 404, 500)
- Logging de eventos de seguridad (logins, logouts, errores)

## ⚙️ Instalación local

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/Abalito04/Cabina-Solar.git
   cd Cabina-Solar
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   # Windows (Git Bash)
   source venv/Scripts/activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno** — creá un archivo `.env` en la raíz:
DATABASE_URL=sqlite:///cabina_solar.db
SECRET_KEY=una-clave-secreta-larga-y-aleatoria


5. **Aplicar migraciones**:
```bash
flask db upgrade
```

6. **Crear empresa y usuario inicial**:
```bash
python seed.py
```

7. **Ejecutar**:
```bash
python run.py
```
Accedé en: `http://127.0.0.1:5000`

## 📦 Deploy en Railway

El proyecto está configurado para desplegarse automáticamente desde GitHub. Railway ejecuta:
flask db upgrade && gunicorn "app:create_app()"


Las variables de entorno `SECRET_KEY` y `DATABASE_URL` deben estar definidas en el panel de Railway. La app no arranca si alguna falta.

## 📱 Próximos pasos
- Panel de administración para gestionar empresas y usuarios
- Roles de usuario (admin / empleado)
- Notificaciones y recordatorios de turnos por email o WhatsApp
- Paginación en listas de clientes, ventas y turnos      
