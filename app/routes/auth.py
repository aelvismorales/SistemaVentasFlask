from flask import Blueprint,request,flash,render_template,redirect,url_for,session
from ..models.modelos import db,Usuario
from ..forms.formularios import CrearCuenta,Login
auth=Blueprint("auth",__name__)

@auth.before_request
def beforerequest():
    global loge
    loge=False
    if 'username' in session:
        loge=True

@auth.route('/')
def index():
	return render_template('index.html',log=loge)

@auth.route('/crear',methods=["GET","POST"])
def crear():
    crear_usuario=CrearCuenta()
    if request.method=="POST" and crear_usuario.validate():
        user=Usuario.query.filter_by(nombre_usuario=crear_usuario.username.data).first()
        if user is not None:
            mensaje="El usuario {} ya existe.".format(crear_usuario.username.data)
            flash(mensaje,category='message')
        else:
            usuario=Usuario(crear_usuario.username.data,crear_usuario.password.data,crear_usuario.rol.data)
            db.session.add(usuario)
            db.session.commit()
            mensaje='Felicidades por registrarte {}'.format(crear_usuario.username.data)
            flash(mensaje,category="message")
            return redirect(url_for("auth.login"))
    return render_template("crear_cuenta.html",form_usuario=crear_usuario)

@auth.route('/login',methods=["GET","POST"])
def login():
    loginForm=Login()
    if request.method=="POST" and loginForm.validate():
        username=loginForm.username.data
        password=loginForm.password.data
        user=Usuario.query.filter_by(nombre_usuario=username).first()
        if user is not None and user.verificar_contrasena(password):
            succes_message='Bienvenido {}'.format(loginForm.username.data)
            flash(succes_message,category='message')
            session['username']=username
            session['id']=user.get_id()
            session['rol']=user.get_rol()

            return redirect(url_for("product.crear_producto"))
        else:
            error_message='Usuario o contraseña no validos!'
            flash(error_message,category='error')
    return render_template('login.html',form_login=loginForm,log=loge)

@auth.route('/logout',methods=["GET","POST"])
def logout():
    session.pop('username',None)
    session.pop('id',None)
    session.pop('role',None)
    return redirect(url_for("auth.login"))
