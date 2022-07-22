from flask_sqlalchemy import SQLAlchemy
from os import environ

class Config(object):
    SECRET_KEY='123447a47f563e90fe2db0f56b1b17be62378e31b7cfd3adc776c59ca4c75e2fc512c15f69bb38307d11d5d17a41a7936789'

class DevelopmentConfig(Config):
    #DEBUG=environ.get('DEBUGGER')
    #DEBUG=True
    WTF_CSRF_CHECK_DEFAULT=False
    #SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin@localhost/sistemaventas'
    SQLALCHEMY_DATABASE_URI=environ.get('DATABASE_URL').replace('postgres','postgresql')
    SQLALCHEMY_TRACK_MODIFICATIONS=False