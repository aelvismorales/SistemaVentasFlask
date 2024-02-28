from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY=environ.get('SECRET_KEY') or '4kkAREdsre2/5'
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    TEMPLATE_FOLDER="./views/templates"
    STATIC_FOLDER="./views/static"
    SQLALCHEMY_TRACK_MODIFICATIONS=False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_DEVELOPMENT') or 'mysql+pymysql://root:admin@localhost/sistemaventas'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI= environ.get('DATABASE_TEST') or 'mysql+pymysql://root:admin@localhost/sistemaventas_test'

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY=environ.get('SECRET_KEY') or '4kkAREdsre25'
    SQLALCHEMY_DATABASE_URI=environ.get('DATABASE_PRODUCTION') or 'mysql+pymysql://root:admin@localhost/sistemaventas'
    #SQLALCHEMY_DATABASE_URI=environ.get('DATABASE_URL').replace('postgres','postgresql')

config = {
 'development': DevelopmentConfig,
 'testing': TestingConfig,
 'production': ProductionConfig,
 'default': DevelopmentConfig
}
