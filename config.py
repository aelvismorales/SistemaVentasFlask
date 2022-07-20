from flask_sqlalchemy import SQLAlchemy

class Config(object):
    SECRET_KEY='123447a47f563e90fe2db0f56b1b17be62378e31b7cfd3adc776c59ca4c75e2fc512c15f69bb38307d11d5d17a41a7936789'

class DevelopmentConfig(Config):
    DEBUG=True
    #WTF_CSRF_CHECK_DEFAULT=False
    #SQLALCHEMY_DATABASE_URI='postgresql://isnjonskuprehk:07d8bb3abcb665f2611cbf435a79c4dfeeac18604299189722d794802c1971fa@ec2-23-23-182-238.compute-1.amazonaws.com:5432/dbgnihpfcroaus'
    #SQLALCHEMY_DATABASE_URI='mysql+pymysql://root:admin@localhost/sistemaventas'
    SQLALCHEMY_DATABASE_URI='postgresql://qukwtjyqolccui:13de5742221cd4bb36d417bdb9f3191aa770141574fc759a06a55335f385673d@ec2-54-152-28-9.compute-1.amazonaws.com:5432/de53inatidu2qk'
    SQLALCHEMY_TRACK_MODIFICATIONS=False