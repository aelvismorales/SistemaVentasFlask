from ast import Not
from datetime import date
from flask import Flask, render_template, request,flash,session,redirect,url_for,jsonify,send_file
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import desc,asc
from config import DevelopmentConfig
from modelos import *
import formularios
import json 
import pandas as pd
import commands

#-------------------------------------------------------------------------------------------------------
# Iniciar la aplicación

def create_app():
	app=Flask(__name__)
	app.config.from_object(DevelopmentConfig)
	db.init_app(app)
	csrf=CSRFProtect()
	csrf.init_app(app)
	with app.app_context():
		db.create_all()
	commands.init_app(app)
	return app,csrf

app,csrf=create_app()
#Lista de comandos
commands.init_app(app)

#-------------------------------------------------------------------------------------------------------
@app.route('/llenarbasededatos')
def llenarbasededatos():
	prd=pd.read_csv('ferreteria_data.csv')
	for i in prd.index:
		productos=Producto(prd['Material'][i],prd['COSTO'][i],prd['PRECIO PUBLICO'][i],prd['STOCK'][i])
		db.session.add(productos)
		db.session.commit()
	return redirect(url_for('buscar_producto'))

@app.route('/downloadtables/<string:name>')
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
#-------------------------------------------------------------------------------------------------------
# Verificaciones de sesion del usuario.
@app.before_request
def beforerequest():
	global loge
	loge=False
	global produ 
	produ=False

	if 'username' in session:
		loge=True
	if 'producto' in session:
		produ=True
	#if 'username' not in session and request.endpoint != 'login':

	#	return redirect(url_for('login'))
	
	if 'rol' in session:
		#if session.get('rol')!='jefe' and request.endpoint == 'crear_cuenta':
		#	flash('No tienes acceso a esta sección',category='error')
		#	return redirect(url_for('buscar_producto'))
		if session.get('rol') =='vendedor' and request.endpoint == 'editar_id':
			flash('No tienes acceso a esta sección',category='error')
			return redirect(url_for('buscar_producto'))
#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
@app.route('/')
def index():
	return render_template('index.html',log=loge)	
    	
@app.route('/crear',methods=['GET','POST'])
def crear_cuenta():
	crear_usuario=formularios.CrearCuenta(request.form)
	if request.method=='POST' and crear_usuario.validate():
		usuario=Usuario(crear_usuario.username.data,crear_usuario.password.data,crear_usuario.rol.data)

		db.session.add(usuario)
		db.session.commit()

		mensaje='Felicidades por registrarte {}'.format(crear_usuario.username.data)
		flash(mensaje,category='message')
	else:
		mensaje='Hubo un error en crear la cuenta, intente nuevamente'
		flash(mensaje,category='error')

	return render_template('crear_cuenta.html',form_usuario=crear_usuario)

@app.route('/login',methods=['GET','POST'])
def login():
	user_form=formularios.Login(request.form)
	
	if request.method=='POST' and user_form.validate():
		username=user_form.username.data
		password=user_form.password.data
		try:
			usuario=Usuario.query.filter_by(nombre_usuario=username).first()
			if usuario is not None and usuario.verificar_contrasena(password):
				succes_message='Bienvenido {}'.format(user_form.username.data)
				flash(succes_message,category='message')
				session['username']=username
				session['id']=usuario.get_id()
				session['rol']=usuario.get_rol()

				return redirect(url_for('crear_producto'))
			else:
				error_message='Usuario o contraseña no validos!'
				flash(error_message,category='error')
		except ValueError as Error:
			session.rollback()
			print(Error)

	return render_template('login.html',form_login=user_form,log=loge)

@app.route('/logout',methods=['GET','POST'])
def logout():
	session.pop('username',None)
	session.pop('id',None)
	session.pop('rol',None)
	return redirect(url_for('login'))
#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
@app.route('/producto',methods=['GET','POST'])
def crear_producto():
	crear_producto=formularios.CrearProducto(request.form)
	if request.method=='POST' and crear_producto.validate():
		precio_venta=crear_producto.precio_venta_producto.data
		producto=Producto(crear_producto.nombre_producto.data,crear_producto.precio_costo_producto.data,precio_venta,crear_producto.stock.data)

		if producto is not None:
			db.session.add(producto)
			db.session.commit()
			succes_message='Se creo el producto "{}"'.format(crear_producto.nombre_producto.data)
			flash(succes_message,category='message')
			return render_template('crear_producto.html',producto_form=crear_producto,log=loge)
		else:
			error_message='No se pudo crear el producto intente nuevamente'
			flash(error_message,category='error')
			
	return render_template('crear_producto.html',producto_form=crear_producto,log=loge)


@app.route('/editar/<int:id>',methods=['GET','POST'])
def editar_id(id):
	producto=Producto.query.get(id)
	editar_producto=formularios.EditarProducto(request.form)
	if request.method=='POST' and editar_producto.validate(): 	
		producto.nombre_producto=editar_producto.nombre__producto.data
		producto.precio_costo_producto=editar_producto.precio_costo_producto.data
		producto.precio_venta_producto=editar_producto.precio_venta_producto.data
		producto.stock=editar_producto.stock.data
		producto.fecha_actualizacion_producto=datetime.now()

		db.session.add(producto)
		db.session.commit()

		succes_message='Se actualizo el producto {}'.format(producto.nombre_producto)
		flash(succes_message,category='message')
	return render_template('editar_producto_id.html',editar_form=editar_producto,log=loge,product_name=producto.get_str_nombre(),product_pc=producto.get_str_pc(),product_pv=producto.get_str_pv(),product_stock=producto.get_stock())

@app.route('/buscar',methods=['GET','POST'])
def buscar_producto():
	buscar_producto=formularios.BuscarProducto(request.form)
	if request.method=='POST': 
		if buscar_producto.validate():
			productos=Producto.query.filter(Producto.nombre_producto.like('%'+buscar_producto.nombreproducto.data+'%')).all()
			if productos is not None:
				return render_template('buscar_productos.html',buscar_form=buscar_producto,productos=productos,log=loge)
			else :
				error_message='No se pudo encontrar el producto intente nuevamente'
				flash(error_message,category='error')
		else:
			render_template('buscar_productos.html',buscar_form=buscar_producto,log=loge,prd=produ)
	
	return render_template('buscar_productos.html',buscar_form=buscar_producto,log=loge,prd=produ)

@app.route('/eliminarproducto/<string:id>',methods=['GET','POST'])
def eliminarproducto(id):
	producto_eliminar=Producto.query.get(id)
	if producto_eliminar is not None:
		nombre_elimninar=producto_eliminar.get_str_nombre()
		db.session.delete(producto_eliminar)
		db.session.commit()
		succes_message='Se elimino el producto "{}" satisfactoriamente'.format(nombre_elimninar)
		flash(succes_message,category='message')
		return redirect(url_for('.buscar_producto'))
	else:
		error_message='El producto no se pudo eliminar intente nuevamente'
		flash(error_message,category='error')

	return redirect(url_for('.buscar_producto'))
#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
@app.route('/crearnotapedido',methods=['GET','POST'])
def crear_nota_pedido():
	nombre_comprador=request.form['comprador_name']
	direccion_comprador=request.form['direccion_comprador']
	dni_comprador=request.form['dni_comprador']
	telefono_comprador=request.form['telefono_comprador']
	estado_nota=request.form.get('estado')
	estado_nota_2=request.form.get('estado2')
	total_venta=0
	if 'producto' in session:
		session.modified=True
		for key,producto in session['producto'].items():
			total_venta=total_venta+session['producto'][key]['precio_individual']
		session['total_venta']=total_venta.__round__(2)

		if nombre_comprador and direccion_comprador and estado_nota and request.method == 'POST':
			existe_comprador=Comprador.query.filter_by(dni=dni_comprador).first()
			estado_nota=estado_nota+estado_nota_2
			if existe_comprador is not None:
				datos_producto_json= json.dumps(session['producto'])

				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,existe_comprador)

				for key,product in session['producto'].items():
					producto=Producto.query.filter_by(nombre_producto=session['producto'][key]['name']).first()
					producto.stock-= session['producto'][key]['cantidad']
				session.modified = True
				session['nombre_comprador']=nombre_comprador
				session['direccion_comprador']=direccion_comprador
				session['dni_comprador']=dni_comprador
				session['telefono_comprador']=telefono_comprador
				
				if nota is not None:
					db.session.add(nota)
					db.session.commit()
					session['numero_nota']=nota.get_id()
					session['fecha_nota']=nota.get_fecha()
					session['estado_nota']=estado_nota
					succes_message='Se creo la nota de pedido para {}'.format(nombre_comprador)
					flash(succes_message,category='message')
				else:
					error_message='No se pudo crear la nota de pedido, intentelo nuevamente'
					flash(error_message,category='error')
			else:
					datos_producto_json= json.dumps(session['producto'])
					comprador_nuevo=Comprador(nombre_comprador,telefono_comprador,direccion_comprador,dni_comprador)
					nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota)
					for key,product in session['producto'].items():
						producto=Producto.query.filter_by(nombre_producto=session['producto'][key]['name']).first()
						producto.stock-=session['producto'][key]['cantidad']
					session.modified = True
					session['nombre_comprador']=nombre_comprador
					session['direccion_comprador']=direccion_comprador
					session['dni_comprador']=dni_comprador
					session['telefono_comprador']=telefono_comprador
					if nota is not None:
						db.session.add(nota)
						db.session.add(comprador_nuevo)
						db.session.commit()
						session['numero_nota']=nota.get_id()
						session['fecha_nota']=nota.get_fecha()
						session['estado_nota']=estado_nota
						succes_message='Se creo la nota de pedido para {} y se registro como nuevo comprador'.format(nombre_comprador)
						flash(succes_message,category='message')
	return redirect(url_for('.buscar_producto'))

@app.route('/buscarcompradorbydni',methods=['GET','POST'])
def buscarcompradorbydni():
	dni=request.form['dni_comprador']
	print(dni)
	if dni and request.method=='POST':
		comprador=Comprador.query.filter_by(dni=dni).first()
		if comprador is not None:
			session.modified = True
			session['nombre_comprador']=comprador.get_nombre()
			session['direccion_comprador']=comprador.get_direccion()
			session['dni_comprador']=comprador.get_dni()
			session['telefono_comprador']=comprador.get_telefono()
		else:
			error_message='El comprador no existe porfavor cree uno'
			flash(error_message,category='error')
	return redirect(url_for('.buscar_producto'))

@app.route('/vernotapedido',methods=['GET','POST'])
def vernotapedido():
	seleccion=request.form.get('seleccionbusqueda')
	fecha=False
	nombre=False
	order=False
	estado_nota=False
	dni_comprador=False
	resumen_Ventas=False
	imprimir_resumen=False
	id_cambio=False
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if request.method=='POST':
		if seleccion=='Fecha':
			fecha=True
			imprimir_resumen=True
		elif seleccion=='Nombre':
			nombre=True
		elif seleccion=='Estado':
			estado_nota=True
		elif seleccion=='DNI':
			dni_comprador=True
		elif seleccion=='resumen':
			resumen_Ventas=True
		elif seleccion=='ID':
			id_cambio=True
		elif seleccion=='Ordenar por Cantidad':
			order=True
			nota_pedido=Nota_de_Pedido.query.order_by(desc(Nota_de_Pedido.total_venta)).all()
			if nota_pedido is not None:
				return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,form_seleccion=seleccion,id_cambio=id_cambio,bool_fecha=fecha,bool_nombre=nombre,bool_order=order,bool_dni=dni_comprador,bool_imprimir=imprimir_resumen,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
			else :
				error_message='No se pudo encontrar la nota de pedido intente nuevamente'
				flash(error_message,category='error')
		
	return render_template('ver_nota_pedido.html',log=loge,form_seleccion=seleccion,bool_fecha=fecha,bool_nombre=nombre,id_cambio=id_cambio,bool_order=order,bool_estado=estado_nota,bool_dni=dni_comprador,bool_resumen=resumen_Ventas,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)

@app.route('/vernotaporestado',methods=['GET','POST'])
def vernotaporestado():
	opcion=request.form.get('opcionestado')
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if request.method=='POST' and opcion:
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.estado==opcion).all()
		return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
	return redirect(url_for('.vernotapedido'))

@app.route('/vernotaporfecha',methods=['GET','POST'])
def vernotaporfecha():
	fecha_inicio=request.form['fecha_inicio']
	fecha_final=request.form['fecha_final']
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if fecha_inicio and fecha_final and request.method=='POST':
		
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio,fecha_final)).all()
		if nota_pedido is not None:
			for note in nota_pedido:
				if note.get_estado() in ['cancelado','cancelado-entregado','cancelado-por-recoger','cancelado-']:
					total_dia+=note.get_total_venta()
				elif note.get_estado() in ['cancelado-VISA','cancelado-VISA-entregado','cancelado-VISA-por-recoger','cancelado-VISA-']:
					total_dia_visa+=note.get_total_venta()
				elif note.get_estado() in ['por-cancelar-','por-cancelar-entregado','por-cancelar-por-recoger']:
					total_dia_por_cancelar+=note.get_total_venta()
				
			return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar,fechita=fecha_inicio,fechita_final=fecha_final,bool_imprimir=True)
		else :
			error_message='No se pudo encontrar la nota de pedido intente nuevamente'
			flash(error_message,category='error')

	return redirect(url_for('.vernotapedido'))

@app.route('/imprimirresumen/<string:fecha>/<string:fecha_final>',methods=['GET','POST'])
def imprimirresumen(fecha,fecha_final):
	fecha=datetime.strptime(fecha, '%Y-%m-%d').date()
	fecha_final=datetime.strptime(fecha_final, '%Y-%m-%d').date()
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	nota_pedido=Nota_de_Pedido.query.order_by(asc(Nota_de_Pedido.id)).filter(Nota_de_Pedido.fecha_creacion.between(fecha,fecha_final)).all()
	if nota_pedido is not None:
		try:
			for note in nota_pedido:
				if note.get_estado() in ['cancelado','cancelado-entregado','cancelado-por-recoger','cancelado-']:
					total_dia+=note.get_total_venta()
				elif note.get_estado() in ['cancelado-VISA','cancelado-VISA-entregado','cancelado-VISA-por-recoger','cancelado-VISA-']:
					total_dia_visa+=note.get_total_venta()
				elif note.get_estado() in ['por-cancelar-','por-cancelar-entregado','por-cancelar-por-recoger']:
					total_dia_por_cancelar+=note.get_total_venta()
			return render_template('resumen_por_imprimir.html',nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar,fechita=fecha)
		except ValueError as EV:
			session.rollback()
			EV('No se pudo general el resumen de ventas realice un rollback')
	else:
		error_message='No se pudo crear un resumen por que no existen notas de pedido'
		flash(error_message,category='error')
	return render_template('resumen_por_imprimir.html',td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar,fechita=fecha)

@app.route('/vernotapornombre',methods=['GET','POST'])
def vernotapornombre():
	nombrecomprador=request.form.get('nombre_comprador')
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if nombrecomprador and request.method=='POST':
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+nombrecomprador+'%')).all()
		if nota_pedido is not None:
			return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
		else :
			error_message='No se pudo encontrar la nota de pedido intente nuevamente'
			flash(error_message,category='error')

	return redirect(url_for('.vernotapedido'))

@app.route('/vernotaporDNI',methods=['GET','POST'])
def vernotaporDNI():
	dni_comprador=request.form.get('dni_comprador')
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if dni_comprador and request.method=='POST':
		comprador=Comprador.query.filter_by(dni=dni_comprador).first()
		if comprador is not None:
			nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+comprador.get_nombre()+'%')).all()
			if nota_pedido is not None:
				return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
			else :
				error_message='No se pudo encontrar la nota de pedido intente nuevamente'
				flash(error_message,category='error')
	return redirect(url_for('.vernotapedido'))


@app.route('/vernotapedidobyID',methods=['GET','POST'])
def vernotapedido_id():
	id=request.form['notaid']
	ver=False
	if id and request.method=='POST':
		
		nota=Nota_de_Pedido.query.get(id)
		ver=True
		notas=json.loads(nota.get_nombre_producto())
		
	return jsonify({'htmlresponse':render_template('ver_nota_id.html',nota=nota,notas=notas,log=loge,ver=ver)})
@app.route('/editarnota/<string:id>',methods=['GET','POST'])
def editarnota(id):
	nota=Nota_de_Pedido.query.get(id)
	nombre_comprador=request.form.get('comprador_name')
	direccion_comprador=request.form.get('direccion_comprador')
	estado_nota=request.form.get('estado')
	estado_nota_2=request.form.get('estado2')
	if nota and nombre_comprador and direccion_comprador and estado_nota and request.method=='POST':
		nota.nombre_comprador=nombre_comprador
		nota.direccion_comprador=direccion_comprador
		nota.estado=estado_nota+estado_nota_2

		db.session.add(nota)
		db.session.commit()
		succes_message='Se actualizo la nota de pedido de {}'.format(nota.nombre_comprador)
		flash(succes_message,category='message')
		return render_template('editar_nota_id.html',nota=nota,log=loge)
	return render_template('editar_nota_id.html',nota=nota,log=loge)

@app.route('/anularnota/<string:id>',methods=['GET','POST'])
def anularnota(id):
	nota=Nota_de_Pedido.query.get(id)
	print('llego2')
	if nota:
		nota.estado='ANULADO-'
		db.session.add(nota)
		db.session.commit()
		succes_message='Se ANULO la nota de pedido {}'.format(nota.id)
		flash(succes_message,category='message')
		return redirect(request.referrer)
	return redirect(request.referrer)


#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
#To Do editar  CRUD informacion de Usuario - Ver Lista de Usuarios 
@app.route('/crearcomprador',methods=['GET','POST'])
def crearcomprador():
	comprador=formularios.CrearComprador(request.form)

	if request.method=='POST' and comprador.validate():
		existe_comprador=Comprador.query.filter_by(nombre_comprador=comprador.nombre_comprador.data).first()

		if existe_comprador is None:
			nuevo_comprador=Comprador(comprador.nombre_comprador.data,comprador.numero_telefono.data,comprador.tipo_comprador.data,comprador.dni.data,comprador.direccion_comprador.data)
		
			db.session.add(nuevo_comprador)
			db.session.commit()
			
			succes_message='Se creo el usuario {}'.format(nuevo_comprador.nombre_comprador)
			flash(succes_message,message='message')
		else:
			error_message='No se puede crear el comprador, este ya se encuentra registrado'
			flash(error_message,category='error')
	return render_template('crear_comprador.html',form_comprador=comprador,log=loge)

@app.route('/editarcomprador/<string:id>',methods=['GET','POST'])
def editarcomprador(id):
	comprador_encontrado=Comprador.query.get(id)
	comprador_nombre=request.form.get('nombre_comprador')
	comprador_numero_telefono=request.form.get('numero_telefono')
	comprador_tipo_comprador=request.form.get('tipo_comprador')
	comprador_direccion=request.form.get('direccion_comprador')
	comprador_dni=request.form.get('dni')

	if request.method=='POST':
		if comprador_encontrado is not None:
			comprador_encontrado.nombre_comprador=comprador_nombre
			comprador_encontrado.numero_telefono_comprador=comprador_numero_telefono
			comprador_encontrado.tipo_comprador=comprador_tipo_comprador
			comprador_encontrado.direccion_comprador=comprador_direccion
			comprador_encontrado.dni=comprador_dni

			db.session.add(comprador_encontrado)
			db.session.commit()

			success_message='Se actualizo correctamente al comprador {}'.format(comprador_encontrado.nombre_comprador)
			flash(success_message,category='message')
		else:
			error_message='No se pudo actualizar la informacion del comprador,intente nuevamente'
			flash(error_message,category='error')
	return render_template('editar_comprador.html',log=loge,form_compra=comprador_encontrado)
@app.route('/eliminarcomprador/<string:id>',methods=['GET','POST'])
def eliminarcomprador(id):
	comprador_encontrado=Comprador.query.get(id)
	if comprador_encontrado is not None:
		nombre_comprador=comprador_encontrado.get_nombre()
		db.session.delete(comprador_encontrado)
		db.session.commit()
		success_message='Se elimino correctamente al comprador {}'.format(nombre_comprador)
		flash(success_message,category='message')
	else:
		error_message='No se pudo eliminar el comprador'
		flash(error_message,category='error')
	return redirect(url_for('.vercompradores'))


@app.route('/vercompradores',methods=['GET','POST'])
def vercompradores():
	dni_comprador=request.form.get('dni_comprador')
	if dni_comprador and request.method=='POST':
		if dni_comprador=='*':
			compradores=Comprador.query.all()
		else:
			compradores=Comprador.query.filter_by(dni=dni_comprador).all()
		return render_template('ver_compradores.html',form_comprador=compradores,log=loge)
	return render_template('ver_compradores.html',log=loge)

#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------


def array_merge( first_array , second_array ):
	if isinstance( first_array , list ) and isinstance( second_array , list ):
		return first_array + second_array
	elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
		return dict( list( first_array.items() ) + list( second_array.items() ) )
	elif isinstance( first_array , set ) and isinstance( second_array , set ):
		return first_array.union( second_array )
	return False
#Agregar el producto a la nota de pedido
@app.route('/add',methods=['POST'])
def add():
	try: 
		id=request.form['code']
		cantidad=float(request.form['quantity'])
		total_venta=0
		producto=Producto.query.get(id)
		if cantidad and id and request.method == 'POST':
			if producto is not None:
				DictProducts={str(id):{'id':id,'name':producto.nombre_producto,'precio':producto.precio_venta_producto,'cantidad':cantidad,'precio_individual':(producto.precio_venta_producto*cantidad).__round__(2)}}

				if 'producto' in session:
					session.modified = True
					if str(id) in session['producto']:
						
						for key,producto in session['producto'].items():
							total_venta=total_venta+session['producto'][key]['precio_individual']
						session['total_venta']=total_venta.__round__(2)
						print('El producto ya esta en el carrito')
					else:
						session['producto']=array_merge(session['producto'],DictProducts)
						
						for key,producto in session['producto'].items():
							total_venta=total_venta+session['producto'][key]['precio_individual']
						session['total_venta']=total_venta.__round__(2)

						return redirect(url_for('.buscar_producto'))
				else:
					session['producto']=DictProducts
					return redirect(url_for('.buscar_producto'))

	except Exception as e:
		print(e)
	finally:
		return redirect(url_for('.buscar_producto'))

#Actualizar Cantidad de Productos en la nota de pedido
@app.route('/updateproduct',methods=['POST'])
def updateproduct():
	cantidad=float(request.form['quantity'])
	key=str(request.form['code'])
	total_venta=0
	if cantidad and request.method == 'POST':
		session.modified = True
		session['producto'][key]['cantidad']=cantidad
		session['producto'][key]['precio_individual']=(cantidad*float(session['producto'][key]['precio'])).__round__(2)
		for key,producto in session['producto'].items():
			total_venta=total_venta+session['producto'][key]['precio_individual']
		session['total_venta']=total_venta.__round__(2)
		return redirect(url_for('.buscar_producto'))
	return redirect(url_for('.buscar_producto'))

#Actualizar precio de un producto en la nota de pedido
@app.route('/updateprice',methods=['POST'])
def updateprice():
	price=float(request.form['price'])
	key=str(request.form['code'])
	total_venta=0
	if price and request.method == 'POST':
		session.modified = True
		session['producto'][key]['precio']=price
		session['producto'][key]['precio_individual']=(session['producto'][key]['cantidad']*float(session['producto'][key]['precio'])).__round__(2)

		for key,producto in session['producto'].items():
			total_venta=total_venta+session['producto'][key]['precio_individual']
		session['total_venta']=total_venta.__round__(2)
		return redirect(url_for('.buscar_producto'))
	return redirect(url_for('.buscar_producto'))

#Eliminar un producto de la nota de pedido
@app.route('/delete',methods=['POST'])
def deleteproduct():
	key_code=str(request.form['code'])
	total_venta=0
	if key_code and request.method=='POST':
		session.modified=True
		for key in session['producto'].items():
			if key[0]==key_code:
				session['producto'].pop(key[0],None)
				if 'producto' in session:
					for key, value in session['producto'].items():
						total_venta=total_venta+session['producto'][key]['precio_individual']
				else:
					session['total_venta']=0
				session['total_venta']=total_venta.__round__(2)
				break
		return redirect(url_for('.buscar_producto'))

	return redirect(url_for('.buscar_producto'))

#Limpiar todo la lista de productos de 	Nota de pedido
@app.route('/empty')
def empty_cart():
	try:
		session.pop('producto',None)
		session.pop('total_venta',None)
		session.pop('fecha_nota',None)
		session.pop('numero_nota',None)
		session.pop('estado_nota',None)
		session.pop('dni_comprador',None)
		session.pop('telefono_comprador',None)
		session.pop('nombre_comprador',None)
		session.pop('direccion_comprador',None)
		
		success_message='Se vacio la nota de pedido'
		flash(success_message,category='message')
		return redirect(url_for('.buscar_producto'))
	except Exception as e:
		print(e)

#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------		
@app.route('/imprimir')
def imprimir():
	return render_template('imprimir.html')

@app.route('/imprimire/<string:id>',methods=['GET','POST'])
def imprimire(id):
	nota=Nota_de_Pedido.query.get(id)
	notas=json.loads(nota.get_nombre_producto())
	if nota.notasdepedidos is None:
		telefono_comprador=''
		dni_comprador=''
	else:
		telefono_comprador=nota.notasdepedidos.numero_telefono_comprador
		dni_comprador=nota.notasdepedidos.dni
	return render_template('imprimirid.html',nota=nota,notas=notas,telefono=telefono_comprador,dni=dni_comprador)

#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
if __name__=='main':
	app.run(debug=False)
