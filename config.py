from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY=environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    TEMPLATE_FOLDER="/var/www/html/SistemaVentasFlask/app/views/templates"
    STATIC_FOLDER="/var/www/html/SistemaVentasFlask/app/views/static"
    SQLALCHEMY_TRACK_MODIFICATIONS=False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_DEVELOPMENT') or 'mysql+pymysql://root:admin@localhost/sistemaventas'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI= environ.get('DATABASE_TEST') or 'mysql+pymysql://root:admin@localhost/sistemaventas'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY=environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI=environ.get('DATABASE_PRODUCTION') or 'mysql+pymysql://root:admin@localhost/sistemaventas'
    #SQLALCHEMY_DATABASE_URI=environ.get('DATABASE_URL').replace('postgres','postgresql')

config = {
 'development': DevelopmentConfig,
 'testing': TestingConfig,
 'production': ProductionConfig,
 'default': DevelopmentConfig
}
