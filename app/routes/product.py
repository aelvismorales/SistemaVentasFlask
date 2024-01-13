from decimal import Decimal
from flask import Blueprint, jsonify,request,render_template,redirect,url_for,session,flash
from ..forms.formularios import CrearProducto,BuscarProducto,EditarProducto
from ..models.modelos import Producto
from datetime import datetime, timedelta, timezone
from app import db


product=Blueprint("product",__name__)

@product.route('/eliminarproducto/<id>',methods=['GET'])
def eliminarproducto(id):
    producto_eliminar=Producto.query.get(id)
    if producto_eliminar:
        nombre_elimninar=producto_eliminar.get_str_nombre()
        db.session.delete(producto_eliminar)
        db.session.commit()
        succes_message='Se elimino el producto "{}" satisfactoriamente'.format(nombre_elimninar)
        flash(succes_message,category='message')
        return jsonify({'message':'Se elimino el producto "{}" satisfactoriamente'.format(nombre_elimninar)})
    else:
        error_message='El producto no se pudo eliminar intente nuevamente'
        flash(error_message,category='error')
        return jsonify({'message':'El producto no se pudo eliminar intente nuevamente'})

@product.route('/buscar',methods=['GET','POST'])
def buscar_producto():
    buscar_producto=BuscarProducto()
    productForm=CrearProducto()
    # Post/Redirect/Get (PRG) pattern to the submit_buscar section of your code. This will prevent the form resubmission warning when refreshing the page after a search.
    if 'submit_crear' in request.form and productForm.validate_on_submit():
        product=Producto.query.filter_by(nombre_producto=productForm.nombre_producto.data).first()
        if product:
            error_message='El producto "{}" ya existe'.format(productForm.nombre_producto.data)
            flash(error_message,category='error')
        else:
            precio_venta=productForm.precio_venta_producto.data
            producto=Producto(productForm.nombre_producto.data.upper(),productForm.precio_costo_producto.data,precio_venta,productForm.stock.data)
            db.session.add(producto)
            db.session.commit()
            succes_message='Se creo el producto "{}"'.format(productForm.nombre_producto.data)
            flash(succes_message,category='message')
            return redirect(url_for('product.buscar_producto'))

    elif 'submit_buscar' in request.form and buscar_producto.validate_on_submit():
        productos=Producto.query.filter(Producto.nombre_producto.like('%'+buscar_producto.nombreproducto.data.upper()+'%')).all()
        if productos:
           # Store the search results in the session so they can be accessed after the redirect
           session['search_results'] = [product.get_json() for product in productos]
           return redirect(url_for('product.buscar_producto'))
        else:
            error_message='No se pudo encontrar ningun producto intente nuevamente'
            flash(error_message,category='error')
            return redirect(url_for('product.buscar_producto'))
    # Retrieve the search results from the session
    productos=[Producto.from_dict(product) for product in session.get('search_results', [])]
    
    return render_template('buscar_productos.html',buscar_form=buscar_producto,producto_form=productForm,productos=productos)

@product.route('/editar/<string:id>',methods=['GET','POST'])
def editar_id(id):
    producto=Producto.query.get(int(id))
    editar_producto=EditarProducto(request.form)

    if editar_producto.validate_on_submit(): 	
        producto.nombre_producto=editar_producto.nombre_producto.data
        producto.precio_costo_producto=editar_producto.precio_costo_producto.data
        producto.precio_venta_producto=editar_producto.precio_venta_producto.data
        producto.stock=editar_producto.stock.data
        producto.fecha_actualizacion_producto=datetime.now(timezone.utc)-timedelta(hours=5)
        db.session.add(producto)
        db.session.commit()
        succes_message='Se actualizo el producto {}'.format(producto.nombre_producto)
        flash(succes_message,category='message')
    return render_template('editar_producto_id.html',editar_form=editar_producto,product_name=producto.get_str_nombre(),product_pc=producto.get_str_pc(),product_pv=producto.get_str_pv(),product_stock=producto.get_stock())

