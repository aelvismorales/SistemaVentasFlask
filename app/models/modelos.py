from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from flask_login import UserMixin,LoginManager,AnonymousUserMixin


db=SQLAlchemy()

login_manager=LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Permisos:
    VER_APLICACION=1
    CREAR_NOTAS=2
    CREAR_PRODUCTOS=4
    ADMINISTRADOR=8  

class Usuario(UserMixin,db.Model):
    __tablename__="usuario"
    id=db.Column(db.Integer,primary_key=True)
    nombre_usuario=db.Column(db.String(50),unique=True)
    contrasena_usuario=db.Column(db.String(128))
    fecha_creacion=db.Column(db.DateTime,default=datetime.now)
    rol_id=db.Column(db.Integer,db.ForeignKey('roles.id',name="fk_rol_usuario"),nullable=False)

    def __init__(self,nombre_usuario,contrasena_usuario,rol_id=None):
        self.nombre_usuario=nombre_usuario
        self.contrasena_usuario=self.crear_contrasena(contrasena_usuario)
        if self.rol_id is None:
            if rol_id is None:
                self.rol_id=1
            else:
                self.rol_id=rol_id

    def crear_contrasena(self,contrasena_usuario):
        return generate_password_hash(contrasena_usuario,"pbkdf2")

    def verificar_contrasena(self,contrasena_usuario):
        return check_password_hash(self.contrasena_usuario,contrasena_usuario)

    def can(self,permiso):
        return self.rol is not None and self.rol.has_permiso(permiso)
    
    def is_admin(self):
        return self.can(Permisos.ADMINISTRADOR)   

    def get_rol(self):
        return self.rol_id
    def get_id(self):
        return self.id

class Role(db.Model):
    __tablename__="roles"
    id=db.Column(db.Integer,primary_key=True)
    nombre_rol=db.Column(db.String(50))
    default=db.Column(db.Boolean,default=False,index=True)
    permisos=db.Column(db.Integer)
    usuarios=db.relationship('Usuario',backref='rol',lazy='dynamic')

    def __init__(self,nombre):
        self.nombre_rol=nombre
        if self.permisos is None:
            self.permisos=0
    
    def __repr__(self):
        return '<Role %r>' % self.nombre_rol
    
    def has_permiso(self,permiso):
        return self.permisos & permiso == permiso
    
    def add_permiso(self,permiso):
        if not self.has_permiso(permiso):
            self.permisos+=permiso

    def remove_permiso(self,permiso):
        if self.has_permiso(permiso):
            self.permisos-=permiso
    
    def reset_permisos(self):
        self.permisos=0
    
    def get_id(self):
        return self.id

    @staticmethod
    def insertar_roles():
        roles={
            'Usuario':[Permisos.VER_APLICACION,Permisos.CREAR_NOTAS,Permisos.CREAR_PRODUCTOS],
            'Administrador':[Permisos.VER_APLICACION,Permisos.CREAR_NOTAS,Permisos.CREAR_PRODUCTOS,Permisos.ADMINISTRADOR]
        }
        default_role='Usuario'
        for r in roles:
            role=Role.query.filter_by(nombre_rol=r).first()
            if role is None:
                role=Role(r)
            role.reset_permisos()
       
            for permiso in roles[r]:
                role.add_permiso(permiso)
            role.default=(role.nombre_rol==default_role)
            db.session.add(role)
        db.session.commit()


class AnonymousUser(AnonymousUserMixin):
    def can(self,permiso):
        return False
    def is_administrador(self):
        return False   
    
login_manager.anonymous_user=AnonymousUser

class Producto(db.Model):
    __tablename__="producto"
    id=db.Column(db.Integer,primary_key=True)
    nombre_producto=db.Column(db.String(200))
    fecha_creacion=db.Column(db.DateTime,default=datetime.now)
    fecha_actualizacion_producto=db.Column(db.DateTime,default=datetime.now)
    precio_costo_producto=db.Column(db.Float)
    precio_venta_producto=db.Column(db.Float)
    stock=db.Column(db.Float)

    def __init__(self,nombre_producto,precio_costo_producto,precio_venta_producto,stock):
        self.nombre_producto=nombre_producto
        self.precio_costo_producto=precio_costo_producto
        self.precio_venta_producto=precio_venta_producto
        self.stock=stock
        
            
    def get_fecha_actualizacion_producto(self):
        return self.fecha_actualizacion_producto.strftime('%d/%m/%Y')
    
    def get_str_nombre(self):
        return str(self.nombre_producto)
    def get_str_pc(self):
        return str(self.precio_costo_producto.__round__(1))
    def get_str_pv(self):
        return str(self.precio_venta_producto.__round__(1))
    def get_stock(self):
        return self.stock

class Comprador(db.Model):
    __tablename__="comprador"
    id=db.Column(db.Integer,primary_key=True)
    nombre_comprador=db.Column(db.String(40))
    numero_telefono_comprador=db.Column(db.String(10))
    tipo_comprador=db.Column(db.String(15))
    direccion_comprador=db.Column(db.String(200))
    dni=db.Column(db.String(20))
    notas=db.relationship('Nota_de_Pedido',backref='notasdepedidos')

    def __init__(self,nombre_comprador,numero_telefono_comprador,direccion_comprador,dni,tipo_comprador='persona'):
        self.nombre_comprador=nombre_comprador
        self.numero_telefono_comprador=numero_telefono_comprador
        self.tipo_comprador=tipo_comprador
        self.direccion_comprador=direccion_comprador
        self.dni=dni
    def get_id(self):
        return self.id
    def get_nombre(self):
        return self.nombre_comprador
    def get_direccion(self):
        return self.direccion_comprador
    def get_telefono(self):
        return self.numero_telefono_comprador
    def get_dni(self):
        return self.dni
    def get_tipo(self):
        return self.tipo_comprador
    

class Nota_de_Pedido(db.Model):
    __tablename__="notapedido"
    id=db.Column(db.Integer,primary_key=True)
    fecha_creacion=db.Column(db.DateTime)
    #fecha_creacion=db.Column(db.DateTime,default=datetime.now)
    nombre_comprador=db.Column(db.String(60))
    nombre_producto=db.Column(db.String(15000))
    total_venta=db.Column(db.Float)
    acuenta=db.Column(db.Float)
    deuda=db.Column(db.Float)
    direccion_comprador=db.Column(db.String(200))
    estado=db.Column(db.String(50))
    fecha_cancelacion=db.Column(db.DateTime)
    comentario=db.Column(db.String(500))
    numero_comprador=db.Column(db.String(20))
    dni_comprador=db.Column(db.String(20))
    comprador_id=db.Column(db.Integer,db.ForeignKey('comprador.id'))

    def get_id(self):
        return self.id
    def get_fecha(self):
        return self.fecha_creacion.strftime('%d/%m/%Y')
    def get_fecha_edit(self):
        return self.fecha_creacion.strftime('%Y-%m-%d')    
    def get_nombre_producto(self):
        return self.nombre_producto
    def get_nombre_comprador(self):
        return self.nombre_comprador
    def get_direccion(self):
        return self.direccion_comprador
    def get_total_venta(self):
        return self.total_venta.__round__(1)
    def get_comprador_id(self):
        return self.comprador_id
    def get_estado(self):
        return self.estado
    def get_fecha_cancelacion(self):
        if self.fecha_cancelacion is not None:
            return self.fecha_cancelacion.strftime('%d/%m/%Y')
        return None
    def get_fecha_cancela(self):
        if self.fecha_cancelacion is not None:
            return self.fecha_cancelacion.strftime('%Y-%m-%d')
        return None
    def get_comentario(self):
        return self.comentario 

    def get_telefono_nota(self):
        return self.numero_comprador

    def get_dni_nota(self):
        return self.dni_comprador
    
    def get_deuda(self):
        return self.deuda
    
    def get_acuenta(self):
        return self.acuenta

    def __init__(self,nombre_producto,total_venta,nombre_comprador,direccion_comprador,estado,numero_comprador,dni_comprador,deuda=0.0,acuenta=0.0,fecha_creacion=datetime.today(),fecha_cancelacion=None,comentario="",comprador_id=None):

        self.nombre_producto=nombre_producto
        self.fecha_creacion=fecha_creacion
        self.total_venta=total_venta
        self.nombre_comprador=nombre_comprador
        self.direccion_comprador=direccion_comprador
        self.estado=estado
        self.notasdepedidos=comprador_id
        self.fecha_cancelacion=fecha_cancelacion
        self.comentario=comentario
        self.numero_comprador=numero_comprador
        self.dni_comprador=dni_comprador
        self.deuda=deuda
        self.acuenta=acuenta

        

