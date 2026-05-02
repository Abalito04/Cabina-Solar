import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Cliente


clientes_bp = Blueprint('clientes', __name__)


def validar_cliente(nombre, apellido, dni, correo):
    if not nombre or not apellido:
        return 'Nombre y apellido son obligatorios.'
    if not dni.isdigit() or not (7 <= len(dni) <= 9):
        return 'El DNI debe tener entre 7 y 9 dígitos numéricos.'
    if correo and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', correo):
        return 'El correo ingresado no es válido.'
    return None


@clientes_bp.route('/')
@login_required
def listar():
    clientes = Cliente.query.filter_by(empresa_id=current_user.empresa_id)\
        .order_by(Cliente.apellido, Cliente.nombre).all()
    return render_template('clientes/listar.html', clientes=clientes)


@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre  = request.form['nombre'].strip()
        apellido = request.form['apellido'].strip()
        dni     = request.form['dni'].strip()
        correo  = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()

        error = validar_cliente(nombre, apellido, dni, correo)
        if error:
            flash(error, 'danger')
            return redirect(url_for('clientes.nuevo'))

        existente = Cliente.query.filter_by(dni=dni, empresa_id=current_user.empresa_id).first()
        if existente:
            flash('Ya existe un cliente con ese DNI.', 'danger')
            return redirect(url_for('clientes.nuevo'))

        cliente = Cliente(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            correo=correo,
            telefono=telefono,
            empresa_id=current_user.empresa_id,
        )
        db.session.add(cliente)
        db.session.commit()
        flash('Cliente creado correctamente.', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/form.html', cliente=None)


@clientes_bp.route('/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(cliente_id):
    cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first_or_404()
    if request.method == 'POST':
        nombre   = request.form['nombre'].strip()
        apellido = request.form['apellido'].strip()
        dni      = request.form['dni'].strip()
        correo   = request.form.get('correo', '').strip()
        telefono = request.form.get('telefono', '').strip()

        error = validar_cliente(nombre, apellido, dni, correo)
        if error:
            flash(error, 'danger')
            return redirect(url_for('clientes.editar', cliente_id=cliente.id))

        existente = Cliente.query.filter(
            Cliente.dni == dni,
            Cliente.id != cliente.id,
            Cliente.empresa_id == current_user.empresa_id
        ).first()
        if existente:
            flash('Ya existe otro cliente con ese DNI.', 'danger')
            return redirect(url_for('clientes.editar', cliente_id=cliente.id))

        cliente.nombre   = nombre
        cliente.apellido = apellido
        cliente.dni      = dni
        cliente.correo   = correo
        cliente.telefono = telefono
        db.session.commit()
        flash('Cliente actualizado.', 'success')
        return redirect(url_for('clientes.listar'))
    return render_template('clientes/form.html', cliente=cliente)


@clientes_bp.route('/<int:cliente_id>/eliminar', methods=['POST'])
@login_required
def eliminar(cliente_id):
    cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first_or_404()
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente eliminado.', 'success')
    return redirect(url_for('clientes.listar'))


@clientes_bp.route('/<int:cliente_id>/detalle')
@login_required
def detalle(cliente_id):
    cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first_or_404()

    ventas = sorted(cliente.ventas, key=lambda v: v.fecha, reverse=True)
    turnos = sorted(cliente.turnos, key=lambda t: t.fecha_hora_turno, reverse=True)

    return render_template(
        'clientes/detalle.html',
        cliente=cliente,
        ventas=ventas,
        turnos=turnos
    )