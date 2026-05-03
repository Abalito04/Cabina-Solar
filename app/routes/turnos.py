from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Cliente, TurnoSesion


turnos_bp = Blueprint('turnos', __name__)

ESTADOS_VALIDOS = {'pendiente', 'realizado', 'cancelado'}


@turnos_bp.route('/')
@login_required
def listar():
    turnos = TurnoSesion.query.join(Cliente)\
        .filter(Cliente.empresa_id == current_user.empresa_id)\
        .order_by(TurnoSesion.fecha_hora_turno.desc()).all()
    return render_template('turnos/listar.html', turnos=turnos)


@turnos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    clientes = Cliente.query.filter_by(empresa_id=current_user.empresa_id)\
        .order_by(Cliente.apellido, Cliente.nombre).all()

    if request.method == 'POST':
        fecha_hora  = request.form['fecha_hora_turno']
        estado      = request.form['estado']
        observacion = request.form.get('observacion', '').strip()

        try:
            cliente_id     = int(request.form['cliente_id'])
            fecha_hora_dt  = datetime.fromisoformat(fecha_hora)
        except ValueError:
            flash('Datos inválidos en el formulario.', 'danger')
            return redirect(url_for('turnos.nuevo'))

        if estado not in ESTADOS_VALIDOS:
            flash('Estado de turno no válido.', 'danger')
            return redirect(url_for('turnos.nuevo'))

        cliente = Cliente.query.filter_by(id=cliente_id, empresa_id=current_user.empresa_id).first_or_404()

        if estado == 'realizado':
            if cliente.saldo_sesiones <= 0:
                flash('El cliente no tiene saldo de sesiones disponible.', 'danger')
                return redirect(url_for('turnos.nuevo'))
            cliente.saldo_sesiones -= 1

        turno = TurnoSesion(
            cliente_id=cliente_id,
            fecha_hora_turno=fecha_hora_dt,
            estado='pendiente',
            observacion=observacion or None,
        )
        db.session.add(turno)
        db.session.commit()
        flash('Turno creado correctamente.', 'success')
        return redirect(url_for('turnos.listar'))
    return render_template('turnos/form.html', turno=None, clientes=clientes)


@turnos_bp.route('/<int:turno_id>/marcar_realizado', methods=['POST'])
@login_required
def marcar_realizado(turno_id):
    turno = TurnoSesion.query.join(Cliente)\
        .filter(TurnoSesion.id == turno_id, Cliente.empresa_id == current_user.empresa_id).first_or_404()

    if turno.estado != 'pendiente':
        flash('Este turno ya fue procesado o cancelado.', 'warning')
        return redirect(url_for('turnos.listar'))

    cliente = turno.cliente

    if cliente.saldo_sesiones <= 0:
        flash('El cliente no tiene saldo de sesiones disponible para realizar este turno.', 'danger')
        return redirect(url_for('turnos.listar'))

    turno.estado = 'realizado'
    cliente.saldo_sesiones -= 1

    db.session.commit()
    flash('Turno marcado como realizado. Se descontó una sesión al cliente.', 'success')
    return redirect(url_for('turnos.listar'))


@turnos_bp.route('/<int:turno_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(turno_id):
    turno = TurnoSesion.query.join(Cliente)\
        .filter(TurnoSesion.id == turno_id, Cliente.empresa_id == current_user.empresa_id).first_or_404()

    if request.method == 'POST':
        estado_nuevo = request.form['estado']
        fecha_hora   = request.form['fecha_hora_turno']

        try:
            fecha_hora_dt = datetime.fromisoformat(fecha_hora)
        except ValueError:
            flash('La fecha y hora ingresada no es válida.', 'danger')
            return redirect(url_for('turnos.editar', turno_id=turno.id))

        if estado_nuevo not in ESTADOS_VALIDOS:
            flash('Estado de turno no válido.', 'danger')
            return redirect(url_for('turnos.editar', turno_id=turno.id))

        estado_viejo = turno.estado
        cliente      = turno.cliente

        if estado_viejo != 'realizado' and estado_nuevo == 'realizado':
            if cliente.saldo_sesiones <= 0:
                flash('El cliente no tiene saldo disponible.', 'danger')
                return redirect(url_for('turnos.editar', turno_id=turno.id))
            cliente.saldo_sesiones -= 1

        elif estado_viejo == 'realizado' and estado_nuevo != 'realizado':
            cliente.saldo_sesiones += 1

        turno.estado           = estado_nuevo
        turno.fecha_hora_turno = fecha_hora_dt
        turno.observacion      = request.form.get('observacion', '').strip()

        db.session.commit()
        flash('Turno modificado correctamente.', 'success')
        return redirect(url_for('turnos.listar'))

    return render_template('turnos/form.html', turno=turno, clientes=None)


@turnos_bp.route('/<int:turno_id>/realizar_rapido', methods=['POST'])
@login_required
def realizar_rapido(turno_id):
    turno = TurnoSesion.query.join(Cliente)\
        .filter(TurnoSesion.id == turno_id, Cliente.empresa_id == current_user.empresa_id).first_or_404()
    if turno.estado == 'pendiente':
        if turno.cliente.saldo_sesiones <= 0:
            flash(f'{turno.cliente.nombre_completo} no tiene sesiones disponibles.', 'danger')
            return redirect(url_for('main.index'))
        turno.estado = 'realizado'
        turno.cliente.saldo_sesiones -= 1
        db.session.commit()
        flash(f'Turno de {turno.cliente.nombre_completo} marcado como realizado.', 'success')
    return redirect(url_for('main.index'))


@turnos_bp.route('/<int:turno_id>/cancelar', methods=['POST'])
@login_required
def cancelar(turno_id):
    turno = TurnoSesion.query.join(Cliente)\
        .filter(TurnoSesion.id == turno_id, Cliente.empresa_id == current_user.empresa_id).first_or_404()

    if turno.estado != 'pendiente':
        flash('Este turno ya fue procesado o cancelado.', 'warning')
        return redirect(url_for('clientes.detalle', cliente_id=turno.cliente_id))

    turno.estado = 'cancelado'
    db.session.commit()
    flash(f'Turno cancelado correctamente.', 'warning')
    return redirect(url_for('clientes.detalle', cliente_id=turno.cliente_id))