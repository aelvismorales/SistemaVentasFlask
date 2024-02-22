from functools import wraps
from flask import abort, flash
from flask_login import current_user
from .models.modelos import Permisos

def permiso_requerido(permiso,mensaje_error="No tienes permiso para acceder a esta página"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not current_user.can(permiso):
                #abort(403)
                flash(mensaje_error,category='error')
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def administrador_requerido(f):
    return permiso_requerido(Permisos.ADMINISTRADOR,"No tienes permiso para acceder a esta página")(f)