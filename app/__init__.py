from flask import Flask
from config import Config,config,DevelopmentConfig
from .models.modelos import db,Role,login_manager
from flask_wtf.csrf import CSRFProtect 
from flask_migrate import Migrate,upgrade,init,migrate
from .routes.database import database
from .routes.auth import auth
from .routes.buyer import buyer
from .routes.note import note
from .routes.product import product
import os

csrf=CSRFProtect()
migraciones=Migrate()

login_manager.login_view="auth.login"

def create_app(config_name):
    print(Config.STATIC_FOLDER)
    print(Config.TEMPLATE_FOLDER)
    app=Flask(__name__,static_folder=Config.STATIC_FOLDER,template_folder=Config.TEMPLATE_FOLDER)
    app.config.from_object(config.get(config_name,"default")) 
    #app.config.from_object(DevelopmentConfig)
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

    app.register_blueprint(database, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(buyer, url_prefix="/")
    app.register_blueprint(note, url_prefix="/")
    app.register_blueprint(product, url_prefix="/")
    return app
