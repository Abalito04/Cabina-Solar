from datetime import datetime, date
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Cliente, Producto, Venta, TurnoSesion, Pago


main_bp = Blueprint('main', __name__)

DIAS = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
MESES = ['enero','febrero','marzo','abril','mayo','junio',
         'julio','agosto','septiembre','octubre','noviembre','diciembre']


@main_bp.route('/')
@login_required
def index():
    hoy = date.today()
    fecha_texto = f"{DIAS[hoy.weekday()]} {hoy.day} de {MESES[hoy.month - 1]} de {hoy.year}"
    eid = current_user.empresa_id

    total_clientes = Cliente.query.filter_by(empresa_id=eid).count()
    total_productos = Producto.query.filter_by(empresa_id=eid).count()
    total_ventas = Venta.query.join(Cliente).filter(Cliente.empresa_id == eid).count()

    turnos_hoy = TurnoSesion.query.join(Cliente).filter(
        Cliente.empresa_id == eid,
        db_date_trunc(TurnoSesion.fecha_hora_turno) == hoy
    ).order_by(TurnoSesion.fecha_hora_turno).all()

    pagos_hoy = Pago.query.join(Venta).join(Cliente).filter(
        Cliente.empresa_id == eid,
        db_date_trunc(Pago.fecha) == hoy
    ).all()
    ingresos_hoy = sum(p.monto for p in pagos_hoy)

    clientes_todos = Cliente.query.filter_by(empresa_id=eid).all()
    clientes_con_deuda = [c for c in clientes_todos if c.saldo_pesos < 0]
    deuda_total = sum(abs(c.saldo_pesos) for c in clientes_con_deuda)

    ultimos_clientes = Cliente.query.filter_by(empresa_id=eid)\
        .order_by(Cliente.id.desc()).limit(5).all()

    return render_template(
        'index.html',
        hoy=hoy,
        fecha_texto=fecha_texto,
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