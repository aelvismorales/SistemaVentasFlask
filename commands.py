import click
from modelos import *
from flask.cli import AppGroup
import pandas as pd
@click.command('crear-db')
def create_db():
    "Crear la base de datos"
    db.create_all()
@click.command('eliminar-db')
def drop_db():
    "Limpia o reset la base de datos"
    db.drop_all()

@click.command('crear-usuario')
@click.argument('name',type=str)
@click.argument('password',type=str)
@click.argument('rol',type=str)
def crear_usuario(name,password,rol):
    "Crear un usuario"
	
    usuario=Usuario(name,password,rol)
    
    db.session.add(usuario)
    db.session.commit()

@click.command('poblar-bd')
def poblar_bd():
	prd=pd.read_csv('ferreteria_data.csv')
	for i in prd.index:
            productos=Producto(prd['Material'][i],prd['COSTO'][i],prd['PRECIO PUBLICO'][i])
            db.session.add(productos)
            db.session.commit()
@click.command('descargar-tabla')
@click.argument('name',type=str)
def descargar_tabla(name):
    if name=='usuario':
        usuario=Usuario.query.all()
        df_usuario=pd.DataFrame(usuario)
        df_usuario.to_csv('usuarios.csv',sep=',')
    elif name=='producto':
        producto=Producto.query.all()
        df_producto=pd.DataFrame(producto)
        df_producto.to_csv('productos.csv',sep=',')
    elif name=='comprador':
        comprador=Comprador.query.all()
        df_comprador=pd.DataFrame(comprador)
        df_comprador.to_csv('comprador.csv',sep=',')
    elif name=='notapedido':
        notapedido=Nota_de_Pedido.query.all()
        df_notapedido=pd.DataFrame(notapedido)
        df_notapedido.to_csv('notapedido.csv',sep=',')

    


def init_app(app):

    app.cli.add_command(crear_usuario)
    app.cli.add_command(create_db)
    app.cli.add_command(drop_db)
    app.cli.add_command(poblar_bd)
    app.cli.add_command(descargar_tabla)
    app.app_context().push()
    

