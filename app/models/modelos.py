from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime,timezone,timedelta
from flask_login import UserMixin,LoginManager,AnonymousUserMixin
from sqlalchemy import func

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
    nickname=db.Column(db.String(50),unique=True)
    contrasena_usuario=db.Column(db.String(128))
    fecha_creacion=db.Column(db.DateTime,default=datetime.now)
    rol_id=db.Column(db.Integer,db.ForeignKey('roles.id',name="fk_rol_usuario"),nullable=False)
    detalles_caja = db.relationship('Detalle_Caja',backref='usuario',lazy='dynamic')

    def __init__(self,nombre_usuario,contrasena_usuario,nickname,rol_id=None):
        self.nombre_usuario=nombre_usuario
        self.nickname=nickname
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
    
    def get_nombre(self):
        return self.nombre_usuario
    def is_admin(self):
        return self.can(Permisos.ADMINISTRADOR)   

    def get_rol(self):
        return self.rol_id
    def get_id(self):
        return self.id
    def get_nickname(self):
        return self.nickname

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
    fecha_creacion=db.Column(db.DateTime,default=datetime.now(timezone.utc)-timedelta(hours=5))
    fecha_actualizacion_producto=db.Column(db.DateTime,default=datetime.now(timezone.utc)-timedelta(hours=5))
    precio_costo_producto=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    precio_venta_producto=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    stock=db.Column(db.Numeric(precision=10,scale=2),nullable=False)

    def __init__(self,nombre_producto,precio_costo_producto,precio_venta_producto,stock):
        self.nombre_producto=nombre_producto
        self.precio_costo_producto=precio_costo_producto
        self.precio_venta_producto=precio_venta_producto
        self.stock=stock
    
    def __repr__(self) -> str:
        return '<Producto %r, precio_venta: %.2f, precio_costo: %.2f>' % (self.nombre_producto,self.precio_venta_producto,self.precio_costo_producto)
            
    
    def get_fecha_actualizacion_producto(self):
        return self.fecha_actualizacion_producto
    
    def get_str_nombre(self):
        return str(self.nombre_producto)
    def get_str_pc(self):
        return str(self.precio_costo_producto)
    def get_str_pv(self):
        return str(self.precio_venta_producto)
    def get_stock(self):
        return self.stock

    def get_json(self):
        json={"id":self.id,"nombre_producto":self.nombre_producto,"precio_costo_producto":self.precio_costo_producto,"precio_venta_producto":self.precio_venta_producto,"stock":self.stock,"fecha_actualizacion_producto":self.fecha_actualizacion_producto.strftime('%d/%m/%Y'),"fecha_creacion":self.fecha_creacion.strftime('%d/%m/%Y')}
        return json if json is not None else {}
    
    @staticmethod
    def from_dict(data):
        producto=Producto(data['nombre_producto'],data['precio_costo_producto'],data['precio_venta_producto'],data['stock'])
        producto.id=data['id']
        producto.fecha_creacion=data['fecha_creacion']
        producto.fecha_actualizacion_producto=data['fecha_actualizacion_producto']
        return producto

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
    
#TODO COLUMNAS DE INPUTS DE PAGO Y DEUDA
class Nota_de_Pedido(db.Model):
    __tablename__="notapedido"
    id=db.Column(db.Integer,primary_key=True)
    fecha_creacion=db.Column(db.DateTime,default=datetime.now(timezone.utc)-timedelta(hours=5))
    nombre_comprador=db.Column(db.String(60))
    nombre_producto=db.Column(db.String(15000))

    total_venta=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    bool_acuenta=db.Column(db.Boolean,default=False) #Este valor va a ser True si el cliente paga algo al momento de la venta y si acuenta es mayor a 0 y si acuenta y total_venta son iguales es False
    acuenta=db.Column(db.Numeric(precision=10,scale=2),nullable=False) # Pago inicial, este valor va a ir aumentando con dada pago adicional
    deuda=db.Column(db.Numeric(precision=10,scale=2),nullable=False) # Deuda total, este valor va a ir disminuyendo con cada pago adicional
    bool_deuda=db.Column(db.Boolean,default=False) #Este valor va a ser True si el cliente no paga nada al momento de la venta y si deuda es mayor a 0.

    direccion_comprador=db.Column(db.String(200))
    estado=db.Column(db.String(50))
    fecha_cancelacion=db.Column(db.DateTime)
    comentario=db.Column(db.String(500))
    numero_comprador=db.Column(db.String(20))
    dni_comprador=db.Column(db.String(20))

    vuelto=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoEfectivo=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoVisa=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoBBVA=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoBCP=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoYape=db.Column(db.Numeric(precision=10,scale=2),nullable=False)



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
    
    def get_vuelto(self):
        return self.vuelto
    
    def get_pagoEfectivo(self):
        return self.pagoEfectivo
    
    def get_pagoVisa(self):
        return self.pagoVisa
    
    def get_pagoBBVA(self):
        return self.pagoBBVA
    
    def get_pagoBCP(self):
        return self.pagoBCP
    
    def get_pagoYape(self):
        return self.pagoYape
    
    def get_json(self):
        json = {"id":self.id, "fecha_creacion":self.fecha_creacion.strftime('%d/%m/%Y'), "nombre_producto":self.nombre_producto, "nombre_comprador":self.nombre_comprador, "direccion_comprador":self.direccion_comprador, "total_venta":self.total_venta, "estado":self.estado, 
                "fecha_cancelacion":self.fecha_cancelacion.strftime('%d/%m/%Y') if self.fecha_cancelacion is not None else None, "comentario":self.comentario, "numero_comprador":self.numero_comprador, "dni_comprador":self.dni_comprador, "deuda":self.deuda, "acuenta":self.acuenta,
                "bool_acuenta":self.bool_acuenta,"bool_deuda":self.bool_deuda,"vuelto":self.vuelto, "pagoVisa":self.pagoVisa, "pagoEfectivo":self.pagoEfectivo, "pagoBBVA":self.pagoBBVA, "pagoBCP":self.pagoBCP, "pagoYape":self.pagoYape}

        return json if json is not None else {}
    def get_deuda(self):
        return self.deuda
    def get_bool_deuda(self):
        return self.bool_deuda

    def __init__(self,nombre_producto,total_venta,nombre_comprador,direccion_comprador,estado,numero_comprador,dni_comprador,deuda=0.0,acuenta=0.0,fecha_cancelacion=None,comentario="",comprador_id=None,vuelto=0.00,pagoVisa=0.00,pagoEfectivo=0.00,pagoBBVA=0.00,pagoBCP=0.00,pagoYape=0.00,bool_acuenta=False,bool_deuda=False):

        self.nombre_comprador=nombre_comprador
        self.direccion_comprador=direccion_comprador
        self.dni_comprador=dni_comprador
        self.numero_comprador=numero_comprador
        self.total_venta=total_venta
        self.estado=estado
        self.nombre_producto=nombre_producto

        self.vuelto=vuelto
        self.pagoVisa=pagoVisa
        self.pagoEfectivo=pagoEfectivo
        self.pagoBBVA=pagoBBVA
        self.pagoBCP=pagoBCP
        self.pagoYape=pagoYape

        
        self.comprador_id=comprador_id
        self.fecha_cancelacion=fecha_cancelacion
        self.comentario=comentario
        self.deuda=deuda
        self.acuenta=acuenta

        self.bool_deuda=bool_deuda
        self.bool_acuenta=bool_acuenta
        

class Detalle_Caja(db.Model):
    __tablename__="detalle_caja"
    id=db.Column(db.Integer,primary_key=True)
    fecha_creacion=db.Column(db.DateTime)
    nota_id = db.Column(db.Integer,nullable=True)
    #nota_dinero = db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    comentario=db.Column(db.String(250))
    #monto=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    tipo=db.Column(db.String(20))
    usuario_id=db.Column(db.Integer,db.ForeignKey('usuario.id'))
    anulado=db.Column(db.Boolean,default=False) # Si es que anulan la salida de dinero
    pagoEfectivo=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoVisa=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoBBVA=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoBCP=db.Column(db.Numeric(precision=10,scale=2),nullable=False)
    pagoYape=db.Column(db.Numeric(precision=10,scale=2),nullable=False)

    def __init__(self,fecha_creacion,comentario,tipo,usuario_id,pagoEfectivo,pagoVisa,pagoBBVA,pagoBCP,pagoYape,nota_id=None):
        self.fecha_creacion=fecha_creacion
        #self.nota_dinero=nota_dinero
        self.comentario=comentario
        #self.monto=monto
        self.tipo=tipo
        self.nota_id=nota_id
        self.usuario_id=usuario_id
        self.pagoEfectivo=pagoEfectivo
        self.pagoVisa=pagoVisa
        self.pagoBBVA=pagoBBVA
        self.pagoBCP=pagoBCP
        self.pagoYape=pagoYape

    def get_id(self):
        return self.id
    def get_fecha(self):
        return self.fecha_creacion.strftime('%d/%m/%Y')
    #def get_monto(self):
    #    return self.monto
    def get_tipo(self):
        return self.tipo
    def get_comentario(self):
        return self.comentario
    def get_usuario_id(self):
        return self.usuario_id
    def get_nota_id(self):
        return self.nota_id
    #def get_nota_dinero(self):
    #    return self.nota_dinero
    def get_json(self):
        usuario_nombre = Usuario.query.filter_by(id=self.usuario_id).first().get_nombre()
        json={"id":self.id,"fecha_creacion":self.fecha_creacion.strftime('%d/%m/%Y'),"nota_id":self.nota_id,"pagoEfectivo":self.pagoEfectivo,"pagoVisa":self.pagoVisa,"pagoBBVA":self.pagoBBVA,"pagoBCP":self.pagoBCP,"pagoYape":self.pagoYape,"tipo":self.tipo,"comentario":self.comentario,"usuario_nombre":self.usuario_nombre,"anulado":self.anulado}
        return json if json is not None else {}
        
    def get_anulado(self):
        return self.anulado
    
    @staticmethod
    def get_json_filtrado_por_tipo(tipo,fecha_inicio,fecha_fin):
        # Verificando si las fechas son None
        if fecha_inicio is None or fecha_fin is None:
            detalles = Detalle_Caja.query.filter_by(tipo=tipo).all()
        else:
            detalles = Detalle_Caja.query.filter_by(tipo=tipo).filter(Detalle_Caja.fecha_creacion.between(fecha_inicio,fecha_fin)).all()

        if not detalles:
            return {}
        
        sum_pago_efectivo = sum([detalle.pagoEfectivo for detalle in detalles])
        sum_pago_visa = sum([detalle.pagoVisa for detalle in detalles])
        sum_pago_bbva = sum([detalle.pagoBBVA for detalle in detalles])
        sum_pago_bcp = sum([detalle.pagoBCP for detalle in detalles])
        sum_pago_yape = sum([detalle.pagoYape for detalle in detalles])

        filtered_json = {"tipo":tipo,"detalles": [detalle.get_json() for detalle in detalles],"sum_pago_efectivo":sum_pago_efectivo,"sum_pago_visa":sum_pago_visa,"sum_pago_bbva":sum_pago_bbva,"sum_pago_bcp":sum_pago_bcp,"sum_pago_yape":sum_pago_yape}
        return filtered_json
