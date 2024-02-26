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
	comprador_nombre = request.form.get('nombre_comprador').strip().upper() or 'VARIOS'
	comprador_dni = request.form.get('dni').strip().upper() or '*'
	comprador_direccion = request.form.get('direccion_comprador').strip().upper() or '*'
	comprador_numero_telefono = request.form.get('numero_telefono_comprador').strip().upper() or '*'
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
	print(comprador_nombre,comprador_numero_telefono,comprador_tipo_comprador,comprador_direccion,comprador_dni)
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
		try:
			nombre_comprador = comprador_encontrado.get_nombre()
			db.session.delete(comprador_encontrado)
			db.session.commit()
			success_message = 'Se eliminó correctamente al comprador {}'.format(nombre_comprador)
			return jsonify({'message': success_message, "status": "ok"}, 200)
		except Exception as e:
			db.session.rollback()
			error_message = 'No se pudo eliminar el comprador: {}'.format(str(e))
			return jsonify({'message': error_message, "status": "error"}, 500)
	else:
		error_message='No se pudo eliminar el comprador'
		return jsonify({'message':error_message,"status":"error"},404)

@buyer.route('/vercompradores',methods=['GET','POST'])
@login_required
def vercompradores():

	# Agregar queries para recibir dni o nombre de comprador.
	# request.args.get('dni_comprador',default='*',type=str)
	nombre = request.args.get('submit_buscar_comprador',default=None,type=str)
	dni = request.args.get('submit_buscar_dni',default=None,type=str)
	compradores = Comprador.get_compradores_filtrados(nombre,dni)
	return render_template('ver_compradores.html',compradores=compradores)
