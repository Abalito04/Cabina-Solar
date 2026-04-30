from datetime import datetime
from .extensions import db


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(80), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    correo = db.Column(db.String(120))
    telefono = db.Column(db.String(30))
    
    # NUEVO: Columna física para almacenar el saldo
    saldo_sesiones = db.Column(db.Integer, nullable=False, default=0)

    ventas = db.relationship('Venta', backref='cliente', cascade='all, delete-orphan', lazy=True)
    turnos = db.relationship('TurnoSesion', backref='cliente', cascade='all, delete-orphan', lazy=True)

    @property
    def nombre_completo(self):
        return f'{self.apellido}, {self.nombre}'
    @property
    def saldo_pesos(self):
        # Sumamos el total de todas las ventas (lo que compró)
        total_comprado = sum(v.total for v in self.ventas)
        
        # Sumamos el total de todos los pagos que hizo en todas sus ventas
        total_pagado = sum(p.monto for v in self.ventas for p in v.pagos)
        
        # La deuda es lo que compró menos lo que pagó
        # Si pagó menos de lo que compró, el número da positivo (debe plata)
        # Lo multiplicamos por -1 para mostrarlo como negativo (ej: -$1500)
        return (total_pagado - total_comprado)


class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255)) 
    cantidad_sesiones = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    activo = db.Column(db.Boolean, default=True)

    ventas = db.relationship('Venta', backref='producto', lazy=True)


class Venta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    sesiones_compradas = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)

    pagos = db.relationship('Pago', backref='venta', cascade='all, delete-orphan', lazy=True)


class Pago(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('venta.id'), nullable=False)
    medio_pago = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.now)
    comprobante = db.Column(db.String(100)) 


class TurnoSesion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    fecha_hora_turno = db.Column(db.DateTime, nullable=False)
    estado = db.Column(db.String(30), nullable=False, default='realizado')
    observacion = db.Column(db.String(200))
    creado_en = db.Column(db.DateTime, nullable=False, default=datetime.now)
