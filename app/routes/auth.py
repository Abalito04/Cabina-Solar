from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from ..models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(f'>>> Intentando login con: {username}')
        user = User.query.filter_by(username=username).first()
        print(f'>>> Usuario encontrado: {user}')
        if user:
            print(f'>>> Check password: {user.check_password(password)}')

        if user and user.check_password(password):
            login_user(user)
            print(f'>>> Login exitoso, redirigiendo...')
            return redirect(url_for('main.index'))

        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))