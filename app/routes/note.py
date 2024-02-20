from decimal import Decimal
from flask import Blueprint,request,render_template,redirect,url_for,session,flash,jsonify
from ..models.modelos import Comprador,Nota_de_Pedido,Producto
from sqlalchemy import asc, desc
from datetime import datetime, timedelta
import json
from app import db

note=Blueprint("note",__name__)

@note.before_request
def beforerequest():
    global loge
    loge=False
    global produ 
    produ=False
    
    if 'username' in session:
        loge=True
    if 'producto' in session:
        produ=True
#Utilizando actualmente
@note.route('/crearnotaventa',methods=['GET','POST'])
def crear_nota_venta():
	if request.method=='POST':
		data= request.get_json()
		nombre= data['nombre_comprador'] if data['nombre_comprador'] else "Varios"
		direccion=data['direccion_comprador'] if data['direccion_comprador'] else "-"
		dni=data['dni_comprador'] if data['dni_comprador'] else "-"
		telefono=data['telefono_comprador'] if data['telefono_comprador'] else "-"
		estado_nota=data['inputEstado1'] if data['inputEstado1'] else None
		estado_nota_2=data['inputEstado2'] if data['inputEstado2'] else None
		productos=data['productos']
		
		total_venta= Decimal(data['total_venta']).quantize(Decimal("1e-{0}".format(2))) # Suma total de todos los productos
		total_pagado= Decimal(data['total_pagado']).quantize(Decimal("1e-{0}".format(2))) # Valor total pagado por el cliente
	
		acuenta= True if data['acuenta'] =='True' else False
		
		vuelto = Decimal(data['vuelto']).quantize(Decimal("1e-{0}".format(2))) if data['vuelto'] else 0.00 # Vuelto que se le da al cliente

		pago_Efectivo = Decimal(data['pagoEfectivoInput']).quantize(Decimal("1e-{0}".format(2)))  if  data['pagoEfectivoInput'] else 0.00 # Pago en efectivo
		pago_Visa = Decimal(data['pagoVisaInput']).quantize(Decimal("1e-{0}".format(2))) if data['pagoVisaInput']  else 0.00 # Pago con tarjeta visa
		pago_BCP = Decimal(data['pagoBCPInput']).quantize(Decimal("1e-{0}".format(2))) if data['pagoBCPInput']  else 0.00 # Pago con tarjeta BCP
		pago_BBVA = Decimal(data['pagoBBVAInput']).quantize(Decimal("1e-{0}".format(2))) if data['pagoBBVAInput'] else 0.00
		pago_YAPE = Decimal(data['pagoYAPEInput']).quantize(Decimal("1e-{0}".format(2))) if data['pagoYAPEInput'] else 0.00
		
		existe_comprador=Comprador.query.filter_by(dni=dni).first()
		estado_nota=estado_nota+"-"+estado_nota_2
		if existe_comprador:
			datos_producto_json= json.dumps(productos)
			if acuenta:
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,deuda=total_venta-total_pagado,acuenta=total_pagado,comprador_id=existe_comprador.id
						,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE,bool_acuenta=True,bool_deuda=True)
				nota.comentario="Dejo a cuenta S/ {} soles. ".format(total_pagado)
			else:
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,comprador_id=existe_comprador.id,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE)
				nota.comentario=""
			# Actualizando stock de productos en la bse de datos
			for product in productos:
				producto=Producto.query.filter_by(nombre_producto=product['nombre_producto']).first()
				producto.stock-= Decimal(product['cantidad']).quantize(Decimal("1e-{0}".format(2)))
				db.session.add(producto)
				db.session.commit()
			if nota:
				db.session.add(nota)
				db.session.commit()
				return jsonify({'message':'Se creo la nota de pedido para {}'.format(nombre),'id':nota.get_id()},201)
			else:
				return jsonify({'message':'No se pudo crear la nota de pedido, intentelo nuevamente'},400)

		else:
			datos_producto_json= json.dumps(productos)
			comprador_nuevo=Comprador(nombre,telefono,direccion,dni)
			db.session.add(comprador_nuevo)
			db.session.commit()
			if acuenta:
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,deuda=total_venta-total_pagado,acuenta=total_pagado,comprador_id=comprador_nuevo.id,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE,bool_acuenta=True,bool_deuda=True)
				nota.comentario="Dejo a cuenta S/ {} soles. ".format(total_pagado)
			else:
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,comprador_id=comprador_nuevo.id,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE)
				nota.comentario=""
			# Actualizando stock de productos en la bse de datos
			for product in productos:
				producto=Producto.query.filter_by(nombre_producto=product['nombre_producto']).first()
				producto.stock-= Decimal(product['cantidad']).quantize(Decimal("1e-{0}".format(2)))
				db.session.add(producto)
				db.session.commit()
			if nota:
				db.session.add(nota)
				db.session.commit()

				return jsonify({'message':'Se creo la nota de pedido para {} y se registro como nuevo comprador'.format(nombre),'id':nota.get_id()},201)
			else:
				return jsonify({'message':'No se pudo crear la nota de pedido, intentelo nuevamente'},400)			

	return render_template('nota_pedido.html')

# Va a existir una ruta para  editar solamente la nota de pedido la cual va a ser la misma que la de crear nota de pedido en vista pero con un id de la nota de pedido
# Creo tendria que tener otra diferentes nombres en LocalStorage para cuando me encuentro en la pantalla de edicion de nota de pedido.

@note.route('/editarnotaventa/<string:id>',methods=['GET','POST'])
def editarnotaventa(id=None):
	nota=Nota_de_Pedido.query.get(id)
	if nota and request.method=='GET':
		#Guardando la informacion de los productos en sesiones
		session['id_nota']=nota.get_id()
		session['productos']=nota.get_nombre_producto()
		session['total_venta']=nota.get_total_venta()
		return render_template('nota_pedido_editar.html',nota=nota.get_json())

	elif nota and request.method=='POST':
		print("Entro al POST de editar nota de pedido")
		data= request.get_json()

		nombre= data['nombre_comprador'] if data['nombre_comprador'] else nota.get_nombre_comprador()
		direccion=data['direccion_comprador'] if data['direccion_comprador'] else nota.get_direccion()
		#dni=data['dni_comprador'] if data['dni_comprador'] else nota.get_dni_nota()
		telefono=data['telefono_comprador'] if data['telefono_comprador'] else nota.get_telefono_nota()
		estado_nota=data['inputEstado1'] if data['inputEstado1'] else None
		estado_nota_2=data['inputEstado2'] if data['inputEstado2'] else None
		productos=data['productos']

		total_venta= Decimal(data['total_venta']).quantize(Decimal("1e-{0}".format(2))) # Suma total de todos los productos
		total_pagado= Decimal(data['total_pagado']).quantize(Decimal("1e-{0}".format(2))) # Valor total pagado por el cliente

		acuenta= True if data['acuenta'] =='True' else False

		vuelto = Decimal(data['vuelto']).quantize(Decimal("1e-{0}".format(2))) if data['vuelto'] else 0.00 # Vuelto que se le da al cliente

		pago_Efectivo = Decimal(data['pagoEfectivo']).quantize(Decimal("1e-{0}".format(2)))  if  data.get('pagoEfectivo', "0") != "0" else 0.00 # Pago en efectivo
		pago_Visa = Decimal(data['pagoVisa']).quantize(Decimal("1e-{0}".format(2))) if data.get('pagoVisa', "0") != "0"  else 0.00 # Pago con tarjeta visa
		pago_BCP = Decimal(data['pagoBCP']).quantize(Decimal("1e-{0}".format(2))) if data.get('pagoBCP', "0") != "0" else 0.00 # Pago con tarjeta BCP
		pago_BBVA = Decimal(data['pagoBBVA']).quantize(Decimal("1e-{0}".format(2))) if data.get('pagoBBVA', "0") != "0" else 0.00
		pago_YAPE = Decimal(data['pagoYAPE']).quantize(Decimal("1e-{0}".format(2))) if data.get('pagoYAPE', "0") != "0" else 0.00

		# Comienzo de la edicion de la nota de pedido
		#Data Personal del comprador
		nota.nombre_comprador=nombre 
		nota.direccion_comprador=direccion		
		nota.numero_comprador=telefono

		#Data de la venta
		nota.estado=estado_nota+"-"+estado_nota_2
		nota.total_venta=total_venta
		#Recordar acuenta y deuda -> acuenta es el pago(total_pagado) que realizo el cliente cuando es True el dato
		# Y deuda es el total_venta - total_pagado, la diferencia que esta pendiente por pagar

		nota.vuelto=vuelto
		nota.pagoVisa=pago_Visa
		nota.pagoEfectivo=pago_Efectivo
		nota.pagoBBVA=pago_BBVA
		nota.pagoBCP=pago_BCP
		nota.pagoYape=pago_YAPE

		nota.deuda=total_venta-total_pagado
		if acuenta:
			nota.acuenta=total_pagado
		nota.bool_acuenta=acuenta

		#Data de los productos
		# Validar como se realizaria el descuento de stock dado que se esta editando la nota de pedido y puede que no se repita la cantidad disminuida.
		nota.nombre_producto=json.dumps(productos)

		#Guardando los cambios
		db.session.add(nota)
		try:
			db.session.commit()
			return jsonify({'message':'Se edito la nota de pedido para {}'.format(nombre)},200)
		except:
			return jsonify({'message':'No se pudo editar la nota de pedido, intentelo nuevamente'},400)

	else:
		return jsonify({'message':'No se pudo cargar la nota de pedido para editar'},400)

#Utilizando actualmente
@note.route('/vernotapedido/<string:id>',methods=['GET'])
def vernotapedido(id):
	nota=Nota_de_Pedido.query.get(id)
	if nota:
		return jsonify(nota.get_json(),200)
	else:
		return jsonify({'message':'No se pudo encontrar la nota de pedido'},400)


@note.route('/editarnotaventa/',methods=['GET','POST'])
def editarNotaVentaNoId():
	#Check for requirements, if they want to generate a new one or only edit.
	# nota=Nota_de_Pedido.query.get(session['id_nota'])
	nombre_comprador=request.form.get('comprador_name')
	direccion_comprador=request.form.get('direccion_comprador')
	dni_comprador=request.form.get('dni_comprador')
	telefono_comprador=request.form.get('telefono_comprador')
	estado_nota=request.form.get('estado')
	estado_nota_2=request.form.get('estado2')
	total_venta=0

	if 'producto' in session:
		session.modified=True
		for key,product in session['producto'].items():
			total_venta=total_venta+session['producto'][key]['precio_individual']

		session['total_venta']=total_venta.__round__(2)
		if estado_nota and request.method == 'POST':
			estado_nota=estado_nota+estado_nota_2
			datos_producto_json= json.dumps(session['producto'])
			existe_comprador=Comprador.query.filter_by(dni=dni_comprador).first()
			if existe_comprador:
				nota =Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,telefono_comprador,dni_comprador,comprador_id=existe_comprador)
			else:
				nota =Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,telefono_comprador,dni_comprador)
			# nota.nombre_comprador=nombre_comprador
			# nota.total_venta=total_venta
			# nota.direccion_comprador=direccion_comprador
			# nota.dni_comprador=dni_comprador
			# nota.telefono_comprador=telefono_comprador
			# nota.nombre_producto=datos_producto_json
			# nota.fecha_creacion=datetime.today()
			# nota.estado=estado_nota
			
			# for key,product in session['producto'].items():
			# 	producto=Producto.query.filter_by(nombre_producto=session['producto'][key]['name']).first()
			# 	print(producto.stock)
			# 	producto.stock-=session['producto'][key]['cantidad']
			if nota is not None:
				db.session.add(nota)
				db.session.commit()
				session.modified = True
				session['nombre_comprador']=nombre_comprador
				session['direccion_comprador']=direccion_comprador
				session['dni_comprador']=dni_comprador
				session['telefono_comprador']=telefono_comprador
				session['numero_nota']=nota.get_id()
				session['fecha_nota']=nota.get_fecha()
				session['estado_nota']=estado_nota
				succes_message='Se creo la nota de pedido para {} y se registro como nuevo comprador, ID:{}'.format(nota.get_nombre_comprador(),nota.get_id())
				flash(succes_message,category='message')
	return redirect(url_for('product.buscar_producto'))
	
@note.route('/convertirNota/<string:id>',methods=['GET','POST'])
def convertirNota(id):
	#Check for requirements if they want to create a new one.
	nota_pedido=Nota_de_Pedido.query.get(id)
	if nota_pedido is not None:
		# existe_comprador=Comprador.query.filter_by(dni=nota_pedido.get_dni_nota()).first()
		if nota_pedido.get_comprador_id():
			nota =Nota_de_Pedido(nota_pedido.get_nombre_producto(),nota_pedido.get_total_venta(),nota_pedido.get_nombre_comprador(),nota_pedido.get_direccion(),nota_pedido.get_estado(),nota_pedido.get_telefono_nota(),nota_pedido.get_dni_nota(),comprador_id=nota_pedido.get_comprador_id())
		else:
			nota =Nota_de_Pedido(nota_pedido.get_nombre_producto(),nota_pedido.get_total_venta(),nota_pedido.get_nombre_comprador(),nota_pedido.get_direccion(),nota_pedido.get_estado(),nota_pedido.get_telefono_nota(),nota_pedido.get_dni_nota())
		nota.estado='cancelado-'
		db.session.add(nota)
		db.session.commit()
		# db.session.delete(nota_pedido)
		succes_message='Se convirtio la Proforma a una Nota de Pedido con ID: {}'.format(nota.id)
		flash(succes_message,'message')
	else:
		flash('No se pudo convertir la Proforma en una Nota','error')
	return redirect(url_for('note.vernotapedido'))

@note.route('/editarnota/<string:id>',methods=['GET','POST'])
def editarnota(id):
	nota=Nota_de_Pedido.query.get(id)
	nombre_comprador=request.form.get('comprador_name')
	direccion_comprador=request.form.get('direccion_comprador')
	estado_nota=request.form.get('estado')
	estado_nota_2=request.form.get('estado2')
	fecha_adicional=request.form.get('fecha_adicional')
	deuda_actual=request.form.get('deuda')
	comentario=request.form.get('comentario')

	if nota and nombre_comprador and direccion_comprador and estado_nota and request.method=='POST':
		nota.nombre_comprador=nombre_comprador
		nota.direccion_comprador=direccion_comprador
		nota.estado=estado_nota+estado_nota_2
		if deuda_actual is not None:
			if float(deuda_actual)>0.0:
				nota.acuenta=float(deuda_actual)
				nota.deuda=float(deuda_actual)
			else:
				nota.acuenta=nota.get_deuda()
				nota.deuda=float(deuda_actual)
		nota.fecha_creacion=fecha_adicional
		nota.fecha_cancelacion=fecha_adicional
		nota.comentario=comentario	
		db.session.add(nota)
		succes_message='Se actualizo la nota de pedido de {}'.format(nota.nombre_comprador)
		flash(succes_message,category='message')
		return redirect(url_for("note.editarnota",id=id))
	return render_template('editar_nota_id.html',nota=nota,log=loge)


@note.route('/anularnota/<string:id>',methods=["GET"])
def anularnota(id):
	nota=Nota_de_Pedido.query.get(id)
	if nota:
		nota.estado='ANULADO-'
		db.session.add(nota)
		succes_message='Se ANULO la nota de pedido {}'.format(nota.id)
		flash(succes_message,category='message')
	return redirect(url_for('note.vernotapedido'))

#Utilizando actualmente
@note.route('/ver_notas_pedido',methods=['GET','POST'])
def ver_notas_pedido():
	# request.args.get('page', 1, type=int) , de esta manera obtenemos args desde url

	if request.method=='GET':
		#Verificar la cantidad de argumentos que estoy recibiendo
		args=request.args
		arg_names=list(args.keys())

		# Inicializando variables
		total_venta_resumen=Decimal(0).quantize(Decimal("1e-{0}".format(2)))
		total_pago_efectivo=Decimal(0).quantize(Decimal("1e-{0}".format(2)))
		total_pago_visa=Decimal(0).quantize(Decimal("1e-{0}".format(2)))
		total_pago_bcp=Decimal(0).quantize(Decimal("1e-{0}".format(2)))
		total_pago_bbva=Decimal(0).quantize(Decimal("1e-{0}".format(2)))
		total_pago_yape=Decimal(0).quantize(Decimal("1e-{0}".format(2)))

		if 'fecha_inicio' in arg_names and 'fecha_final' in arg_names and 'comprador' in arg_names:
			fecha_inicio_actual = request.args.get('fecha_inicio', default=None, type=str)
			fecha_final_actual = request.args.get('fecha_final', default=None, type=str)
			comprador=request.args.get('comprador',default=None,type=str)

			# Verificar si se esta filtrando por estado
			estado_nota=request.args.get('estado',default='',type=str)
			estado_nota_2=request.args.get('estado2',default='',type=str)
			estado_nota_final=estado_nota+"-"+estado_nota_2

			filtro_estado = None

			if estado_nota and estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado == estado_nota_final
			elif estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota_2 + '%')
			elif estado_nota:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota + '%')

			# Resumen de Ventas
			if filtro_estado is not None:
				if fecha_final_actual and fecha_inicio_actual and comprador:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),Nota_de_Pedido.nombre_comprador.like('%'+comprador+'%'),filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				elif fecha_final_actual and fecha_inicio_actual:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				elif comprador:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+comprador+'%'),filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None
			else:
				if fecha_final_actual and fecha_inicio_actual and comprador:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),Nota_de_Pedido.nombre_comprador.like('%'+comprador+'%')).order_by(asc(Nota_de_Pedido.id)).all()
				elif fecha_final_actual and fecha_inicio_actual:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual)).order_by(asc(Nota_de_Pedido.id)).all()
				elif comprador:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+comprador+'%')).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None
			
			# Resumen de Ventas
			if notas_pedidos_actual:
				json_notas_pedidos_actual=[nota.get_json() for nota in notas_pedidos_actual]
				for nota in json_notas_pedidos_actual:
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO']:
						# Suma general
						total_venta_resumen+=nota['total_venta']
						# Suma por Efectivo
						total_pago_efectivo+=nota['pagoEfectivo']
						# Suma por Visa
						total_pago_visa+=nota['pagoVisa']
						# Suma por BCP
						total_pago_bcp+=nota['pagoBCP']
						# Suma por BBVA
						total_pago_bbva+=nota['pagoBBVA']
						# Suma por Yape
						total_pago_yape+=nota['pagoYape']
				return render_template('ver_notas_pedidos.html',nota_pedido=json_notas_pedidos_actual,total_venta_resumen=total_venta_resumen,total_pago_efectivo=total_pago_efectivo,total_pago_visa=total_pago_visa,total_pago_bcp=total_pago_bcp,total_pago_bbva=total_pago_bbva,total_pago_yape=total_pago_yape)
			else:
				flash('No se pudo encontrar ninguna nota de pedido','error')
				return render_template('ver_notas_pedidos.html')

		elif 'fecha_inicio' in arg_names and 'fecha_final' in arg_names and 'dni' in arg_names:
			fecha_inicio_actual = request.args.get('fecha_inicio', default=None, type=str)
			fecha_final_actual = request.args.get('fecha_final', default=None, type=str)
			dni=request.args.get('dni',default=None,type=str)

			#Verificar si se esta filtrando por estado
			estado_nota=request.args.get('estado',default='',type=str)
			estado_nota_2=request.args.get('estado2',default='',type=str)
			estado_nota_final=estado_nota+"-"+estado_nota_2

			filtro_estado = None

			if estado_nota and estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado == estado_nota_final
			elif estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota_2 + '%')
			elif estado_nota:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota + '%')
			
			if filtro_estado is not None:
				if fecha_final_actual and fecha_inicio_actual and dni:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),Nota_de_Pedido.dni_comprador==dni,filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				elif fecha_final_actual and fecha_inicio_actual:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),Nota_de_Pedido.dni_comprador==dni,filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				elif dni:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.dni_comprador==dni,filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None
			else:
				if fecha_final_actual and fecha_inicio_actual and dni:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),Nota_de_Pedido.dni_comprador==dni).order_by(asc(Nota_de_Pedido.id)).all()
				elif fecha_final_actual and fecha_inicio_actual:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),Nota_de_Pedido.dni_comprador==dni).order_by(asc(Nota_de_Pedido.id)).all()
				elif dni:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.dni_comprador==dni).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None

			# Resumen de Ventas
			if notas_pedidos_actual:
				json_notas_pedidos_actual=[nota.get_json() for nota in notas_pedidos_actual]
				for nota in json_notas_pedidos_actual:
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO']:
						# Suma general
						total_venta_resumen+=nota['total_venta']
						# Suma por Efectivo
						total_pago_efectivo+=nota['pagoEfectivo']
						# Suma por Visa
						total_pago_visa+=nota['pagoVisa']
						# Suma por BCP
						total_pago_bcp+=nota['pagoBCP']
						# Suma por BBVA
						total_pago_bbva+=nota['pagoBBVA']
						# Suma por Yape
						total_pago_yape+=nota['pagoYape']
				return render_template('ver_notas_pedidos.html',nota_pedido=json_notas_pedidos_actual,total_venta_resumen=total_venta_resumen,total_pago_efectivo=total_pago_efectivo,total_pago_visa=total_pago_visa,total_pago_bcp=total_pago_bcp,total_pago_bbva=total_pago_bbva,total_pago_yape=total_pago_yape)
			else:
				flash('No se pudo encontrar ninguna nota de pedido','error')
				return render_template('ver_notas_pedidos.html')

		elif 'fecha_inicio' in arg_names and 'fecha_final' in arg_names:
			fecha_inicio_actual = request.args.get('fecha_inicio', default=(datetime.today().date()).strftime('%Y/%m/%d'), type=str)
			fecha_final_actual = request.args.get('fecha_final', default=(datetime.today().date() + timedelta(days=1)).strftime('%Y/%m/%d'), type=str)

			# Verificar si se esta filtrando por estado
			estado_nota=request.args.get('estado',default='',type=str)
			estado_nota_2=request.args.get('estado2',default='',type=str)
			estado_nota_final=estado_nota+"-"+estado_nota_2

			filtro_estado = None

			if estado_nota and estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado == estado_nota_final
			elif estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota_2 + '%')
			elif estado_nota:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota + '%')

			if filtro_estado is not None:
				if fecha_final_actual and fecha_inicio_actual:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual),filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None
			else:
				if fecha_final_actual and fecha_inicio_actual:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio_actual,fecha_final_actual)).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None

			# Resumen de Ventas
			if notas_pedidos_actual:
				json_notas_pedidos_actual=[nota.get_json() for nota in notas_pedidos_actual]
				for nota in json_notas_pedidos_actual:
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO']:
						# Suma general
						total_venta_resumen+=nota['total_venta']
						# Suma por Efectivo
						total_pago_efectivo+=nota['pagoEfectivo']
						# Suma por Visa
						total_pago_visa+=nota['pagoVisa']
						# Suma por BCP
						total_pago_bcp+=nota['pagoBCP']
						# Suma por BBVA
						total_pago_bbva+=nota['pagoBBVA']
						# Suma por Yape
						total_pago_yape+=nota['pagoYape']
				return render_template('ver_notas_pedidos.html',nota_pedido=json_notas_pedidos_actual,total_venta_resumen=total_venta_resumen,total_pago_efectivo=total_pago_efectivo,total_pago_visa=total_pago_visa,total_pago_bcp=total_pago_bcp,total_pago_bbva=total_pago_bbva,total_pago_yape=total_pago_yape)
			else:
				flash('No se pudo encontrar ninguna nota de pedido','error')
				return render_template('ver_notas_pedidos.html')

		elif 'comprador' in arg_names:
			comprador=request.args.get('comprador',default='VARIOS',type=str)

			# Verificar si se esta filtrando por estado
			estado_nota=request.args.get('estado',default='',type=str)
			estado_nota_2=request.args.get('estado2',default='',type=str)
			estado_nota_final=estado_nota+"-"+estado_nota_2

			filtro_estado = None
			if estado_nota and estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado == estado_nota_final
			elif estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota_2 + '%')
			elif estado_nota:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota + '%')
			
			if filtro_estado is not None:
				if comprador:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+comprador+'%'),filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None
			else:
				if comprador:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+comprador+'%')).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None

			# Resumen de Ventas
			if notas_pedidos_actual:
				json_notas_pedidos_actual=[nota.get_json() for nota in notas_pedidos_actual]
				for nota in json_notas_pedidos_actual:
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO']:
						# Suma general
						total_venta_resumen+=nota['total_venta']
						# Suma por Efectivo
						total_pago_efectivo+=nota['pagoEfectivo']
						# Suma por Visa
						total_pago_visa+=nota['pagoVisa']
						# Suma por BCP
						total_pago_bcp+=nota['pagoBCP']
						# Suma por BBVA
						total_pago_bbva+=nota['pagoBBVA']
						# Suma por Yape
						total_pago_yape+=nota['pagoYape']
				return render_template('ver_notas_pedidos.html',nota_pedido=json_notas_pedidos_actual,total_venta_resumen=total_venta_resumen,total_pago_efectivo=total_pago_efectivo,total_pago_visa=total_pago_visa,total_pago_bcp=total_pago_bcp,total_pago_bbva=total_pago_bbva,total_pago_yape=total_pago_yape)
			else:
				flash('No se pudo encontrar ninguna nota de pedido','error')
				return render_template('ver_notas_pedidos.html')

		elif 'dni' in arg_names:
			dni=request.args.get('dni',default='',type=str)
			
			estado_nota=request.args.get('estado',default='',type=str)
			estado_nota_2=request.args.get('estado2',default='',type=str)
			estado_nota_final=estado_nota+"-"+estado_nota_2

			filtro_estado = None
			if estado_nota and estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado == estado_nota_final
			elif estado_nota_2:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota_2 + '%')
			elif estado_nota:
				filtro_estado = Nota_de_Pedido.estado.like('%' + estado_nota + '%')
			
			# Verificar si se esta filtrando por estado
			if filtro_estado is not None:
				if dni:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.dni_comprador==dni,filtro_estado).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None
			else:
				if dni:
					notas_pedidos_actual=Nota_de_Pedido.query.filter(Nota_de_Pedido.dni_comprador==dni).order_by(asc(Nota_de_Pedido.id)).all()
				else:
					notas_pedidos_actual = None
			
			# Resumen de Ventas
			if notas_pedidos_actual:
				json_notas_pedidos_actual=[nota.get_json() for nota in notas_pedidos_actual]
				for nota in json_notas_pedidos_actual:
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO']:
						# Suma general
						total_venta_resumen+=nota['total_venta']
						# Suma por Efectivo
						total_pago_efectivo+=nota['pagoEfectivo']
						# Suma por Visa
						total_pago_visa+=nota['pagoVisa']
						# Suma por BCP
						total_pago_bcp+=nota['pagoBCP']
						# Suma por BBVA
						total_pago_bbva+=nota['pagoBBVA']
						# Suma por Yape
						total_pago_yape+=nota['pagoYape']
				return render_template('ver_notas_pedidos.html',nota_pedido=json_notas_pedidos_actual,total_venta_resumen=total_venta_resumen,total_pago_efectivo=total_pago_efectivo,total_pago_visa=total_pago_visa,total_pago_bcp=total_pago_bcp,total_pago_bbva=total_pago_bbva,total_pago_yape=total_pago_yape)
			else:
				flash('No se pudo encontrar ninguna nota de pedido','error')
				return render_template('ver_notas_pedidos.html')
			
		elif 'id' in arg_names:
			id=request.args.get('id',default='',type=str)
			nota=Nota_de_Pedido.query.get(id)
			if nota:
				json_notas_pedidos_actual=[nota.get_json()]
				for nota in json_notas_pedidos_actual:
						if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO']:
							# Suma general
							total_venta_resumen+=nota['total_venta']
							# Suma por Efectivo
							if nota['pagoEfectivo']:
								total_pago_efectivo+=nota['pagoEfectivo']
							# Suma por Visa
							if nota['pagoVisa']:
								total_pago_visa+=nota['pagoVisa']
							# Suma por BCP
							if nota['pagoBCP']:
								total_pago_bcp+=nota['pagoBCP']
							# Suma por BBVA
							if nota['pagoBBVA']:
								total_pago_bbva+=nota['pagoBBVA']
							# Suma por Yape
							if nota['pagoYape']:
								total_pago_yape+=nota['pagoYape']
				return render_template('ver_notas_pedidos.html',nota_pedido=json_notas_pedidos_actual,total_venta_resumen=total_venta_resumen,total_pago_efectivo=total_pago_efectivo,total_pago_visa=total_pago_visa,total_pago_bcp=total_pago_bcp,total_pago_bbva=total_pago_bbva,total_pago_yape=total_pago_yape)
			else:
				flash('No se pudo encontrar la nota de pedido con el ID: {}'.format(id),'error')
				return render_template('ver_notas_pedidos.html')
		else:
			return render_template('ver_notas_pedidos.html')
	else:
		return jsonify({'message':'No se pudo cargar las notas de pedido'},400)

@note.route('/vernotaID',methods=['GET','POST'])
def vernotaID():
	id=request.form.get('id_notas')
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if id and request.method=='POST':
		nota_pedido=Nota_de_Pedido.query.filter_by(id=id).all()
		if nota_pedido is not None:
			return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
		else :
			error_message='No se pudo encontrar la nota de pedido intente nuevamente'
			flash(error_message,category='error')
	return redirect(url_for('note.vernotapedido'))

@note.route('/vernotapedidobyID',methods=['GET','POST'])
def vernotapedido_id():

	id=request.form['notaid']
	nota=Nota_de_Pedido.query.get(id)
	notas=json.loads(nota.get_nombre_producto())
	if nota.notasdepedidos is None:
		telefono_comprador=nota.get_telefono_nota()
		dni_comprador=nota.get_dni_nota()
	else:
		telefono_comprador=nota.notasdepedidos.get_telefono()
		dni_comprador=nota.notasdepedidos.get_dni()
	return jsonify({'htmlresponse':render_template('ver_nota_id.html',nota=nota,notas=notas,telefono=telefono_comprador,dni=dni_comprador)})

@note.route('/imprimirresumen/<string:fecha>/<string:fecha_final>',methods=['GET','POST'])
def imprimirresumen(fecha,fecha_final):
	fecha=datetime.strptime(fecha, '%Y-%m-%d').date()
	fecha_final=datetime.strptime(fecha_final, '%Y-%m-%d').date()
	total_dia=0
	total_dia_visa=0
	total_dia_bcp=0
	total_dia_bbva=0
	total_dia_yape=0
	total_dia_por_cancelar=0
	nota_pedido=Nota_de_Pedido.query.order_by(asc(Nota_de_Pedido.id)).filter(Nota_de_Pedido.fecha_creacion.between(fecha,fecha_final)).all()
	if nota_pedido is not None:
		for note in nota_pedido:
			if note.get_estado() in ['cancelado-','cancelado-por-recoger','cancelado-entregado']:
				if note.get_acuenta()>0:
					total_dia+=note.get_acuenta()
				else:
					total_dia+=note.get_total_venta()
			elif note.get_estado() in ['cancelado-VISA-','cancelado-VISA-entregado','cancelado-VISA-por-recoger']:
				if note.get_acuenta()>0:
					total_dia_visa+=note.get_acuenta()
				else:
					total_dia_visa+=note.get_total_venta()

			elif note.get_estado() in ['por-cancelar-','por-cancelar-entregado','por-cancelar-por-recoger']:
				if note.get_acuenta()>0:
					total_dia_por_cancelar+=note.get_acuenta()
				else:
					total_dia_por_cancelar+=note.get_total_venta()
			elif note.get_estado() in ['cancelado-BCP-','cancelado-BCP-por-recoger','cancelado-BCP-entregado']:
				if note.get_acuenta()>0:
					total_dia_bcp+=note.get_acuenta()
				else:
					total_dia_bcp+=note.get_total_venta()
			elif note.get_estado() in ['cancelado-BBVA-','cancelado-BBVA-por-recoger','cancelado-BBVA-entregado']:
				if note.get_acuenta()>0:
					total_dia_bbva+=note.get_acuenta()
				else:
					total_dia_bbva+=note.get_total_venta()
			elif note.get_estado() in ['cancelado-YAPE-','cancelado-YAPE-por-recoger','cancelado-YAPE-entregado']:
				if note.get_acuenta()>0:
					total_dia_yape+=note.get_acuenta()
				else:
					total_dia_yape+=note.get_total_venta()

		return render_template('resumen_por_imprimir.html',nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar,tdbcp=total_dia_bcp,tdbbva=total_dia_bbva,tdy=total_dia_yape,fechita=fecha)
	else:
		error_message='No se pudo crear un resumen por que no existen notas de pedido'
		flash(error_message,category='error')
	return render_template('resumen_por_imprimir.html',td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar,tdbcp=total_dia_bcp,tdbbva=total_dia_bbva,tdy=total_dia_yape,fechita=fecha)



	debt=float(request.form['debt'])
	session['deuda']=0
	if request.method=='POST':
		session.modified=True
		if debt>=0 and debt<session['total_venta']:
			session['acuenta']=debt
		else:
			flash("No se puede actualizar el acuenta por que es mayor que el monto total.","error")
		return redirect(url_for('product.buscar_producto'))

	return redirect(url_for('product.buscar_producto'))
#Eliminar un producto de la nota de pedido
@note.route('/delete',methods=['POST'])
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
		return redirect(url_for('product.buscar_producto'))

	return redirect(url_for('product.buscar_producto'))

@note.route('/imprimir')
def imprimir():
	return render_template('imprimir.html',acuenta=session['acuenta'],deuda=session['deuda'])




#Utilizando actualmente
@note.route('/nuevoingresosalida',methods=['POST'])
def nuevoingresosalida():
	return jsonify({'message':'Llego el post','status':'success'},200)



#Utilizando actualmente
@note.route('/imprimire/<string:id>',methods=['GET','POST'])
def imprimire(id):
	nota=Nota_de_Pedido.query.get(id)
	notas= json.loads(nota.get_nombre_producto())
	print(notas)
	if nota.notasdepedidos is None:
		telefono_comprador=nota.get_telefono_nota()
		dni_comprador=nota.get_dni_nota()
	else:
		telefono_comprador=nota.notasdepedidos.get_telefono()
		dni_comprador=nota.notasdepedidos.get_dni()

	return render_template('imprimirid.html',nota=nota,notas=notas,telefono=telefono_comprador,dni=dni_comprador)
