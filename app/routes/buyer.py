from flask import Blueprint, jsonify,request,render_template,redirect,url_for,session,flash
from ..models.modelos import Comprador
from flask_login import current_user,login_required

from app import db

buyer=Blueprint("buyer",__name__)

@buyer.route('/crearcomprador',methods=['GET','POST'])
@login_required
def crearcomprador():
	# Obtener los datos del formulario de la peticion
	# y crear una instancia del formulario de comprador
	comprador_nombre = request.form.get('nombre_comprador').strip().upper()
	comprador_dni = request.form.get('dni').strip().upper()
	comprador_direccion = request.form.get('direccion_comprador').strip().upper()
	comprador_numero_telefono = request.form.get('numero_telefono_comprador').strip().upper()
	comprador_tipo = request.form.get('tipo_comprador')
	if request.method=='POST':
		# Verificar si el comprador ya existe
		existe_comprador = Comprador.query.filter_by(dni=comprador_dni).first()

		if existe_comprador is None:
			nuevo_comprador = Comprador(comprador_nombre,comprador_numero_telefono,comprador_direccion,comprador_dni,comprador_tipo)
			db.session.add(nuevo_comprador)
			db.session.commit()
			succes_message = 'Se creo el usuario {}'.format(nuevo_comprador.nombre_comprador)
			flash(succes_message,category='message')
			return redirect(url_for('buyer.vercompradores'))
		else:
			error_message='No se puede crear el comprador, este ya se encuentra registrado'
			flash(error_message,category='error')
			return redirect(url_for('buyer.crearcomprador'))
	else:
		return jsonify({'message':'No se puede crear al comprador'},404)

@buyer.route('/editarcomprador/<string:id>',methods=['PUT'])
@login_required
def editarcomprador(id):
	comprador_encontrado=Comprador.query.get(id)
	data = request.get_json()
	print(data)
	comprador_nombre = data.get('nombre')
	comprador_numero_telefono = data.get('numero')
	comprador_tipo_comprador = data.get('tipo')
	comprador_direccion = data.get('direccion')
	comprador_dni = data.get('dni')

	if request.method=='PUT':
		if comprador_encontrado is not None:
			comprador_encontrado.nombre_comprador=comprador_nombre
			comprador_encontrado.numero_telefono_comprador=comprador_numero_telefono
			comprador_encontrado.tipo_comprador=comprador_tipo_comprador
			comprador_encontrado.direccion_comprador=comprador_direccion
			comprador_encontrado.dni=comprador_dni

			db.session.add(comprador_encontrado)
			db.session.commit()
			success_message='Se actualizo correctamente al comprador {}'.format(comprador_encontrado.nombre_comprador)
			return jsonify({'message':success_message,"status":"ok"},200)
		else:
			error_message='No se pudo actualizar el comprador'
			return jsonify({'message':error_message,"status":"error"},404)
	else:
		return jsonify({'message':'No se puede actualizar al comprador'},404)
	
@buyer.route('/eliminarcomprador/<string:id>',methods=['GET','DELETE'])
@login_required
def eliminarcomprador(id):
	comprador_encontrado=Comprador.query.get(id)
	if comprador_encontrado is not None:
		nombre_comprador=comprador_encontrado.get_nombre()
		db.session.delete(comprador_encontrado)
		success_message='Se elimino correctamente al comprador {}'.format(nombre_comprador)
		return jsonify({'message':success_message,"status":"ok"},200)
	else:
		error_message='No se pudo eliminar el comprador'
		flash(error_message,category='error')
		return jsonify({'message':error_message,"status":"error"},404)

@buyer.route('/vercompradores',methods=['GET','POST'])
@login_required
def vercompradores():
#	dni_comprador=request.form.get('dni_comprador')
#	if dni_comprador and request.method=='POST':
#		if dni_comprador=='*':
#			compradores=Comprador.query.all()
#		else:
#			compradores=Comprador.query.filter_by(dni=dni_comprador).all()
#		return render_template('ver_compradores.html',form_comprador=compradores,log=loge)
	compradores = Comprador.query.all()
	return render_template('ver_compradores.html',compradores=compradores)

@buyer.route('/buscarcompradorbydni',methods=['GET','POST'])
def buscarcompradorbydni():
	data=request.get_json()
	dni=data['dni_comprador']
	if dni and request.method=='POST':
		comprador=Comprador.query.filter_by(dni=dni).first()
		if comprador:
			return jsonify({'message':'Se obtuvo el comprador correctamente','nombre_comprador':comprador.get_nombre(),'direccion_comprador':comprador.get_direccion()
				   ,'dni_comprador':comprador.get_dni(),'telefono_comprador':comprador.get_telefono()
				   },200)
		else:
			return jsonify({'message':'El comprador no existe porfavor cree uno'},404)
	
