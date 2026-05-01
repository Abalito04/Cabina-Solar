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

4. **Aplicar migraciones**:
   ```bash
   flask db upgrade
   ```

5. **Crear empresa y usuario inicial** (requiere `seed.py` con datos propios):
   ```bash
   python seed.py
   ```

6. **Ejecutar**:
   ```bash
   python run.py
   ```
   Accedé en: `http://127.0.0.1:5000`

## 🔐 Variables de entorno

Creá un archivo `.env` en la raíz con:

```
DATABASE_URL=postgresql://... (o dejarlo vacío para usar SQLite local)
SECRET_KEY=tu-clave-secreta
```

## 📦 Deploy en Railway

El proyecto está configurado para desplegarse automáticamente desde GitHub. Railway ejecuta:
```
flask db upgrade && gunicorn "app:create_app()"
```

## 📱 Próximos pasos
- Panel de administración para gestionar empresas y usuarios
- Roles de usuario (admin / empleado)
- Notificaciones y recordatorios de turnos por email o WhatsApp
