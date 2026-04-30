from flask import Flask
from .extensions import db
from .routes.main import main_bp
from .routes.clientes import clientes_bp
from .routes.productos import productos_bp
from .routes.ventas import ventas_bp
from .routes.turnos import turnos_bp


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cabina_solar.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'cambiar-por-una-clave-segura'

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(clientes_bp, url_prefix='/clientes')
    app.register_blueprint(productos_bp, url_prefix='/productos')
    app.register_blueprint(ventas_bp, url_prefix='/ventas')
    app.register_blueprint(turnos_bp, url_prefix='/turnos')

    with app.app_context():
        from . import models
        db.create_all()

    return app
