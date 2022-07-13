from ast import For
from wtforms import Form
from wtforms import StringField,PasswordField,SelectField,FloatField,SearchField,HiddenField,FieldList,FormField
from wtforms.validators import DataRequired,Length

class CrearCuenta(Form):
    username=StringField('Username',validators=[Length(min=4,max=30,message="Ingrese un nombre de usuario valido"),DataRequired(message="El nombre de usuario es requerido")])
    password=PasswordField('Password',validators=[Length(min=4,max=10,message="La contraseña puede tener un maximo de 10 caracteres"),DataRequired(message="La contraseña es requerida")])
    rol=SelectField("Rol",validators=[DataRequired("Seleccione una opción")],choices=[('vendedor','vendedor'),('administrador','administrador'),('jefe','jefe')])

class Login(Form):
    username=StringField('Username',validators=[Length(min=4,max=30,message="Ingrese un nombre de usuario valido"),DataRequired(message="El nombre de usuario es requerido")])
    password=PasswordField('Password',validators=[Length(min=4,max=10,message="La contraseña puede tener un maximo de 10 caracteres"),DataRequired(message="La contraseña es requerida")])

class CrearProducto(Form):
    nombre_producto=StringField('Nombre producto',validators=[Length(max=200,message="Ingrese un nombre de producto valido"),DataRequired(message="El nombre del producto es requerido")])
    precio_costo_producto=FloatField('Precio costo producto',validators=[DataRequired(message='El precio de costo es requerido')])
    precio_venta_producto=FloatField('Precio venta producto',validators=[DataRequired(message='El precio de venta es requerido')])

class BuscarProducto(Form):
    nombreproducto=SearchField('Buscar producto',validators=[Length(max=200,message="Ingrese un nombre de producto valido"),DataRequired(message="El nombre del producto es requerido")])

class EditarProducto(Form):
    nombre__producto=StringField('Nombre producto',validators=[Length(max=200,message="Ingrese un nombre de producto valido"),DataRequired(message="El nombre del producto es requerido")])
    precio_costo_producto=FloatField('Precio costo producto',validators=[DataRequired(message='El precio de costo es requerido')])
    precio_venta_producto=FloatField('Precio venta producto',validators=[DataRequired(message='El precio de venta es requerido')])

class CrearNotaPedido(Form):
    #cantidad=cantidad=FloatField()
    #nombre___producto=StringField('Nombre producto',validators=[Length(max=200,message="Ingrese un nombre de producto valido"),DataRequired(message="El nombre del producto es requerido")])
    #precio_venta_producto=FloatField('Precio venta producto',validators=[DataRequired(message='El precio de venta es requerido')])
    nombre_comprador=StringField('Comprador',validators=[Length(max=200,message="Ingrese un direccion valida"),DataRequired(message="Se necesita una direccion")])
    direccion_comprador=StringField('Direccion',validators=[Length(max=200,message="Ingrese un direccion valida"),DataRequired(message="Se necesita una direccion")])
