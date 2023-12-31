from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY="#1523ABC"
    SQLALCHEMY_COMMIT_ON_TEARDOWN=True
    TEMPLATE_FOLDER="./views/templates/"
    STATIC_FOLDER="./views/static/"
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    # WTF_CSRF_CHECK_DEFAULT=False

    # @staticmethod
    # def init_app(app):
    #     pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin@localhost/sistemaventas'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin@localhost/sistemaventas'

class ProductionConfig(Config):
    SECRET_KEY=environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI=environ.get('DATABASE_URL').replace('postgres','postgresql')

config = {
 'development': DevelopmentConfig,
 'testing': TestingConfig,
 'production': ProductionConfig,
 'default': DevelopmentConfig
}