from flask import Flask
from config import Config,config
from .models.modelos import db,Role,login_manager
from flask_wtf.csrf import CSRFProtect 
from flask_migrate import Migrate


csrf=CSRFProtect()
migrate=Migrate()


def create_app(config_name):
    app=Flask(__name__,static_folder=Config.STATIC_FOLDER,template_folder=Config.TEMPLATE_FOLDER)
    app.config.from_object(config[config_name]) 
    db.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        db.create_all()
        Role.insertar_roles()
    migrate.init_app(app,db)
    login_manager.init_app(app)
    from .routes.database import database
    from .routes.auth import auth
    from .routes.buyer import buyer
    from .routes.note import note
    from .routes.product import product
    app.register_blueprint(database, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(buyer, url_prefix="/")
    app.register_blueprint(note, url_prefix="/")
    app.register_blueprint(product, url_prefix="/")
    return app
