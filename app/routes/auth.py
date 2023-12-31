from flask import Blueprint,request,flash,render_template,redirect,url_for,session,current_app
from ..models.modelos import db,Usuario,Role
from ..forms.formularios import CrearCuenta,Login
from flask_login import login_user,logout_user,login_required
from datetime import timedelta
auth=Blueprint("auth",__name__)

@auth.before_request
def before_request():
    session.permanent=True
    session.modified=True
    current_app.permanent_session_lifetime=timedelta(hours=4)

@auth.route('/')
def index():
	return render_template('index.html',log=True)

@auth.route('/crear',methods=["GET","POST"])
def crear():
    form=CrearCuenta()
    if form.validate_on_submit():
        user=Usuario.query.filter_by(nombre_usuario=form.username.data).first()
        if user:
            mensaje="El usuario {} ya existe.".format(form.username.data)
            flash(mensaje,category='message')
        else:
            role_id=Role.query.filter_by(nombre_rol=form.rol.data).first()
            usuario=Usuario(form.username.data,form.password.data,role_id.get_id())
            db.session.add(usuario)
            db.session.commit()
            flash(f'Felicidades por registrarte {form.username.data}', category="message")
            return redirect(url_for("auth.login"))
    return render_template("crear_cuenta.html",form_usuario=form)

@auth.route('/login',methods=["GET","POST"])
def login():
    form=Login()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user=Usuario.query.filter_by(nombre_usuario=username).first()
        if user and user.verificar_contrasena(password):
            succes_message='Bienvenido {}'.format(form.username.data)
            flash(succes_message,category='message')
            login_user(user)


            return redirect(url_for("product.crear_producto"))
        else:
            error_message='Usuario o contraseña no validos!'
            flash(error_message,category='error')
    return render_template('login.html',form_login=form,log=True)

@auth.route('/logout',methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
