from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..extensions import db
from ..models import Producto

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/')
def listar():
    productos = Producto.query.order_by(Producto.nombre).all()
    return render_template('productos/listar.html', productos=productos)

@productos_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    if request.method == 'POST':
        producto = Producto(
            nombre=request.form['nombre'].strip(),
            descripcion=request.form.get('descripcion', '').strip(),  # Guardamos la descripción
            cantidad_sesiones=int(request.form['cantidad_sesiones']),
            precio=float(request.form['precio']),
            activo=('activo' in request.form),
        )
        db.session.add(producto)
        db.session.commit()
        flash('Producto creado correctamente.', 'success')
        return redirect(url_for('productos.listar'))
    return render_template('productos/form.html', producto=None)

@productos_bp.route('/<int:producto_id>/editar', methods=['GET', 'POST'])
def editar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    if request.method == 'POST':
        producto.nombre = request.form['nombre'].strip()
        producto.descripcion = request.form.get('descripcion', '').strip()  # Actualizamos la descripción
        producto.cantidad_sesiones = int(request.form['cantidad_sesiones'])
        producto.precio = float(request.form['precio'])
        producto.activo = ('activo' in request.form)
        db.session.commit()
        flash('Producto actualizado.', 'success')
        return redirect(url_for('productos.listar'))
    return render_template('productos/form.html', producto=producto)

@productos_bp.route('/<int:producto_id>/eliminar', methods=['POST'])
def eliminar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado.', 'success')
    return redirect(url_for('productos.listar'))