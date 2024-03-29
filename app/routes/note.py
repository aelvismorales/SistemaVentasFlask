from flask import Blueprint,request,render_template,redirect,url_for,session,flash,jsonify
from ..models.modelos import Comprador,Nota_de_Pedido,Producto
from sqlalchemy import asc, desc
from datetime import datetime
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

@note.route('/crearnotapedido',methods=['GET','POST'])
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
				if session['acuenta']>0:
					nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,telefono_comprador,dni_comprador,deuda=total_venta-session['acuenta'],acuenta=session['acuenta'],comprador_id=existe_comprador)
					nota.comentario="Dejo a cuenta S/ {} soles. ".format(session["acuenta"])
					session.modified=True
					session['deuda']=total_venta-session['acuenta']
				else:
					nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,telefono_comprador,dni_comprador,comprador_id=existe_comprador)
					
				
				for key,product in session['producto'].items():
					producto=Producto.query.filter_by(nombre_producto=session['producto'][key]['name']).first()
					producto.stock-= session['producto'][key]['cantidad']	
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
					succes_message='Se creo la nota de pedido para {}'.format(nombre_comprador)
					flash(succes_message,category='message')
				else:
					error_message='No se pudo crear la nota de pedido, intentelo nuevamente'
					flash(error_message,category='error')
			else:
					datos_producto_json= json.dumps(session['producto'])
					comprador_nuevo=Comprador(nombre_comprador,telefono_comprador,direccion_comprador,dni_comprador)
					if session["acuenta"] > 0:
						nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,telefono_comprador,dni_comprador,deuda=total_venta-session['acuenta'],acuenta=session['acuenta'])
						nota.comentario="Dejo a cuenta S/ {} soles. ".format(session["acuenta"])
						session.modified=True
						session['deuda']=total_venta-session['acuenta']
					else:
						nota=Nota_de_Pedido(datos_producto_json,total_venta,nombre_comprador,direccion_comprador,estado_nota,telefono_comprador,dni_comprador)
						
					
					for key,product in session['producto'].items():
						producto=Producto.query.filter_by(nombre_producto=session['producto'][key]['name']).first()
						producto.stock-=session['producto'][key]['cantidad']

					if nota is not None:
						db.session.add(nota)
						db.session.commit()
						db.session.add(comprador_nuevo)
						db.session.commit()
						session.modified = True
						session['nombre_comprador']=nombre_comprador
						session['direccion_comprador']=direccion_comprador
						session['dni_comprador']=dni_comprador
						session['telefono_comprador']=telefono_comprador
						session['numero_nota']=nota.get_id()
						session['fecha_nota']=nota.get_fecha()
						session['estado_nota']=estado_nota
						succes_message='Se creo la nota de pedido para {} y se registro como nuevo comprador'.format(nombre_comprador)
						flash(succes_message,category='message')
	return redirect(url_for('product.buscar_producto'))

@note.route('/editarnotaventa/<string:id>',methods=['GET','POST'])
def editarnotaventa(id=None):
	nota=Nota_de_Pedido.query.get(id)
	session['id_nota']=id
	if nota is not None:
		session.modified=True
		session['nombre_comprador']=nota.get_nombre_comprador()
		session['direccion_comprador']=nota.get_direccion()
		session['dni_comprador']=nota.get_dni_nota()
		session['telefono_comprador']=nota.get_telefono_nota()
		session['producto']=json.loads(nota.get_nombre_producto())
		session['editar_activo']=True
		session['fecha_hoy']=nota.get_fecha_edit()

	return redirect(url_for('product.buscar_producto'))

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


@note.route('/vernotapedido',methods=['GET','POST'])
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
	# valVer=False
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	nota_pedido=[]
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
				return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,form_seleccion=seleccion,id_cambio=id_cambio,bool_fecha=fecha,bool_nombre=nombre,bool_order=order,bool_dni=dni_comprador,bool_imprimir=imprimir_resumen,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar,)
			else :
				error_message='No se pudo encontrar la nota de pedido intente nuevamente'
				flash(error_message,category='error')
		
	return render_template('ver_nota_pedido.html',log=loge,form_seleccion=seleccion,bool_fecha=fecha,bool_nombre=nombre,id_cambio=id_cambio,bool_order=order,bool_estado=estado_nota,bool_dni=dni_comprador,bool_resumen=resumen_Ventas,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)

@note.route('/vernotaporestado',methods=['GET','POST'])
def vernotaporestado():
	opcion=request.form.get('opcionestado')
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if request.method=='POST' and opcion:
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.estado==opcion).order_by(asc(Nota_de_Pedido.id)).all()
		return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
	return redirect(url_for('note.vernotaporestado'))

@note.route('/vernotaporfecha',methods=['GET','POST'])
def vernotaporfecha():

	fecha_inicio=request.form['fecha_inicio']
	fecha_final=request.form['fecha_final']
	total_dia=0
	total_dia_visa=0
	total_dia_bcp=0
	total_dia_bbva=0
	total_dia_yape=0
	total_dia_por_cancelar=0
	if fecha_inicio and fecha_final and request.method=='POST':
		
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.fecha_creacion.between(fecha_inicio,fecha_final)).order_by(asc(Nota_de_Pedido.id)).all()
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

			return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar,tdbcp=total_dia_bcp,tdbbva=total_dia_bbva,tdy=total_dia_yape,fechita=fecha_inicio,fechita_final=fecha_final,bool_imprimir=True)
		else :
			error_message='No se pudo encontrar la nota de pedido intente nuevamente'
			flash(error_message,category='error')

	return redirect(url_for('note.vernotapedido'))
	 
@note.route('/vernotapornombre',methods=['GET','POST'])
def vernotapornombre():
	nombrecomprador=request.form.get('nombre_comprador')
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if nombrecomprador and request.method=='POST':
		nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+nombrecomprador+'%')).order_by(asc(Nota_de_Pedido.id)).all()
		if nota_pedido is not None:
			return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
		else :
			error_message='No se pudo encontrar la nota de pedido intente nuevamente'
			flash(error_message,category='error')

	return redirect(url_for('note.vernotapedido'))

@note.route('/vernotaporDNI',methods=['GET','POST'])
def vernotaporDNI():
	dni_comprador=request.form.get('dni_comprador')
	total_dia=0
	total_dia_visa=0
	total_dia_por_cancelar=0
	if dni_comprador and request.method=='POST':
		comprador=Comprador.query.filter_by(dni=dni_comprador).first()
		if comprador is not None:
			nota_pedido=Nota_de_Pedido.query.filter(Nota_de_Pedido.nombre_comprador.like('%'+comprador.get_nombre()+'%')).order_by(asc(Nota_de_Pedido.id)).all()
			if nota_pedido is not None:
				return render_template('ver_nota_pedido.html',log=loge,nota_pedido=nota_pedido,td=total_dia,tdv=total_dia_visa,tdpc=total_dia_por_cancelar)
			else :
				error_message='No se pudo encontrar la nota de pedido intente nuevamente'
				flash(error_message,category='error')
	return redirect(url_for('note.vernotapedido'))

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


#Actualizar Cantidad de Productos en la nota de pedido
@note.route('/updateproduct',methods=['POST'])
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
		return redirect(url_for('product.buscar_producto'))
	return redirect(url_for('product.buscar_producto'))

#Actualizar precio de un producto en la nota de pedido
@note.route('/updateprice',methods=['POST'])
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
		return redirect(url_for('product.buscar_producto'))
	return redirect(url_for('product.buscar_producto'))

@note.route('/updatedebt',methods=['POST'])
def updatedebt():
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

#Limpiar todo la lista de productos de 	Nota de pedido
@note.route('/empty')
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
		session.pop('editar_activo',None)
		session.pop('id_nota',None)
		session.pop('fecha_hoy',None)
		session.pop('acuenta',None)
		session.pop('deuda',None)
		
		success_message='Se vacio la nota de pedido'
		flash(success_message,category='message')
		return redirect(url_for('product.buscar_producto'))
	except Exception as e:
		print(e)

@note.route('/imprimir')
def imprimir():
	return render_template('imprimir.html',acuenta=session['acuenta'],deuda=session['deuda'])

@note.route('/imprimire/<string:id>',methods=['GET','POST'])
def imprimire(id):
	nota=Nota_de_Pedido.query.get(id)
	notas=json.loads(nota.get_nombre_producto())
	if nota.notasdepedidos is None:
		telefono_comprador=nota.get_telefono_nota()
		dni_comprador=nota.get_dni_nota()
	else:
		telefono_comprador=nota.notasdepedidos.get_telefono()
		dni_comprador=nota.notasdepedidos.get_dni()

	return render_template('imprimirid.html',nota=nota,notas=notas,telefono=telefono_comprador,dni=dni_comprador)
