from flask import Flask
from config import Config,config
from .models.modelos import db,Role,login_manager
from flask_wtf.csrf import CSRFProtect 
from flask_migrate import Migrate,upgrade,init,migrate
from .routes.database import database
from .routes.auth import auth
from .routes.buyer import buyer
from .routes.note import note
from .routes.product import product
import os
import logging
from logging.handlers import RotatingFileHandler

csrf=CSRFProtect()
migraciones=Migrate()

login_manager.login_view="auth.login"

def create_app(config_name):
    app=Flask(__name__,static_folder=Config.STATIC_FOLDER,template_folder=Config.TEMPLATE_FOLDER)
    app.config.from_object(config.get(config_name,"default")) 
    db.init_app(app)
    migraciones.init_app(app,db,directory="/var/www/html/SistemaVentasFlask/migrations")
    csrf.init_app(app)

    with app.app_context():
        db.create_all()
        Role.insertar_roles()
        if os.path.exists("/var/www/html/SistemaVentasFlask/migrations"):
            upgrade()
        else:
            init()
            migrate(message="Initial database migration")
    login_manager.init_app(app)

    #Agregando manejador de Logs
    log_dir = "/var/www/html/SistemaVentasFlask/logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "sistema.log")
    handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(handler)

    app.register_blueprint(database, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(buyer, url_prefix="/")
    app.register_blueprint(note, url_prefix="/")
    app.register_blueprint(product, url_prefix="/")
    return app
