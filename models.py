from datetime import datetime
#from bcrypt import gensalt, hashpw
#from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import synonym
from werkzeug.security import generate_password_hash

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

# Create user model. For simplicity, it will store passwords in plain text.
# Obviously that's not right thing to do in real world application.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    # password = db.Column(db.String(64))
    _password = db.Column('password', db.String(64))

    def get_attr(self):
        return self._password

    def set_attr(self, value):
         self._password = generate_password_hash(value) if value is not None else generate_password_hash('')

    @declared_attr
    def password(cls):
        return synonym('_password', descriptor=property(cls.get_attr, cls.set_attr))
    
    # Will be used to determine who has privileges to change db and users 
    admin = db.Column(db.Boolean, default=False, unique=False, nullable=False)
    
    def __init__(self, login=None, email=None, password=None, admin=False):
        self.login = login
        self.email = email
        self.password = password
        self.admin = admin

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username