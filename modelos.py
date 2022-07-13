
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime

db=SQLAlchemy()

class Usuario(db.Model):
    __tablename__="usuario"
    id=db.Column(db.Integer,primary_key=True)
    nombre_usuario=db.Column(db.String(50),unique=True)
    contrasena_usuario=db.Column(db.String(102))
    fecha_creacion=db.Column(db.DateTime,default=datetime.now)
    rol_usuario=db.Column(db.String(20))

    def __init__(self,nombre_usuario,contrasena_usuario,rol_usuario):
        self.nombre_usuario=nombre_usuario
        self.contrasena_usuario=self.crear_contrasena(contrasena_usuario)
        self.rol_usuario=rol_usuario

    def crear_contrasena(self,contrasena_usuario):
        return generate_password_hash(contrasena_usuario,"sha256")

    def verificar_contrasena(self,contrasena_usuario):
        return check_password_hash(self.contrasena_usuario,contrasena_usuario)

    def get_rol(self):
        return self.rol_usuario
    def get_id(self):
        return self.id

class Producto(db.Model):
    __tablename__="producto"
    id=db.Column(db.Integer,primary_key=True)
    nombre_producto=db.Column(db.String(200))
    fecha_creacion=db.Column(db.DateTime,default=datetime.now)
    fecha_actualizacion_producto=db.Column(db.DateTime,default=datetime.now)
    precio_costo_producto=db.Column(db.Float)
    precio_venta_producto=db.Column(db.Float)
    #notapedido=db.relationship('Nota_de_Pedido',backref='notadepedido',lazy=True)
    #notapedido_id=db.Column(db.Integer,db.ForeignKey('notapedido.id'),nullable=False)

    def __init__(self,nombre_producto,precio_costo_producto,precio_venta_producto):
        self.nombre_producto=nombre_producto
        self.precio_costo_producto=precio_costo_producto
        self.precio_venta_producto=precio_venta_producto
        
            
    def get_fecha_actualizacion_producto(self):
        return self.fecha_actualizacion_producto.strftime("%B %d, %Y")
    
    def get_str_nombre(self):
        return str(self.nombre_producto)
    def get_str_pc(self):
        return str(self.precio_costo_producto)
    def get_str_pv(self):
        return str(self.precio_venta_producto)

class Comprador(db.Model):
    __tablename__="comprador"
    id=db.Column(db.Integer,primary_key=True)
    nombre_comprador=db.Column(db.String(30))
    numero_telefono_comprador=db.Column(db.String(9))
    tipo_comprador=db.Column(db.String(15))
    direccion_comprador=db.Column(db.String(200))
    #notapedido=db.relationship('Nota_de_Pedido',backref='notasdepedidos',lazy=True)

    def __init__(self,nombre_comprador,numero_telefono_comprador,tipo_comprador,direccion_comprador):
        self.nombre_comprador=nombre_comprador
        self.numero_telefono_comprador=numero_telefono_comprador
        self.tipo_comprador=tipo_comprador
        self.direccion_comprador=direccion_comprador

class Nota_de_Pedido(db.Model):
    __tablename__="notapedido"
    id=db.Column(db.Integer,primary_key=True)
    fecha_creacion=db.Column(db.DateTime,default=datetime.now)
    nombre_comprador=db.Column(db.String(250))
    nombre_producto=db.Column(db.String(9999))
    total_venta=db.Column(db.Float)
    direccion_comprador=db.Column(db.String(200))
    
    #cantidad=db.Column(db.Float)
    #db.ForeignKey('producto.id')
    #producto_id=db.Column(db.Integer,nullable=False)
    #comprador_id=db.Column(db.Integer,db.ForeignKey('comprador.id'),nullable=False)
    #producto=db.relationship('producto',backref='nombre_producto',lazy='select')
    
    #precio_producto=db.Column(db.Float)
    
    def __init__(self,nombre_producto,total_venta,nombre_comprador,direccion_comprador):
        #self.cantidad=cantidad
        self.nombre_producto=nombre_producto
        #self.precio_producto=precio_producto
        self.total_venta=total_venta
        self.nombre_comprador=nombre_comprador
        self.direccion_comprador=direccion_comprador
        #self.producto_id=producto_id
    

