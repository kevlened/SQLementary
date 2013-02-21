from datetime import datetime
#from bcrypt import gensalt, hashpw
#from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.engine.url import URL

db = SQLAlchemy()

#class User(db.Model, UserMixin):
#    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String(128), unique=True, nullable=False)
#    display_name = db.Column(db.String(32), unique=True, nullable=False)
#    created = db.Column(db.DateTime, unique=False, nullable=False)
#    deleted = db.Column(db.DateTime, unique=False, nullable=True)
#    salt = db.Column(db.String(32), unique=False, nullable=False)
#    password = db.Column(db.String(60), unique=False, nullable=False)
#    admin = db.Column(db.Boolean, default=False, unique=False, nullable=False)
#
#    def __init__(self, email, display_name, password, admin=False):
#        self.email = email
#        self.display_name = display_name
#        self.admin = admin
#        self.created = datetime.now()
#
#        salt = gensalt(10)
#        self.salt = salt
#        self.password = hashpw(password, salt)
#
#    def __repr__(self):
#        return '<User %r>' % (self.email)


class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    db_type = db.Column(db.String(128), unique=False, nullable=False)
    host = db.Column(db.String(128), unique=False, nullable=True)
    port = db.Column(db.Integer, unique=False, nullable=True)
    full_name = db.Column(db.String(128), unique=False, nullable=False)
    username = db.Column(db.String(128), unique=False, nullable=True)
    password = db.Column(db.String(60), unique=False, nullable=True)
    alias = db.Column(db.String(128), unique=False, nullable=True)

#    default = db.Column(db.Boolean, default=False, unique=False,
#                        nullable=False)
#    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#    user = db.relationship('User', backref=db.backref('resumes',
#                           lazy='dynamic'))

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
        #return connection_string + " as " + self.alias
        #return '<Resume %s: %s>' % (self.user.email, self.title)
