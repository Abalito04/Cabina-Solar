from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Cliente

clientes_bp = Blueprint('clientes', __name__)


@clientes_bp.route('/')
def listar():
    clientes = Cliente.query.order_by(Cliente.apellido, Cliente.nombre).all()
    return render_template('clientes/listar.html', clientes=clientes)


@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        dni = request.form['dni'].strip()
        existente = Cliente.query.filter_by(dni=dni).first()
        if existente:
            flash('Ya existe un cliente con ese DNI.', 'danger')
            return redirect(url_for('clientes.nuevo'))

        cliente = Cliente(
            nombre=request.form['nombre'].strip(),
            apellido=request.form['apellido'].strip(),
            dni=dni,
            correo=request.form.get('correo', '').strip(),
            telefono=request.form.get('telefono', '').strip(),
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado correctamente.', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/form.html', cliente=None)


@clientes_bp.route('/<int:cliente_id>/editar', methods=['GET', 'POST'])
def editar(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    if request.method == 'POST':
        dni = request.form['dni'].strip()
        existente = Cliente.query.filter(Cliente.dni == dni, Cliente.id != cliente.id).first()
        if existente:
            flash('Ya existe otro cliente con ese DNI.', 'danger')
            return redirect(url_for('clientes.editar', cliente_id=cliente.id))

        cliente.nombre = request.form['nombre'].strip()
        cliente.apellido = request.form['apellido'].strip()
        cliente.dni = dni
        cliente.correo = request.form.get('correo', '').strip()
        cliente.telefono = request.form.get('telefono', '').strip()
        db.session.commit()
        flash('Cliente actualizado.', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/form.html', cliente=cliente)


@clientes_bp.route('/<int:cliente_id>/eliminar', methods=['POST'])
def eliminar(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado.', 'success')
    return redirect(url_for('clientes.listar'))

@clientes_bp.route('/<int:cliente_id>/detalle')
def detalle(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    
    # Ordenamos las ventas y turnos por fecha (del más nuevo al más viejo)
    ventas = sorted(cliente.ventas, key=lambda v: v.fecha, reverse=True)
    turnos = sorted(cliente.turnos, key=lambda t: t.fecha_hora_turno, reverse=True)
    
    return render_template(
        'clientes/detalle.html', 
        cliente=cliente, 
        ventas=ventas, 
        turnos=turnos
    )