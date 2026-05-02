import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from ..extensions import limiter

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session.permanent = True
            login_user(user)
            logger.info(f'Login exitoso — usuario: {username} — IP: {request.remote_addr}')
            return redirect(url_for('main.index'))

        logger.warning(f'Login fallido — usuario: {username} — IP: {request.remote_addr}')
        flash('Usuario o contraseña incorrectos.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    logger.info(f'Logout — usuario: {username}')
    return redirect(url_for('auth.login'))