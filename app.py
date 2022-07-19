from flask import Flask, render_template, request,flash,session,redirect,url_for,jsonify,send_file
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import desc
from config import DevelopmentConfig
from modelos import *
import formularios
import json 
import pandas as pd
import commands

#-------------------------------------------------------------------------------------------------------
# Iniciar la aplicación
app=Flask(__name__)
app.config.from_object(DevelopmentConfig)

db.init_app(app)
csrf=CSRFProtect(app)
csrf.init_app(app)

with app.app_context():
    db.create_all()
	
#Lista de comandos
commands.init_app(app)

#-------------------------------------------------------------------------------------------------------
@app.route('/llenarbasededatos')
def llenarbasededatos():
	prd=pd.read_csv('ferreteria_data.csv')
	for i in prd.index:
		productos=Producto(prd['Material'][i],prd['COSTO'][i],prd['PRECIO PUBLICO'][i])
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

	return render_template('login.html',form_login=user_form,log=loge)

@app.route('/logout',methods=['GET','POST'])
def logout():
	session.clear()
	return redirect(url_for('login'))
#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
@app.route('/producto',methods=['GET','POST'])
def crear_producto():
	crear_producto=formularios.CrearProducto(request.form)
	if request.method=='POST' and crear_producto.validate():
		precio_venta=crear_producto.precio_venta_producto.data
		producto=Producto(crear_producto.nombre_producto.data,crear_producto.precio_costo_producto.data,precio_venta)

		if producto is not None:
			db.session.add(producto)
			db.session.commit()
			succes_message='Se creo el producto {}'.format(crear_producto.nombre_producto.data)
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
		producto.fecha_actualizacion_producto=datetime.now()

		db.session.add(producto)
		db.session.commit()

		succes_message='Se actualizo el producto {}'.format(producto.nombre_producto)
		flash(succes_message,category='message')
		return render_template('editar_producto_id.html',editar_form=editar_producto,log=loge,product_name=producto.get_str_nombre(),product_pc=producto.get_str_pc(),product_pv=producto.get_str_pv())

	return render_template('editar_producto_id.html',editar_form=editar_producto,log=loge,product_name=producto.get_str_nombre(),product_pc=producto.get_str_pc(),product_pv=producto.get_str_pv())

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
#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
@app.route('/crearnotapedido',methods=['GET','POST'])
def crear_nota_pedido():
	nombre_comprador=request.form['comprador_name']
	direccion_comprador=request.form['direccion_comprador']
	estado_nota=request.form.get('estado')
	total_venta=0
	if 'producto' in session:
		session.modified=True
		for key,producto in session['producto'].items():
				total_venta=total_venta+session['producto'][key]['precio_individual']
		session['total_venta']=total_venta

		if nombre_comprador and direccion_comprador and estado_nota and request.method == 'POST':
			existe_comprador=Comprador.query.filter_by(nombre_comprador=nombre_comprador).first()
			
			if existe_comprador is not None:
				datos_producto_json= json.dumps(session['producto'])

				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,existe_comprador)
				session['nombre_comprador']=nombre_comprador
				session['direccion_comprador']=direccion_comprador

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
					nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota)
					session['nombre_comprador']=nombre_comprador
					session['direccion_comprador']=direccion_comprador

					if nota is not None:
						db.session.add(nota)
						db.session.commit()
						session['numero_nota']=nota.get_id()
						session['fecha_nota']=nota.get_fecha()
						session['estado_nota']=estado_nota
						succes_message='Se creo la nota de pedido para {}'.format(nombre_comprador)
						flash(succes_message,category='message')
						
						error_message='Se esta creando la nota de pedido con un comprador no registrado'
						flash(error_message,category='error')

	return redirect(url_for('.buscar_producto'))
# To Do --> Poner una seleccion de busqueda un desplegable de opciones ['Buscar por Fecha-Nombre de Comprador - Notas Pendientes - Enviadas'].
@app.route('/vernotapedido',methods=['GET','POST'])
def vernotapedido():
	seleccion=request.form.get('seleccionbusqueda')
	fecha=False
	nombre=False
	order=False
	if request.method=='POST':
		if seleccion=='Fecha':
			fecha=True
		elif seleccion=='Nombre':
			nombre=True
		elif seleccion=='Ordenar por Cantidad':
			order=True
			nota_pedido=Nota_de_Pedido.query.order_by(desc(Nota_de_Pedido.total_venta)).all()
			if nota_pedido is not None:
				return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,form_seleccion=seleccion,bool_fecha=fecha,bool_nombre=nombre,bool_order=order)
			else :
				error_message='No se pudo encontrar la nota de pedido intente nuevamente'
				flash(error_message,category='error')
		
	return render_template('ver_nota_pedido.html',log=loge,form_seleccion=seleccion,bool_fecha=fecha,bool_nombre=nombre,bool_order=order)

@app.route('/vernotaporfecha',methods=['GET','POST'])
def vernotaporfecha():
	fecha_inicio=request.form['fecha_inicio']
	fecha_final=request.form['fecha_final']

	if fecha_inicio and fecha_final and request.method=='POST':
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio,fecha_final)).all()
		if nota_pedido is not None:
			print(nota_pedido )
			return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido)
		else :
			error_message='No se pudo encontrar la nota de pedido intente nuevamente'
			flash(error_message,category='error')

	return redirect(url_for('.vernotapedido'))

@app.route('/vernotapornombre',methods=['GET','POST'])
def vernotapornombre():
	nombrecomprador=request.form['nombre_comprador']
	print(nombrecomprador)
	if nombrecomprador and request.method=='POST':
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+nombrecomprador+'%')).all()
		if nota_pedido is not None:
			return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido)
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
	return jsonify({'htmlresponse':render_template('ver_nota_id.html',nota=nota,notas=notas,log=loge,ver=ver)})
#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
#To Do editar  CRUD informacion de Usuario - Ver Lista de Usuarios 
@app.route('/crearcomprador',methods=['GET','POST'])
def crearcomprador():
	comprador=formularios.CrearComprador(request.form)

	if request.method=='POST' and comprador.validate():
		existe_comprador=Comprador.query.filter_by(nombre_comprador=comprador.nombre_comprador.data).first()
	
		if existe_comprador is None:
			nuevo_comprador=Comprador(comprador.nombre_comprador.data,comprador.numero_telefono.data,comprador.tipo_comprador.data,comprador.direccion_comprador.data)
		
			db.session.add(nuevo_comprador)
			db.session.commit()
			
			succes_message='Se creo el usuario {}'.format(nuevo_comprador.nombre_comprador)
			flash(succes_message,message='message')
		else:
			error_message='No se puede crear el comprador, este ya se encuentra registrado'
			flash(error_message,category='error')
	return render_template('crear_comprador.html',form_comprador=comprador,log=loge)
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
				DictProducts={str(id):{'id':id,'name':producto.nombre_producto,'precio':producto.precio_venta_producto,'cantidad':cantidad,'precio_individual':producto.precio_venta_producto*cantidad}}

				if 'producto' in session:
					session.modified = True
					if str(id) in session['producto']:
						
						for key,producto in session['producto'].items():
							total_venta=total_venta+session['producto'][key]['precio_individual']
						session['total_venta']=total_venta
						print('El producto ya esta en el carrito')
					else:
						session['producto']=array_merge(session['producto'],DictProducts)
						
						for key,producto in session['producto'].items():
							total_venta=total_venta+session['producto'][key]['precio_individual']
						session['total_venta']=total_venta

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
		session['producto'][key]['precio_individual']=cantidad*float(session['producto'][key]['precio'])
		for key,producto in session['producto'].items():
			total_venta=total_venta+session['producto'][key]['precio_individual']
		session['total_venta']=total_venta
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
		session['producto'][key]['precio_individual']=session['producto'][key]['cantidad']*float(session['producto'][key]['precio'])

		for key,producto in session['producto'].items():
			total_venta=total_venta+session['producto'][key]['precio_individual']
		session['total_venta']=total_venta
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
				session['total_venta']=total_venta
				break
		return redirect(url_for('.buscar_producto'))

	return redirect(url_for('.buscar_producto'))

#Limpiar todo la lista de productos de 	Nota de pedido
@app.route('/empty')
def empty_cart():
	try:
		session.pop('producto')
		session.pop('total_venta')
		session.pop('fecha_nota')
		session.pop('numero_nota')
		session.pop('estado_nota')

		return redirect(url_for('.buscar_producto'))
	except Exception as e:
		print(e)

#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------		
@app.route('/imprimir')
def imprimir():
	return render_template('imprimir.html')

#-------------------------------------------------------------------------------------------------------#-------------------------------------------------------------------------------------------------------
if __name__=='main':
	app.run(debug=False)