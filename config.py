from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY="#1523ABC"
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    TEMPLATE_FOLDER="/var/www/html/SistemaVentasFlask/app/views/templates"
    STATIC_FOLDER="/var/www/html/SistemaVentasFlask/app/views/static"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    # WTF_CSRF_CHECK_DEFAULT=False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin@localhost/sistemaventas'
    #SQLALCHEMY_DATABASE_URI='mysql+pymysql://remote:admin@192.168.100.17:3307/sistemaventas'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin@localhost/sistemaventas'

class ProductionConfig(Config):
    SECRET_KEY=environ.get('SECRET_KEY')
    #SQLALCHEMY_DATABASE_URI=environ.get('DATABASE_URL').replace('postgres','postgresql')

config = {
 'development': DevelopmentConfig,
 'testing': TestingConfig,
 'production': ProductionConfig,
 'default': DevelopmentConfig
}
