from datetime import datetime, date
from flask import Blueprint, render_template
from ..models import Cliente, Producto, Venta, TurnoSesion, Pago

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    hoy = date.today()

    # Contadores generales
    total_clientes = Cliente.query.count()
    total_productos = Producto.query.count()
    total_ventas = Venta.query.count()

    # Turnos de hoy (todos los turnos cuya fecha sea el dia de hoy)
    turnos_hoy = TurnoSesion.query.filter(
        db_date_trunc(TurnoSesion.fecha_hora_turno) == hoy
    ).order_by(TurnoSesion.fecha_hora_turno).all()

    # Ingresos del dia: suma de todos los pagos hechos hoy
    pagos_hoy = Pago.query.filter(
        db_date_trunc(Pago.fecha) == hoy
    ).all()
    ingresos_hoy = sum(p.monto for p in pagos_hoy)

    # Clientes con deuda pendiente
    clientes_todos = Cliente.query.all()
    clientes_con_deuda = [c for c in clientes_todos if c.saldo_pesos < 0]
    deuda_total = sum(abs(c.saldo_pesos) for c in clientes_con_deuda)

    # Ultimos clientes registrados
    ultimos_clientes = Cliente.query.order_by(Cliente.id.desc()).limit(5).all()

    return render_template(
        'index.html',
        hoy=hoy,
        total_clientes=total_clientes,
        total_productos=total_productos,
        total_ventas=total_ventas,
        turnos_hoy=turnos_hoy,
        ingresos_hoy=ingresos_hoy,
        clientes_con_deuda=clientes_con_deuda,
        deuda_total=deuda_total,
        ultimos_clientes=ultimos_clientes,
    )


def db_date_trunc(column):
    """Helper para comparar solo la fecha (sin hora) en SQLite."""
    from sqlalchemy import func
    return func.date(column)