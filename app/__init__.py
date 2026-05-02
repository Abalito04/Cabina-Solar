import os
from flask import Flask
from .extensions import db, login_manager, migrate
from .routes.main import main_bp
from .routes.clientes import clientes_bp
from .routes.productos import productos_bp
from .routes.ventas import ventas_bp
from .routes.turnos import turnos_bp
from .extensions import db, login_manager, migrate, limiter, csrf  # agregás limiter


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///cabina_solar.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if not app.config['SECRET_KEY']:
        raise RuntimeError("SECRET_KEY no está definida en las variables de entorno")
    app.config['SESSION_COOKIE_SECURE'] = True    # solo HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # no accesible desde JS
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # protección básica CSRF
    app.config['WTF_CSRF_ENABLED'] = True
    csrf.init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    # User loader — Flask-Login lo usa para reconstruir el usuario desde la sesión
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
        #db.create_all()

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
    
    # Al final de create_app(), antes del return:
    @app.before_request
    def require_login():
        from flask_login import current_user
        from flask import request, redirect, url_for
        public = ['auth.login', 'static']
        if not current_user.is_authenticated and request.endpoint not in public:
            return redirect(url_for('auth.login'))

    return app