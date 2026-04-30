from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Cliente, TurnoSesion

turnos_bp = Blueprint('turnos', __name__)

@turnos_bp.route('/')
def listar():
    turnos = TurnoSesion.query.order_by(TurnoSesion.fecha_hora_turno.desc()).all()
    return render_template('turnos/listar.html', turnos=turnos)

@turnos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    clientes = Cliente.query.order_by(Cliente.apellido, Cliente.nombre).all()

    if request.method == 'POST':
        cliente_id = int(request.form['cliente_id'])
        fecha_hora = request.form['fecha_hora_turno']
        estado = request.form['estado']
        observacion = request.form.get('observacion', '').strip()

        cliente = Cliente.query.get_or_404(cliente_id)
        
        if estado == 'realizado':
            if cliente.saldo_sesiones <= 0:
                flash('El cliente no tiene saldo de sesiones disponible.', 'danger')
                return redirect(url_for('turnos.nuevo'))
            
            # DESCONTAMOS UNA SESIÓN DEL SALDO DEL CLIENTE
            cliente.saldo_sesiones -= 1

        turno = TurnoSesion(
            cliente_id=cliente_id,
            fecha_hora_turno=datetime.fromisoformat(fecha_hora),
            estado='pendiente',
            observacion=observacion or None,
        )
        db.session.add(turno)
        db.session.commit()
        flash('Turno creado correctamente.', 'success')
        return redirect(url_for('turnos.listar'))
    return render_template('turnos/form.html', turno=None, clientes=clientes)


@turnos_bp.route('/<int:turno_id>/marcar_realizado', methods=['POST'])
def marcar_realizado(turno_id):
    turno = TurnoSesion.query.get_or_404(turno_id)
    
    if turno.estado != 'pendiente':
        flash('Este turno ya fue procesado o cancelado.', 'warning')
        return redirect(url_for('turnos.listar'))
        
    cliente = turno.cliente
    
    # Verificamos si tiene saldo antes de dejarlo realizar la sesión
    if cliente.saldo_sesiones <= 0:
        flash('El cliente no tiene saldo de sesiones disponible para realizar este turno.', 'danger')
        return redirect(url_for('turnos.listar'))
        
    # Cambiamos el estado y descontamos la sesión
    turno.estado = 'realizado'
    cliente.saldo_sesiones -= 1
    
    db.session.commit()
    flash('Turno marcado como realizado. Se descontó una sesión al cliente.', 'success')
    
    return redirect(url_for('turnos.listar'))


@turnos_bp.route('/<int:turno_id>/editar', methods=['GET', 'POST'])
def editar(turno_id):
    turno = TurnoSesion.query.get_or_404(turno_id)
    
    if request.method == 'POST':
        estado_nuevo = request.form['estado']
        estado_viejo = turno.estado
        cliente = turno.cliente
        
        # Si estaba pendiente o cancelado, y lo pasan a realizado -> le descontamos la sesión
        if estado_viejo != 'realizado' and estado_nuevo == 'realizado':
            if cliente.saldo_sesiones <= 0:
                flash('El cliente no tiene saldo disponible.', 'danger')
                return redirect(url_for('turnos.editar', turno_id=turno.id))
            cliente.saldo_sesiones -= 1
            
        # Si estaba realizado y lo pasan a pendiente/cancelado (por error) -> le devolvemos la sesión
        elif estado_viejo == 'realizado' and estado_nuevo != 'realizado':
            cliente.saldo_sesiones += 1
            
        turno.estado = estado_nuevo
        turno.fecha_hora_turno = datetime.fromisoformat(request.form['fecha_hora_turno'])
        turno.observacion = request.form.get('observacion', '').strip()
        
        db.session.commit()
        flash('Turno modificado correctamente.', 'success')
        return redirect(url_for('turnos.listar'))
        
    return render_template('turnos/form.html', turno=turno)

# Atajo rápido usado desde el Dashboard — marca realizado
@turnos_bp.route('/<int:turno_id>/realizar_rapido', methods=['POST'])
def realizar_rapido(turno_id):
    turno = TurnoSesion.query.get_or_404(turno_id)
    if turno.estado == 'pendiente':
        if turno.cliente.saldo_sesiones <= 0:
            flash(f'{turno.cliente.nombre_completo} no tiene sesiones disponibles.', 'danger')
            return redirect(url_for('main.index'))
        turno.estado = 'realizado'
        turno.cliente.saldo_sesiones -= 1
        db.session.commit()
        flash(f'Turno de {turno.cliente.nombre_completo} marcado como realizado.', 'success')
    return redirect(url_for('main.index'))


# Atajo rápido usado desde el Dashboard — cancela el turno
@turnos_bp.route('/<int:turno_id>/cancelar_rapido', methods=['POST'])
def cancelar_rapido(turno_id):
    turno = TurnoSesion.query.get_or_404(turno_id)
    if turno.estado == 'pendiente':
        turno.estado = 'cancelado'
        db.session.commit()
        flash(f'Turno de {turno.cliente.nombre_completo} cancelado.', 'warning')
    return redirect(url_for('main.index'))