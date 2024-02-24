from decimal import Decimal
from flask import Blueprint,request,render_template,session,flash,jsonify
from flask_login import current_user,login_required
from ..models.modelos import Comprador,Nota_de_Pedido,Producto,Detalle_Caja
from ..decorators import administrador_requerido
from sqlalchemy import asc
from datetime import datetime, timedelta
import json
from app import db

note=Blueprint("note",__name__)

#Utilizando actualmente
@note.route('/crearnotaventa',methods=['GET','POST'])
@login_required
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
		usuario_id = current_user.get_id()
		if existe_comprador:
			datos_producto_json= json.dumps(productos)
			if acuenta:
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,usuario_id,deuda=total_venta-total_pagado,acuenta=total_pagado,comprador_id=existe_comprador.id
						,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE,bool_acuenta=True,bool_deuda=True)
				nota.comentario="Dejo a cuenta S/ {} soles. ".format(total_pagado)
			else:
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,usuario_id,comprador_id=existe_comprador.id,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE)
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
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,usuario_id,deuda=total_venta-total_pagado,acuenta=total_pagado,comprador_id=comprador_nuevo.id,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE,bool_acuenta=True,bool_deuda=True)
				nota.comentario="Dejo a cuenta S/ {} soles. ".format(total_pagado)
			else:
				nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre,direccion,estado_nota,telefono,dni,usuario_id,comprador_id=comprador_nuevo.id,vuelto=vuelto,pagoVisa=pago_Visa,pagoEfectivo=pago_Efectivo,pagoBBVA=pago_BBVA,pagoBCP=pago_BCP,pagoYape=pago_YAPE)
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

#Utilizando actualmente
@note.route('/editarnotaventa/<string:id>',methods=['GET','POST'])
@login_required
def editarnotaventa(id=None):
	nota=Nota_de_Pedido.query.get(id)
	if nota and request.method=='GET':
		#Guardando la informacion de los productos en sesiones
		session['id_nota']=nota.get_id()
		session['productos']=nota.get_nombre_producto()
		session['total_venta']=nota.get_total_venta()
		return render_template('nota_pedido_editar.html',nota=nota.get_json())

	elif nota and request.method=='POST':
		data= request.get_json()

		nombre= data['nombre_comprador'] if data['nombre_comprador'] else nota.get_nombre_comprador()
		direccion=data['direccion_comprador'] if data['direccion_comprador'] else nota.get_direccion()
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
@login_required
def vernotapedido(id):
	nota=Nota_de_Pedido.query.get(id)
	if nota:
		return jsonify(nota.get_json(),200)
	else:
		return jsonify({'message':'No se pudo encontrar la nota de pedido'},400)

#Utilizando actualmente
@note.route('/anularnota/<string:id>',methods=["GET"])
@login_required
def anularnota(id):
	nota=Nota_de_Pedido.query.get(id)
	if nota:
		nota.estado='ANULADO-'
		nota.comentario="Nota de pedido anulada por el usuario {}".format(current_user.get_nombre())
		nota.bool_acuenta=False
		nota.bool_deuda=False
		nota.deuda=0		
		db.session.add(nota)
		succes_message='Se ANULO la nota de pedido {}'.format(nota.id)
		db.session.commit()

		return jsonify({'message':succes_message,'status':'success'},200)
	else:
		return jsonify({'message':'No se pudo encontrar la nota de pedido','status':'error'},400)

#Utilizando actualmente
@note.route('/eliminar-nota-pedido/<string:id>',methods=['GET'])
@login_required
@administrador_requerido
def eliminar_nota_pedido(id):
	nota=Nota_de_Pedido.query.get(id)
	if nota:
		try:
			db.session.delete(nota)
			db.session.commit()
			return jsonify({'message':'Se elimino la nota de pedido {}'.format(id),'status':'success'},200)
		except Exception as e:
			db.session.rollback()
			return jsonify({'message':'Error al eliminar la nota de pedido','status':'error','error': str(e)}, 500)
	else:
		return jsonify({'message':'No se pudo encontrar la nota de pedido','status':'error'},400)

#Utilizando actualmente
@note.route('/ver_notas_pedido',methods=['GET','POST'])
@login_required
def ver_notas_pedido():
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
					if (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
						# Suma general
						total_venta_resumen+=nota['acuenta']
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
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO'] or (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
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
						
					if (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
						# Suma general
						total_venta_resumen+=nota['acuenta']
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
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO'] or (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
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

					if (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
						# Suma general
						total_venta_resumen+=nota['acuenta']
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
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO'] or (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
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

					if (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
						# Suma general
						total_venta_resumen+=nota['acuenta']
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
					if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO'] or (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
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
					
					if (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
						# Suma general
						total_venta_resumen+=nota['acuenta']
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
						if nota['estado'] in ['CANCELADO-','CANCELADO--','CANCELADO-POR-RECOGER','CANCELADO-ENTREGADO'] or (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
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
						
						if (nota['estado'] in ['POR-CANCELAR-'] and nota['bool_acuenta']):
							# Suma general
							total_venta_resumen+=nota['acuenta']
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
				flash('No se pudo encontrar la nota de pedido con el ID: {}'.format(id),'error')
				return render_template('ver_notas_pedidos.html')
		else:
			return render_template('ver_notas_pedidos.html')
	else:
		return jsonify({'message':'No se pudo cargar las notas de pedido'},400)


#Utilizado actualmente
@note.route('/validar-deuda/<string:id>',methods=['GET'])
@login_required
def validar_deuda(id):
	nota=Nota_de_Pedido.query.get(id)
	#Validar si la nota existe
	if nota:
		deuda= nota.get_deuda()
		bool_deuda=nota.get_bool_deuda()
		if bool_deuda:
			return jsonify({'message':'La nota de pedido tiene una deuda pendiente','status':'success','deuda':deuda,'bool_deuda':bool_deuda},200)
		else:
			return jsonify({'message':'No se puede obtener la deuda por que ya esta cancelada','status':'error'},400)
	else:
		return jsonify({'message':'No se pudo encontrar la nota de pedido','status':'error'},400)

#Utilizando actualmente
@note.route('/nuevoingresosalida',methods=['POST'])
@login_required
def nuevoingresosalida():
	#Obtener los datos del formulario
	data = request.get_json()
	#Verificar si se recibio la data
	if data:
		fecha_creacion = data.get('inputFechaSalida',datetime.today()) 
		tipo =  data.get('inputTipoSalida',None)
		notaID = data.get('inputNotaID',None)
		comentario = data.get('inputComentario',None)
		usuario_id = current_user.get_id()

		pagoEfectivo = Decimal(data.get('pagoEfectivoInput',0.00)).quantize(Decimal("1e-{0}".format(2)))
		pagoVisa = Decimal(data.get('pagoVisaInput',0.00)).quantize(Decimal("1e-{0}".format(2)))
		pagoBCP = Decimal(data.get('pagoBCPInput',0.00)).quantize(Decimal("1e-{0}".format(2)))
		pagoBBVA = Decimal(data.get('pagoBBVAInput',0.00)).quantize(Decimal("1e-{0}".format(2)))
		pagoYAPE = Decimal(data.get('pagoYAPEInput',0.00)).quantize(Decimal("1e-{0}".format(2)))
		
		notapedido = None
		if notaID:
			notapedido = Nota_de_Pedido.query.get(notaID)

		if notapedido:
			# Si el tipo es INGRESO y tiene una deuda
			montoT = pagoEfectivo + pagoVisa + pagoBCP + pagoBBVA + pagoYAPE
			if tipo == "INGRESO" and notapedido.bool_deuda:
				if notapedido.deuda == montoT:
					try:
						notapedido.deuda = Decimal(0).quantize(Decimal("1e-{0}".format(2)))
						notapedido.bool_deuda = False
						notapedido.acuenta += montoT
						notapedido.bool_acuenta = False
						# Agregar comentario del ingreso
						notapedido.comentario = comentario
						notapedido.pagoEfectivo += pagoEfectivo
						notapedido.pagoVisa += pagoVisa
						notapedido.pagoBCP += pagoBCP
						notapedido.pagoBBVA += pagoBBVA
						notapedido.pagoYape += pagoYAPE
						notapedido.estado = "CANCELADO--"

						db.session.add(notapedido)
						# Creado el detalle
						detalle = Detalle_Caja(fecha_creacion,comentario, tipo, usuario_id,pagoEfectivo,pagoVisa,pagoBBVA,pagoBCP,pagoYAPE,notaID)
						db.session.add(detalle)
						db.session.commit()
						return jsonify({'message': 'Se ha cancelado la deuda de la nota de pedido', 'status': 'success'}, 200)
					except Exception as e:
						db.session.rollback()
						return jsonify({'message': 'Error al cancelar la deuda', 'status': 'error'}, 400)

				else:
					try:
						notapedido.deuda -= montoT
						notapedido.acuenta += montoT
						#Actualizando los montos de pago de la nota de pedido
						notapedido.pagoEfectivo += pagoEfectivo
						notapedido.pagoVisa += pagoVisa
						notapedido.pagoBCP += pagoBCP
						notapedido.pagoBBVA += pagoBBVA
						notapedido.pagoYape += pagoYAPE
						
						# Agregar comentario del ingreso
						notapedido.comentario = comentario
						db.session.add(notapedido)
						# Creado el detalle
						detalle = Detalle_Caja(fecha_creacion, comentario, tipo, usuario_id,pagoEfectivo,pagoVisa,pagoBBVA,pagoBCP,pagoYAPE,notaID)
						db.session.add(detalle)
						db.session.commit()
						return jsonify({'message': 'Se ha realizado un ingreso a la nota de pedido', 'status': 'success'}, 200)
					except Exception as e:
						db.session.rollback()
						return jsonify({'message': 'Error al realizar el ingreso', 'status': 'error'}, 400)

			# Si el tipo es EGRESO y tiene una deuda
			elif tipo == "EGRESO" and notapedido.bool_deuda:
				return jsonify({'message':'No se puede realizar un egreso por que la nota de pedido tiene una deuda pendiente','status':'error'},400)
			# Si el tipo es INGRESO y no tiene una deuda
			elif tipo == "INGRESO" and notapedido.bool_deuda == False:
				return jsonify({'message':'No se puede realizar un ingreso por que la nota de pedido no tiene una deuda pendiente','status':'error'},400)
			# Si el tipo es EGRESO y no tiene una deuda
			elif tipo == "EGRESO" and notapedido.bool_deuda == False:
				try:
					# Egreso significa que le estoy devolviendo dinero, entonces el total de la venta disminuye
					notapedido.total_venta -= montoT
					notapedido.acuenta -= montoT

					#Actualizando los montos de pago de la nota de pedido
					notapedido.pagoEfectivo -= pagoEfectivo
					notapedido.pagoVisa -= pagoVisa
					notapedido.pagoBCP -= pagoBCP
					notapedido.pagoBBVA -= pagoBBVA
					notapedido.pagoYape -= pagoYAPE
					# Agregar comentario del egreso
					notapedido.comentario = comentario
					db.session.add(notapedido)
					# Creado el detalle
					detalle = Detalle_Caja(fecha_creacion, comentario, tipo, usuario_id,pagoEfectivo,pagoVisa,pagoBBVA,pagoBCP,pagoYAPE,notaID)
					db.session.add(detalle)
					db.session.commit()
					return jsonify({'message': 'Se ha realizado un egreso a la nota de pedido', 'status': 'success'}, 200)
				except Exception as e:
					db.session.rollback()
					return jsonify({'message': 'Error al realizar el egreso', 'status': 'error'}, 400)
			else:
				return jsonify({'message':'No se pudo realizar el ingreso o egreso','status':'error'},400)
		else:
			# Si no existe la nota de pedido, creo un detalle de caja normal
			# Se espera notaDinero sea 0 , se espera que la notaID sea nulla
			try:
				detalle = Detalle_Caja(fecha_creacion,comentario,tipo,usuario_id,pagoEfectivo,pagoVisa,pagoBBVA,pagoBCP,pagoYAPE,notaID)
				db.session.add(detalle)
				db.session.commit()
				return jsonify({'message':'Se ha creado el detalle correctamente','status':'success'},200)
			except Exception as e:
				db.session.rollback()
				return jsonify({'message':'Error al crear el detalle','status':'error'},400)
	else:
		return jsonify({'message':'No se recibio ningun dato','status':'error'},400)


#Utilizando actualmente
@note.route('/imprimire/<string:id>',methods=['GET','POST'])
@login_required
def imprimire(id):
	nota=Nota_de_Pedido.query.get(id)
	notas= json.loads(nota.get_nombre_producto())
	if nota.notasdepedidos is None:
		telefono_comprador=nota.get_telefono_nota()
		dni_comprador=nota.get_dni_nota()
	else:
		telefono_comprador=nota.notasdepedidos.get_telefono()
		dni_comprador=nota.notasdepedidos.get_dni()

	return render_template('imprimirid.html',nota=nota,notas=notas,telefono=telefono_comprador,dni=dni_comprador,vendedor=nota.get_nombre_usuario())


#Utilizando actualmente
@note.route('/ver-ingresos-salidas',methods=['GET'])
@login_required
def ver_ingresos_salidas():

	# Obteniendo argumentos
	args=request.args

	# Inicializando variables
	fecha_inicio_actual = args.get('fecha_inicio', default=(datetime.today().date()).strftime('%Y/%m/%d'))
	fecha_final_actual = args.get('fecha_final', default=(datetime.today().date() + timedelta(days=1)).strftime('%Y/%m/%d'))

	json_filtrado_ingresos = Detalle_Caja.get_json_filtrado_por_tipo('INGRESO',fecha_inicio_actual,fecha_final_actual)
	json_filtrado_egresos = Detalle_Caja.get_json_filtrado_por_tipo('EGRESO',fecha_inicio_actual,fecha_final_actual)
	return render_template('ver_ingresos_salidas.html', ingresos=json_filtrado_ingresos, egresos=json_filtrado_egresos)

#Utilizando actualmente
@login_required
@note.route('/anular-ingreso-salida/<string:id>',methods=['PUT'])
def anular_ingreso_salida(id):
	#Obtener el detalle de caja
	detalle=Detalle_Caja.query.get(id)
	if detalle:
		detalle.anulado=True
		db.session.add(detalle)
		try:
			db.session.commit()
			return jsonify({'message':'Se anulo el detalle de caja','status':'success'},200)
		except:
			return jsonify({'message':'No se pudo anular el detalle de caja','status':'error'},400)
	else:
		return jsonify({'message':'No se pudo encontrar el detalle de caja','status':'error'},400)
