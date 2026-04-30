from flask import Blueprint, render_template
from ..models import Cliente, Producto, Venta, TurnoSesion

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    clientes = Cliente.query.count()
    productos = Producto.query.count()
    ventas = Venta.query.count()
    turnos = TurnoSesion.query.count()
    ultimos_clientes = Cliente.query.order_by(Cliente.id.desc()).limit(5).all()
    return render_template(
        'index.html',
        clientes=clientes,
        productos=productos,
        ventas=ventas,
        turnos=turnos,
        ultimos_clientes=ultimos_clientes,
    )
