from datetime import datetime
#from bcrypt import gensalt, hashpw
#from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import URL

db = SQLAlchemy()

class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    db_type = db.Column(db.String(128), unique=False, nullable=False)
    host = db.Column(db.String(128), unique=False, nullable=True)
    port = db.Column(db.Integer, unique=False, nullable=True)
    full_name = db.Column(db.String(128), unique=False, nullable=False)
    username = db.Column(db.String(128), unique=False, nullable=True)
    password = db.Column(db.String(60), unique=False, nullable=True)
    alias = db.Column(db.String(128), unique=False, nullable=True)

    def __init__(self, db_type, full_name, username=None, password=None, host=None, port=None, alias=None):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.full_name = full_name
        self.username = username
        self.password = password
        self.alias = alias

    def __repr__(self):
        connection_string = str(URL(self.db_type, username = self.username, password = self.password, database = self.full_name))
        a = self.alias if self.alias else self.full_name
        
        return '<Database %s: %s>' % (a, self.id)
