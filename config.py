class Dev_Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlementary.sqlite'
    SECRET_KEY = 'yeah not a secret'
    SQLALCHEMY_ECHO = False
    
class Prod_Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///sqlementary.sqlite'
    SECRET_KEY = 'yeah not a secret'
    SQLALCHEMY_ECHO = False