from flask import Blueprint,request,render_template,redirect,url_for,session,flash
from ..forms.formularios import CrearProducto,BuscarProducto,EditarProducto
from ..models.modelos import Producto
from datetime import datetime
from app import db


product=Blueprint("product",__name__)

@product.before_request
def beforerequest():
    global loge
    loge=False
    global produ 
    produ=False
    
    if 'username' in session:
        loge=True
    if 'producto' in session:
        produ=True

@product.route("/producto",methods=["GET","POST"])
def crear_producto():
    productForm=CrearProducto()
    print("llegue")
    if request.method=='POST' and productForm.validate():
        product=Producto.query.filter_by(nombre_producto=productForm.nombre_producto.data).first()
        if product is None:
            precio_venta=productForm.precio_venta_producto.data
            producto=Producto(productForm.nombre_producto.data,productForm.precio_costo_producto.data,precio_venta,productForm.stock.data)
            print("llegue2")
            db.session.add(producto)
            succes_message='Se creo el producto "{}"'.format(productForm.nombre_producto.data)
            flash(succes_message,category='message')
            return render_template('crear_producto.html',producto_form=productForm,log=loge)
    return render_template('crear_producto.html',producto_form=productForm,log=loge)

@product.route('/eliminarproducto/<string:id>',methods=['GET'])
def eliminarproducto(id):
    producto_eliminar=Producto.query.get(id)
    if producto_eliminar is not None:
        nombre_elimninar=producto_eliminar.get_str_nombre()
        db.session.delete(producto_eliminar)
        succes_message='Se elimino el producto "{}" satisfactoriamente'.format(nombre_elimninar)
        flash(succes_message,category='message')
        return redirect(url_for('product.buscar_producto'))
    else:
        error_message='El producto no se pudo eliminar intente nuevamente'
        flash(error_message,category='error')
    return redirect(url_for('product.buscar_producto'))

@product.route('/buscar',methods=['GET','POST'])
def buscar_producto():
    buscar_producto=BuscarProducto()
    if request.method=='POST' and buscar_producto.validate():
        productos=Producto.query.filter(Producto.nombre_producto.like('%'+buscar_producto.nombreproducto.data+'%')).all()
        if productos is not None:
           return render_template('buscar_productos.html',buscar_form=buscar_producto,productos=productos,log=loge)
        else:
            error_message='No se pudo encontrar el producto intente nuevamente'
            flash(error_message,category='error')
    return render_template('buscar_productos.html',buscar_form=buscar_producto,log=loge,prd=produ)

@product.route('/editar/<int:id>',methods=['GET','POST'])
def editar_id(id):
    producto=Producto.query.get(id)
    editar_producto=EditarProducto(request.form)

    if request.method=='POST' and editar_producto.validate(): 	
        producto.nombre_producto=editar_producto.nombre__producto.data
        producto.precio_costo_producto=editar_producto.precio_costo_producto.data
        producto.precio_venta_producto=editar_producto.precio_venta_producto.data
        producto.stock=editar_producto.stock.data
        producto.fecha_actualizacion_producto=datetime.now()
        db.session.add(producto)
        succes_message='Se actualizo el producto {}'.format(producto.nombre_producto)
        flash(succes_message,category='message')
    return render_template('editar_producto_id.html',editar_form=editar_producto,log=loge,product_name=producto.get_str_nombre(),product_pc=producto.get_str_pc(),product_pv=producto.get_str_pv(),product_stock=producto.get_stock())

#Funcion utilizada para poder agregar mas productos a una lista ( nota de pedido)
def array_merge( first_array , second_array ):
	if isinstance( first_array , list ) and isinstance( second_array , list ):
		return first_array + second_array
	elif isinstance( first_array , dict ) and isinstance( second_array , dict ):
		return dict( list( first_array.items() ) + list( second_array.items() ) )
	elif isinstance( first_array , set ) and isinstance( second_array , set ):
		return first_array.union( second_array )
	return False

#Agregar el producto a la nota de pedido
@product.route('/add',methods=['POST'])
def add():
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

					return redirect(url_for('product.buscar_producto'))
			else:
				session['producto']=DictProducts
				return redirect(url_for('product.buscar_producto'))
