# Cabina Solar - Sistema de Gestión

Sistema web desarrollado en Flask para administrar clientes, venta de paquetes de sesiones, turnos y control de pagos y deudas en un centro de bronceado / cabina solar.

## 🚀 Funcionalidades Principales

* **Gestión de Clientes**: Alta, edición y detalle completo.
* **Control de Sesiones**: Cálculo automático de "Sesiones Restantes". El sistema no permite agendar turnos realizados si el cliente no tiene saldo.
* **Catálogo de Productos**: Paquetes de sesiones configurables con nombre, descripción, cantidad de sesiones y precio.
* **Historial y Detalle Individual ("Radiografía" del cliente)**:
  * Historial de paquetes comprados.
  * Registro de asistencia y turnos con fecha y hora.
  * Control de pagos realizados y medio de pago usado (efectivo, transferencia, tarjeta).
* **Gestión de Deudas (Saldos a favor/en contra)**:
  * Si un cliente paga menos que el valor total del paquete, el sistema calcula la deuda.
  * Botón rápido para ir cobrando saldos pendientes de a poco.
* **Control de Turnos**: Cambio rápido de estado (Pendiente -> Realizado) que descuenta automáticamente la sesión del saldo del cliente, o devuelve la sesión si el turno se cancela.

## 🛠️ Tecnologías

* **Backend**: Python 3.8+ con Flask
* **Base de Datos**: SQLite + Flask-SQLAlchemy (ORM)
* **Frontend**: HTML5, Jinja2, Bootstrap 5

## ⚙️ Instalación y Uso local

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/tu-usuario/cabina-solar.git
   cd cabina-solar
   ```

2. **Crear y activar un entorno virtual**:
   * En Windows (Git Bash): `source venv/Scripts/activate`
   * En Windows (CMD/PowerShell): `venv\Scripts\activate`
   * En Mac/Linux: `source venv/bin/activate`

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**:
   ```bash
   python run.py
   ```

5. **Acceder**:
   Abrí tu navegador web e ingresá a: `http://127.0.0.1:5000/`

*Nota: La base de datos `cabina_solar.db` se generará automáticamente la primera vez que se ejecute la aplicación. El archivo `.gitignore` previene que la base local se suba al repositorio.*

## 📱 Próximos pasos previstos
- Construcción de rutas API JSON para consumo desde una futura App Android.
- Módulo de reportes diarios/mensuales de caja.
- Login y roles de usuario.