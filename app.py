from flask import Flask, render_template, request,flash,session,redirect,url_for
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from modelos import *
import formularios
import json 

app=Flask(__name__)
app.config.from_object(DevelopmentConfig)

db.init_app(app)
csrf=CSRFProtect(app)
csrf.init_app(app)

with app.app_context():
    db.create_all()
	


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
	#	print('login redirect')
	#	return redirect(url_for('login'))
	
	if 'rol' in session:
		#if session.get('rol')!='jefe' and request.endpoint == 'crear_cuenta':
	#		flash('No tienes acceso a esta sección',category='error')
		#	return redirect(url_for('buscar_producto'))
		if session.get('rol') =='vendedor' and request.endpoint == 'editar_id':
			flash('No tienes acceso a esta sección',category='error')
			return redirect(url_for('buscar_producto'))

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
	loggin=False
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
			loggin=True
			return redirect(url_for('crear_producto'))
		else:
			error_message='Usuario o contraseña no validos!'
			flash(error_message,category='error')

	return render_template('login.html',form_login=user_form,log=loggin)

@app.route('/logout',methods=['GET','POST'])
def logout():
	if 'username' in session:
		session.pop('username')
		print('adios')
	if 'producto' in session:
		session.pop('producto')
	if 'total_venta' in session:
		session.pop('total_venta')
	if 'direccion_comprador' in session:
		session.pop('direccion_comprador')
	if 'nombre_comprador' in session:
		session.pop('nombre_comprador')

	return redirect(url_for('login'))

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
	print('1')
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

@app.route('/crearnotapedido',methods=['GET','POST'])
def crear_nota_pedido():
	nombre_comprador=request.form['comprador_name']
	direccion_comprador=request.form['direccion_comprador']
	total_venta=0
	if 'producto' in session:
		session.modified=True
		for key,producto in session['producto'].items():
				total_venta=total_venta+session['producto'][key]['precio_individual']
		session['total_venta']=total_venta
		if nombre_comprador and direccion_comprador and request.method == 'POST':
			datos_producto_json= json.dumps(session['producto'])
			nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador)

			session['nombre_comprador']=nombre_comprador
			session['direccion_comprador']=direccion_comprador

			if nota is not None:
				db.session.add(nota)
				db.session.commit()
				succes_message='Se creo la nota de pedido para {}'.format(nombre_comprador)
				flash(succes_message,category='message')
			else:
				error_message='No se pudo crear la nota de pedido, intentelo nuevamente'
				flash(error_message,category='error')

	return redirect(url_for('.buscar_producto'))


def array_merge( first_array , second_array ):
	if isinstance( first_array , list ) and isinstance( second_array , list ):
		return first_array + second_array
	elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
		return dict( list( first_array.items() ) + list( second_array.items() ) )
	elif isinstance( first_array , set ) and isinstance( second_array , set ):
		return first_array.union( second_array )
	return False

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

@app.route('/delete',methods=['POST'])
def deleteproduct():
	key_code=str(request.form['code'])
	total_venta=0
	if key_code and request.method=='POST':
		session.modified=True
		for key in session['producto'].items():
			if key[0]==key_code:
				print('elimino')
				session['producto'].pop(key[0],None)
				print(session['producto'])
				if 'producto' in session:
					for key, value in session['producto'].items():
						total_venta=total_venta+session['producto'][key]['precio_individual']
				else:
					session['total_venta']=0
				session['total_venta']=total_venta
				break
		return redirect(url_for('.buscar_producto'))

	return redirect(url_for('.buscar_producto'))

@app.route('/empty')
def empty_cart():
	try:
		session.pop('producto')
		session.pop('total_venta')

		return redirect(url_for('.buscar_producto'))
	except Exception as e:
		print(e)
		
@app.route('/imprimir')
def imprimir():
	return render_template('imprimir.html')

		
if __name__=='main':
	app.run(debug=False)