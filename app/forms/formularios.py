from ast import For
from email.policy import default
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SelectField,FloatField,SearchField,HiddenField,FieldList,FormField,DateField,BooleanField
from wtforms.validators import DataRequired,Length

class CrearCuenta(FlaskForm):
    username=StringField('Username',validators=[Length(min=4,max=30,message="Ingrese un nombre de usuario valido"),DataRequired(message="El nombre de usuario es requerido")])
    nickname=StringField('Nickname',validators=[Length(min=4,max=30,message="Ingrese un nickname valido"),DataRequired(message="El nickname es requerido")])
    password=PasswordField('Password',validators=[Length(min=4,max=10,message="La contraseña puede tener un maximo de 10 caracteres"),DataRequired(message="La contraseña es requerida")])
    rol=SelectField("Rol",validators=[DataRequired("Seleccione una opción")],choices=[('Usuario','Usuario'),('Administrador','Administrador')])

class Login(FlaskForm):
    username=StringField('Username',validators=[Length(min=4,max=30,message="Ingrese un nombre de usuario valido"),DataRequired(message="El nombre de usuario es requerido")])
    password=PasswordField('Password',validators=[Length(min=4,max=10,message="La contraseña puede tener un maximo de 10 caracteres"),DataRequired(message="La contraseña es requerida")])
    remember=BooleanField('Remember me')

class CrearProducto(FlaskForm):
    nombre_producto=StringField('Nombre producto',validators=[Length(max=200,message="Ingrese un nombre de producto valido"),DataRequired(message="El nombre del producto es requerido")])
    precio_costo_producto=FloatField('Precio costo producto',validators=[DataRequired(message='El precio de costo es requerido')])
    precio_venta_producto=FloatField('Precio venta producto',validators=[DataRequired(message='El precio de venta es requerido')])
    stock=FloatField('Stock',validators=[DataRequired('Ingrese el stock')])
class BuscarProducto(FlaskForm):
    nombreproducto=SearchField('Buscar producto',validators=[Length(max=200,message="Ingrese un nombre de producto valido"),DataRequired(message="El nombre del producto es requerido")])


class BuscarNotaporComprador(FlaskForm):
    nombrecomprador=SearchField('Buscar por nombre de comprador',validators=[Length(max=200,message="Ingrese un nombre de comprador valido"),DataRequired(message="El nombre del comprador es requerido")])


class BuscarNotaporFecha(FlaskForm):
    fecha_inicio=DateField(label='Fecha Inicio',format="%Y-%m-%d",validators=[DataRequired('Ingrese una fecha valida')],render_kw={'placeholder': '2022-07-15 para Junio 15, 2022'})
    fecha_final=DateField(label='Fecha Final',format="%Y-%m-%d",validators=[DataRequired('Ingrese una fecha valida')],render_kw={'placeholder': '2022-07-16 para Junio 16, 2022'})

class OpcionesFiltros(FlaskForm):
    filtros=SelectField("Tipo de Comprador",validators=[DataRequired("Seleccione una opción")],choices=[('Nombre','Nombre'),('Fecha','Fecha'),('Ordenar por Cantidad','Ordenar por Cantidad')])
  

class EditarProducto(FlaskForm):
    nombre_producto=StringField('Nombre producto',validators=[Length(max=200,message="Ingrese un nombre de producto valido")])
    precio_costo_producto=FloatField('Precio costo producto')
    precio_venta_producto=FloatField('Precio venta producto')
    stock=FloatField('Stock',validators=[DataRequired('Ingrese el stock')])
class CrearNotaPedido(FlaskForm):
    nombre_comprador=StringField('Comprador',validators=[Length(max=200,message="Ingrese un direccion valida"),DataRequired(message="Se necesita una direccion")])
    direccion_comprador=StringField('Direccion',validators=[Length(max=200,message="Ingrese un direccion valida"),DataRequired(message="Se necesita una direccion")])
    numero_telefono=StringField('Numero de celular',validators=[Length(max=10,message="Ingrese un numero de telefono válido"),DataRequired('Ingrese un numero de telefono')],default='')
    dni=StringField('DNI:',validators=[DataRequired('Ingrese un DNI valido.'),Length(max=10)])
    estado=SelectField("Estado",validators=[DataRequired("Seleccione una opción")],choices=[('CANCELADO','CANCELADO'),('POR-CANCELAR','POR CANCELAR'),('PROFORMA','PROFORMA')],render_kw={'CANCELADO':'CANCELADO'})
    estado_pedido=SelectField("Estado Pedido",validators=[DataRequired("Seleccione una opción")],choices=[('ENTREGADO','ENTREGADO'),('POR-ENTREGAR','POR ENTREGAR')])
    
class CrearComprador(FlaskForm):
    
    nombre_comprador=StringField('Nombre del comprador',validators=[Length(max=200,message="Ingrese un nombre válido"),DataRequired('Ingrese un nombre')])
    numero_telefono=StringField('Numero de celular',validators=[Length(max=10,message="Ingrese un numero de telefono válido"),DataRequired('Ingrese un numero de telefono')],default='')    
    tipo_comprador=SelectField("Tipo de Comprador",validators=[DataRequired("Seleccione una opción")],choices=[('persona','persona'),('empresa','empresa')],render_kw={'value':'persona'})    
    direccion_comprador=StringField('Direccion',validators=[Length(max=200,message="Ingrese un direccion valida"),DataRequired(message="Se necesita una direccion")])
    dni=StringField('DNI:',validators=[DataRequired('Ingrese un DNI valido.'),Length(max=15)])