from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Producto


productos_bp = Blueprint('productos', __name__)


def validar_producto(nombre, cantidad_sesiones_str, precio_str):
    if not nombre:
        return None, None, 'El nombre del producto es obligatorio.'
    try:
        cantidad_sesiones = int(cantidad_sesiones_str)
        precio = float(precio_str)
    except ValueError:
        return None, None, 'La cantidad de sesiones y el precio deben ser números válidos.'
    if cantidad_sesiones < 1:
        return None, None, 'La cantidad de sesiones debe ser al menos 1.'
    if precio < 0:
        return None, None, 'El precio no puede ser negativo.'
    return cantidad_sesiones, precio, None


@productos_bp.route('/')
@login_required
def listar():
    productos = Producto.query.filter_by(empresa_id=current_user.empresa_id)\
        .order_by(Producto.nombre).all()
    return render_template('productos/listar.html', productos=productos)


@productos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        nombre      = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()

        cantidad_sesiones, precio, error = validar_producto(
            nombre,
            request.form['cantidad_sesiones'],
            request.form['precio']
        )
        if error:
            flash(error, 'danger')
            return redirect(url_for('productos.nuevo'))

        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            cantidad_sesiones=cantidad_sesiones,
            precio=precio,
            activo=('activo' in request.form),
            empresa_id=current_user.empresa_id,
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado correctamente.', 'success')
        return redirect(url_for('productos.listar'))
    return render_template('productos/form.html', producto=None)


@productos_bp.route('/<int:producto_id>/editar', methods=['GET', 'POST'])
@login_required
def editar(producto_id):
    producto = Producto.query.filter_by(id=producto_id, empresa_id=current_user.empresa_id).first_or_404()
    if request.method == 'POST':
        nombre      = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()

        cantidad_sesiones, precio, error = validar_producto(
            nombre,
            request.form['cantidad_sesiones'],
            request.form['precio']
        )
        if error:
            flash(error, 'danger')
            return redirect(url_for('productos.editar', producto_id=producto.id))

        producto.nombre            = nombre
        producto.descripcion       = descripcion
        producto.cantidad_sesiones = cantidad_sesiones
        producto.precio            = precio
        producto.activo            = ('activo' in request.form)
        db.session.commit()
        flash('Producto actualizado.', 'success')
        return redirect(url_for('productos.listar'))
    return render_template('productos/form.html', producto=producto)


@productos_bp.route('/<int:producto_id>/eliminar', methods=['POST'])
@login_required
def eliminar(producto_id):
    producto = Producto.query.filter_by(id=producto_id, empresa_id=current_user.empresa_id).first_or_404()
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado.', 'success')
    return redirect(url_for('productos.listar'))