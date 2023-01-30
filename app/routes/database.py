from flask import Blueprint,url_for,redirect,send_file
from ..models.modelos import *
import pandas as pd
from app import db

database=Blueprint('database',__name__)

@database.route('/llenarproductos')
def llenarproductos():
	prd=pd.read_csv('producto.csv')
	for i in prd.index:
		productos=Producto(prd['nombre_producto'][i],prd['precio_costo_producto'][i],prd['precio_venta_producto'][i],prd['stock'][i])
		db.session.add(productos)
		db.session.commit()
	return redirect(url_for('product.buscar_producto'))

@database.route('/llenarnotas')
def llenarnotas():
	prd=pd.read_csv('notapedido.csv')
	for i in prd.index:
		notas=Nota_de_Pedido(prd['nombre_producto'][i],prd['total_venta'][i],prd['nombre_comprador'][i],prd['direccion_comprador'][i],prd['estado'][i],prd['fecha_creacion'][i])
		db.session.add(notas)
		db.session.commit()
	return redirect(url_for('product.buscar_producto'))

@database.route('/llenarcompradores')
def llenarcompradores():
	prd=pd.read_csv('comprador.csv')
	for i in prd.index:
		compradores=Comprador(prd['nombre_comprador'][i],prd['numero_telefono_comprador'][i],prd['direccion_comprador'][i],prd['dni'][i])
		db.session.add(compradores)
		db.session.commit()
	return redirect(url_for('product.buscar_producto'))

@database.route('/llenarusuarios')
def llenarusuarios():
	prd=pd.read_csv('comprador.csv')
	for i in prd.index:
		usuarios=Usuario(prd['nombre_usuario'][i],prd['contrasena_usuario'][i],prd['rol_usuario'][i])
		db.session.add(usuarios)
		db.session.commit()
	return redirect(url_for('product.buscar_producto'))


@database.route('/downloadtables/<string:name>')
def downloadtables(name):
	if name=='usuario':
		usuario=Usuario.query.all()

		df_usuario=pd.DataFrame(columns=['id','nombre_usuario','contrasena_usuario','fecha_creacion','rol_usuario'])
		for u in usuario:
			df_usuario=df_usuario.append({'id':u.id,'nombre_usuario':u.nombre_usuario,'contrasena_usuario':u.contrasena_usuario,'fecha_creacion':u.fecha_creacion,'rol_usuario':u.rol_usuario},ignore_index=True)
		df_usuario.to_csv('usuario.csv',sep=',')
	elif name=='producto':
		producto=Producto.query.all()
		df_producto=pd.DataFrame(columns=['id','nombre_producto','fecha_creacion','fecha_actualizacion_producto','precio_costo_producto','precio_venta_producto'])
		for p in producto:
			df_producto=df_producto.append({'id':p.id,'nombre_producto':p.nombre_producto,'fecha_creacion':p.fecha_creacion,'fecha_actualizacion_producto':p.fecha_actualizacion_producto,'precio_costo_producto':p.precio_costo_producto,'precio_venta_producto':p.precio_venta_producto})
		df_producto.to_csv('producto.csv',sep=',')
	elif name=='comprador':
		comprador=Comprador.query.all()
		df_comprador=pd.DataFrame(columns=['id','nombre_comprador','numero_telefono_comprador','tipo_comprador','direccion_comprador'])
		for c in comprador:
			df_comprador=df_comprador.append({'id': c.id,'nombre_comprador':c.nombre_comprador,'numero_telefono_comprador':c.numero_telefono_comprador,'tipo_comprador':c.tipo_comprador,'direccion_comprador':c.direccion_comprador})
		df_comprador.to_csv('comprador.csv',sep=',')
	elif name=='notapedido':
		notapedido=Nota_de_Pedido.query.all()
		df_notapedido=pd.DataFrame(columns=['id','fecha_creacion','nombre_comprador','nombre_producto','nombre_producto','total_venta','direccion_comprador','estado'])
		for n in notapedido:
			df_notapedido=df_notapedido.append({'id':n.id,'fecha_creacion':n.fecha_creacion,'nombre_comprador':n.nombre_comprador,'nombre_producto':n.nombre_producto,'total_venta':n.total_venta,'direccion_comprador':n.direccion_comprador,'estado':n.estado})
		df_notapedido.to_csv('notapedido.csv',sep=',')
	print('Descargando la tabla {} .csv'.format(name))
	return send_file(
        '{}.csv'.format(name),
        mimetype='text/csv',
        download_name='{}.csv'.format(name),
        as_attachment=True
    )

@database.route("/actualizarnota")
def actualizarnota():
	notas=Nota_de_Pedido.query.all()
	for nota in notas:
		nota.deuda=0.0
		nota.acuenta=0.0
		db.session.add(nota)
		db.session.commit()
	return redirect(url_for('product.buscar_producto'))