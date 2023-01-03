from flask import Blueprint,request,render_template,redirect,url_for,session,flash
from ..forms.formularios import CrearComprador
from ..models.modelos import Comprador

from app import db



buyer=Blueprint("buyer",__name__)

@buyer.before_request
def beforerequest():
    global loge
    loge=False
    global produ 
    produ=False
    
    if 'username' in session:
        loge=True
    if 'producto' in session:
        produ=True


@buyer.route('/crearcomprador',methods=['GET','POST'])
def crearcomprador():
	comprador=CrearComprador(request.form)

	if request.method=='POST' and comprador.validate():
		existe_comprador=Comprador.query.filter_by(nombre_comprador=comprador.nombre_comprador.data).first()
		if existe_comprador is None:
			nuevo_comprador=Comprador(comprador.nombre_comprador.data,comprador.numero_telefono.data,comprador.direccion_comprador.data,comprador.tipo_comprador.data,comprador.dni.data)
		
			db.session.add(nuevo_comprador)
			
			succes_message='Se creo el usuario {}'.format(nuevo_comprador.nombre_comprador)
			flash(succes_message,category='message')
		else:
			error_message='No se puede crear el comprador, este ya se encuentra registrado'
			flash(error_message,category='error')

	return render_template('crear_comprador.html',form_comprador=comprador,log=loge)

@buyer.route('/editarcomprador/<string:id>',methods=['GET','POST'])
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
			success_message='Se actualizo correctamente al comprador {}'.format(comprador_encontrado.nombre_comprador)
			flash(success_message,category='message')

	return render_template('editar_comprador.html',log=loge,form_compra=comprador_encontrado)

@buyer.route('/eliminarcomprador/<string:id>',methods=['GET','POST'])
def eliminarcomprador(id):
	comprador_encontrado=Comprador.query.get(id)
	if comprador_encontrado is not None:
		nombre_comprador=comprador_encontrado.get_nombre()
		db.session.delete(comprador_encontrado)
		success_message='Se elimino correctamente al comprador {}'.format(nombre_comprador)
		flash(success_message,category='message')
	else:
		error_message='No se pudo eliminar el comprador'
		flash(error_message,category='error')
	return redirect(url_for('buyer.vercompradores'))

@buyer.route('/vercompradores',methods=['GET','POST'])
def vercompradores():
	dni_comprador=request.form.get('dni_comprador')
	if dni_comprador and request.method=='POST':
		if dni_comprador=='*':
			compradores=Comprador.query.all()
		else:
			compradores=Comprador.query.filter_by(dni=dni_comprador).all()
		return render_template('ver_compradores.html',form_comprador=compradores,log=loge)
	return render_template('ver_compradores.html',log=loge)

@buyer.route('/buscarcompradorbydni',methods=['GET','POST'])
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
	return redirect(url_for('product.buscar_producto'))