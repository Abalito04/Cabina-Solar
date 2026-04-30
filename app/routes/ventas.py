from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from ..extensions import db
from ..models import Cliente, Producto, Venta, Pago

ventas_bp = Blueprint('ventas', __name__)


@ventas_bp.route('/')
def listar():
    # Filtros opcionales
    cliente_id = request.args.get('cliente_id', type=int)
    medio_pago = request.args.get('medio_pago', '')
    fecha_desde = request.args.get('fecha_desde', '')
    fecha_hasta = request.args.get('fecha_hasta', '')

    query = Venta.query

    if cliente_id:
        query = query.filter(Venta.cliente_id == cliente_id)
    if fecha_desde:
        query = query.filter(Venta.fecha >= datetime.fromisoformat(fecha_desde))
    if fecha_hasta:
        query = query.filter(Venta.fecha <= datetime.fromisoformat(fecha_hasta + 'T23:59:59'))
    if medio_pago:
        query = query.join(Pago).filter(Pago.medio_pago == medio_pago)

    ventas = query.order_by(Venta.fecha.desc()).all()
    clientes = Cliente.query.order_by(Cliente.apellido, Cliente.nombre).all()
    total_filtrado = sum(v.total for v in ventas)

    return render_template(
        'ventas/listar.html',
        ventas=ventas,
        clientes=clientes,
        cliente_id=cliente_id,
        medio_pago=medio_pago,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        total_filtrado=total_filtrado,
    )


@ventas_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    cliente_preseleccionado = request.args.get('cliente_id', type=int)
    clientes = Cliente.query.order_by(Cliente.apellido, Cliente.nombre).all()
    productos = Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()

    if request.method == 'POST':
        cliente_id = int(request.form['cliente_id'])
        producto_id = int(request.form['producto_id'])
        medio_pago = request.form['medio_pago']
        monto = float(request.form['monto'])

        producto = Producto.query.get_or_404(producto_id)
        cliente = Cliente.query.get_or_404(cliente_id)

        cliente.saldo_sesiones += producto.cantidad_sesiones

        venta = Venta(
            cliente_id=cliente_id,
            producto_id=producto_id,
            sesiones_compradas=producto.cantidad_sesiones,
            total=producto.precio,
            fecha=datetime.now(),
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
        db.session.commit()
        flash('Venta y pago registrados correctamente. Sesiones sumadas al cliente.', 'success')
        return redirect(url_for('ventas.listar'))

    return render_template(
        'ventas/form.html',
        clientes=clientes,
        productos=productos,
        cliente_preseleccionado=cliente_preseleccionado,
    )


@ventas_bp.route('/pago_deuda/<int:cliente_id>', methods=['POST'])
def pago_deuda(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    monto_a_pagar = float(request.form['monto'])
    medio_pago = request.form['medio_pago']

    deuda_total = abs(cliente.saldo_pesos)
    if cliente.saldo_pesos >= 0 or monto_a_pagar <= 0:
        flash('No hay deuda para cobrar o el monto es inválido.', 'warning')
        return redirect(url_for('clientes.detalle', cliente_id=cliente.id))

    if monto_a_pagar > deuda_total:
        flash(f'El monto ingresado es mayor a la deuda total (${deuda_total:.2f}).', 'danger')
        return redirect(url_for('clientes.detalle', cliente_id=cliente.id))

    ventas = sorted(cliente.ventas, key=lambda v: v.fecha)
    monto_restante = monto_a_pagar

    for venta in ventas:
        if monto_restante <= 0:
            break
        pagado_en_esta_venta = sum(p.monto for p in venta.pagos)
        falta_pagar_aca = venta.total - pagado_en_esta_venta
        if falta_pagar_aca > 0:
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
    flash(f'Se registró un pago de ${monto_a_pagar:.2f} correctamente.', 'success')
    return redirect(url_for('clientes.detalle', cliente_id=cliente.id))


# ─── EXPORTACIÓN A EXCEL ──────────────────────────────────────────────────────

@ventas_bp.route('/exportar/excel')
def exportar_excel():
    wb = openpyxl.Workbook()

    estilo_header = Font(bold=True, color='FFFFFF')
    fill_header = PatternFill(fill_type='solid', fgColor='2563EB')
    alineacion_centro = Alignment(horizontal='center')

    def crear_hoja(wb, nombre, columnas, filas):
        ws = wb.create_sheet(title=nombre)
        for col_idx, col_nombre in enumerate(columnas, 1):
            celda = ws.cell(row=1, column=col_idx, value=col_nombre)
            celda.font = estilo_header
            celda.fill = fill_header
            celda.alignment = alineacion_centro
        for fila_idx, fila in enumerate(filas, 2):
            for col_idx, valor in enumerate(fila, 1):
                ws.cell(row=fila_idx, column=col_idx, value=valor)
        return ws

    # Hoja 1: Clientes
    clientes = Cliente.query.order_by(Cliente.apellido).all()
    crear_hoja(wb, 'Clientes', 
        ['ID', 'Apellido', 'Nombre', 'DNI', 'Correo', 'Teléfono', 'Sesiones Restantes', 'Deuda $'],
        [(c.id, c.apellido, c.nombre, c.dni, c.correo, c.telefono,
          c.saldo_sesiones, round(abs(c.saldo_pesos), 2) if c.saldo_pesos < 0 else 0)
         for c in clientes]
    )

    # Hoja 2: Ventas
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    crear_hoja(wb, 'Ventas',
        ['ID', 'Fecha', 'Cliente', 'Producto', 'Sesiones', 'Total $'],
        [(v.id, v.fecha.strftime('%d/%m/%Y %H:%M'), v.cliente.nombre_completo,
          v.producto.nombre, v.sesiones_compradas, v.total)
         for v in ventas]
    )

    # Hoja 3: Pagos
    pagos = Pago.query.order_by(Pago.fecha.desc()).all()
    crear_hoja(wb, 'Pagos',
        ['ID', 'Fecha', 'Cliente', 'Venta ID', 'Medio de Pago', 'Monto $'],
        [(p.id, p.fecha.strftime('%d/%m/%Y %H:%M'), p.venta.cliente.nombre_completo,
          p.venta_id, p.medio_pago, p.monto)
         for p in pagos]
    )

    # Hoja 4: Turnos
    turnos = TurnoSesion.query.order_by(TurnoSesion.fecha_hora_turno.desc()).all()
    from ..models import TurnoSesion as TS
    crear_hoja(wb, 'Turnos',
        ['ID', 'Fecha y Hora', 'Cliente', 'Estado', 'Observación'],
        [(t.id, t.fecha_hora_turno.strftime('%d/%m/%Y %H:%M'), t.cliente.nombre_completo,
          t.estado, t.observacion or '')
         for t in turnos]
    )

    # Hoja 5: Productos
    productos = Producto.query.order_by(Producto.nombre).all()
    crear_hoja(wb, 'Productos',
        ['ID', 'Nombre', 'Descripción', 'Sesiones', 'Precio $', 'Activo'],
        [(p.id, p.nombre, p.descripcion or '', p.cantidad_sesiones, p.precio,
          'Sí' if p.activo else 'No')
         for p in productos]
    )

    # Borramos la hoja en blanco que crea openpyxl por defecto
    if 'Sheet' in wb.sheetnames:
        del wb['Sheet']

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    nombre_archivo = f'cabina_solar_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'

    return send_file(
        buffer,
        as_attachment=True,
        download_name=nombre_archivo,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )