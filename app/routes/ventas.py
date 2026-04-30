from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Cliente, Producto, Venta, Pago

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/')
def listar():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('ventas/listar.html', ventas=ventas)

@ventas_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    clientes = Cliente.query.order_by(Cliente.apellido, Cliente.nombre).all()
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()

    if request.method == 'POST':
        cliente_id = int(request.form['cliente_id'])
        producto_id = int(request.form['producto_id'])
        medio_pago = request.form['medio_pago']
        monto = float(request.form['monto'])
        fecha = request.form.get('fecha')

        producto = Producto.query.get_or_404(producto_id)
        cliente = Cliente.query.get_or_404(cliente_id)

        # SUMAMOS LAS SESIONES AL SALDO DEL CLIENTE
        cliente.saldo_sesiones += producto.cantidad_sesiones
        
        venta = Venta(
            cliente_id=cliente_id,
            producto_id=producto_id,
            sesiones_compradas=producto.cantidad_sesiones,
            total=producto.precio,
            fecha=datetime.fromisoformat(fecha) if fecha else datetime.now(),
        )
        db.session.add(venta)
        db.session.flush()

        pago = Pago(
            venta_id=venta.id,
            medio_pago=medio_pago,
            monto=monto,
            fecha=venta.fecha,
        )
        db.session.add(pago)
        
        # Guardamos la venta, el pago y el nuevo saldo del cliente
        db.session.commit()
        flash('Venta y pago registrados correctamente. Sesiones sumadas al cliente.', 'success')
        return redirect(url_for('ventas.listar'))

    return render_template('ventas/form.html', clientes=clientes, productos=productos)

# app/routes/ventas.py (al final)

@ventas_bp.route('/pago_deuda/<int:cliente_id>', methods=['POST'])
def pago_deuda(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    monto_a_pagar = float(request.form['monto'])
    medio_pago = request.form['medio_pago']
    
    # Verificamos si realmente debe algo
    deuda_total = abs(cliente.saldo_pesos)
    if cliente.saldo_pesos >= 0 or monto_a_pagar <= 0:
        flash('No hay deuda para cobrar o el monto es inválido.', 'warning')
        return redirect(url_for('clientes.detalle', cliente_id=cliente.id))
        
    if monto_a_pagar > deuda_total:
        flash(f'El monto ingresado es mayor a la deuda total (${deuda_total}).', 'danger')
        return redirect(url_for('clientes.detalle', cliente_id=cliente.id))

    # Buscamos las ventas y calculamos cuánto falta pagar de cada una
    # Vamos repartiendo la plata ingresada en las ventas que todavía deben
    ventas = sorted(cliente.ventas, key=lambda v: v.fecha)
    monto_restante = monto_a_pagar
    
    for venta in ventas:
        if monto_restante <= 0:
            break
            
        pagado_en_esta_venta = sum(p.monto for p in venta.pagos)
        falta_pagar_aca = venta.total - pagado_en_esta_venta
        
        if falta_pagar_aca > 0:
            # Si le falta pagar más plata de la que nos dio ahora, aplicamos todo el monto restante a esta venta
            pago_a_aplicar = min(falta_pagar_aca, monto_restante)
            
            nuevo_pago = Pago(
                venta_id=venta.id,
                medio_pago=medio_pago,
                monto=pago_a_aplicar,
                fecha=datetime.now()
            )
            db.session.add(nuevo_pago)
            monto_restante -= pago_a_aplicar
            
    db.session.commit()
    flash(f'Se registró un pago de ${monto_a_pagar} correctamente.', 'success')
    return redirect(url_for('clientes.detalle', cliente_id=cliente.id))
