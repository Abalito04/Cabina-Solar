import os
import logging
from flask import Flask, render_template
from datetime import timedelta
from .extensions import db, login_manager, migrate, limiter, csrf
from .routes.main import main_bp
from .routes.clientes import clientes_bp
from .routes.productos import productos_bp
from .routes.ventas import ventas_bp
from .routes.turnos import turnos_bp

logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        raise RuntimeError("DATABASE_URL no está definida en las variables de entorno")

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise RuntimeError("SECRET_KEY no está definida en las variables de entorno")

    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['SESSION_COOKIE_SECURE']      = True
    app.config['SESSION_COOKIE_HTTPONLY']    = True
    app.config['SESSION_COOKIE_SAMESITE']    = 'Lax'
    app.config['WTF_CSRF_ENABLED']           = True

    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(turnos_bp, url_prefix='/turnos')
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    with app.app_context():
        from . import models

    # ── Filtro personalizado: formato de moneda sin decimales con punto como separador de miles
    @app.template_filter('moneda')
    def moneda_filter(value):
        try:
            return f"{int(round(float(value))):,}".replace(',', '.')
        except (ValueError, TypeError):
            return value

    @app.template_global()
    def google_calendar_url(turno):
        from urllib.parse import urlencode
        from datetime import timedelta

        inicio = turno.fecha_hora_turno.strftime('%Y%m%dT%H%M%S')
        fin = (turno.fecha_hora_turno + timedelta(minutes=30)).strftime('%Y%m%dT%H%M%S')

        params = {
            'action': 'TEMPLATE',
            'text': f'Turno Cabina Solar — {turno.cliente.nombre_completo}',
            'dates': f'{inicio}/{fin}',
            'details': turno.observacion or 'Sesión de cabina solar.',
        }
        return f'https://calendar.google.com/calendar/render?{urlencode(params)}'

    @app.before_request
    def require_login():
        from flask_login import current_user
        from flask import request, redirect, url_for
        public = ['auth.login', 'static']
        if not current_user.is_authenticated and request.endpoint not in public:
            return redirect(url_for('auth.login'))

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f'Error 500: {e}')
        return render_template('errors/500.html'), 500

    return app