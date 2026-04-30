from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Producto

productos_bp = Blueprint('productos', __name__)

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
        producto = Producto(
            nombre=request.form['nombre'].strip(),
            descripcion=request.form.get('descripcion', '').strip(),
            cantidad_sesiones=int(request.form['cantidad_sesiones']),
            precio=float(request.form['precio']),
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
        producto.nombre = request.form['nombre'].strip()
        producto.descripcion = request.form.get('descripcion', '').strip()
        producto.cantidad_sesiones = int(request.form['cantidad_sesiones'])
        producto.precio = float(request.form['precio'])
        producto.activo = ('activo' in request.form)
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