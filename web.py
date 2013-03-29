import os
import json

from flask.ext.sqlalchemy import SQLAlchemy
from jinja2 import Template
from flask import Flask, request, redirect, render_template, url_for
from flask.ext import admin, login, wtf
from flask.ext.admin.contrib import sqlamodel
from werkzeug.security import generate_password_hash, check_password_hash

from config import Dev_Config
from models import db, Database, User
from SQLementary import build_elm_schema, run, get_connection
from elm_objects import elm_constraint

app = Flask(__name__)
app.config.from_object(Dev_Config)

db.init_app(app)

@app.route("/")
def index():
    return render_template('index.htm', user=login.current_user)

@app.route("/databases")
def get_databases():
    databases = Database.query.all()
    
    db_list = {}
    
    for database in databases:
        a = database.alias if database.alias else database.full_name
        db_list[database.id] = a
    response = json.dumps(db_list)
    return response

@app.route('/<int:query_id>/schema', methods=['GET', 'POST'])
def get_schema(query_id):
    database = Database.query.filter_by(id=query_id).first()
    db_type = database.db_type
    full_name = database.full_name
    host = database.host
    port = database.port
    username = database.username
    password = database.password
    
    db = get_connection(db_type, full_name, host = host, port = port, username = username, password = password)
    
    schema = build_elm_schema(db)
    schema_dict = {}
    for tab in schema:
        try:
            col_dict = {}
            for col in tab.elm_columns:
                col_dict[col.name] = str(col.type)
            schema_dict[tab.name] = col_dict
        except:
            print tab.name + " wasn't loaded"
        
    #schema_dict = {tab.name:{col.name:str(col.type) for col in tab.elm_columns} for tab in schema}
    schema_json = json.dumps(schema_dict)
    return schema_json
    
    
@app.route('/<int:query_id>/query', methods=['GET', 'POST'])
def get_query_data(query_id):
    if query_id:
        data = request.json
        desiredcols = [[col['table'],col['column'],col['aggregate']] for col in data['desiredcolumns']]
        #filters = [(fil['table'],fil['column'], fil['aggregate'], fil['operator'], fil['value1'], fil['value2']) for fil in data['filters']]  
        
        filters = []
        
        # Build filters, could be hierarchical
        for fil in data['filters']:
            t = fil['table']
            c = fil['column']
            agg = fil['aggregate']
            op = fil['operator']
            v1 = fil['value1']
            v2 = fil['value2']
            bt = fil['boolType']
            fs = fil['filters']
            if bt == "":              
                filters.append(elm_constraint(t,c,op,v1,v2,agg,bt,fs))
            else:
                fils = []
                for f in fs:
                    _t = f['table']
                    _c = f['column']
                    _agg = f['aggregate']
                    _op = f['operator']
                    _v1 = f['value1']
                    _v2 = f['value2']
                    _bt = fil['boolType']
                    _fs = f['filters']
                    fils.append(elm_constraint(_t,_c,_op,_v1,_v2,_agg,_bt,_fs))
                filters.append(elm_constraint(t,c,op,v1,v2,agg,bt,fils))
                 
        row_count = data['rowlimit']
        dist = data['distinct'] == True
        
        database = Database.query.filter_by(id=query_id).first()
        db_type = database.db_type
        full_name = database.full_name
        host = database.host
        port = database.port
        username = database.username
        password = database.password
                
        sql, data = run(db_type, full_name, desiredcols,
                        host = host, port = port,
                        username = username, password = password,
                        constraints=filters,
                        row_limit=row_count,
                        distinct=dist)
        
        '''Guarantee all data is in string format'''
        for t in range(len(data)):
            tpl = data[t]
            tuple_string = []
            for item in tpl:
                '''Convert all the strings to utf-8''' 
                tuple_string.append(str(item).encode('utf-8'))
            data[t] = tuple(tuple_string)
                                  
        response = json.dumps({'sql': sql, 'data': data})
        return response
    else:
        return "You must have a query id"

# Define login and registration forms (for flask-login)
class LoginForm(wtf.Form):
    login = wtf.TextField(validators=[wtf.required()])
    password = wtf.PasswordField(validators=[wtf.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise wtf.ValidationError('Invalid user')

        if not check_password_hash(user.password, self.password.data):
            raise wtf.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


#class RegistrationForm(wtf.Form):
#    login = wtf.TextField(validators=[wtf.required()])
#    email = wtf.TextField()
#    password = wtf.PasswordField(validators=[wtf.required()])
#
#    def validate_login(self, field):
#        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
#            raise wtf.ValidationError('Duplicate username')

# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.setup_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)

# Create customized model view class
class MyModelView(sqlamodel.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


# Create customized index view class
class MyAdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = form.get_user()
        login.login_user(user)
        return redirect(url_for('admin.index'))

    return render_template('form.html', form=form)

@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect(url_for('index'))
###############################################################################
#########################End Authorization Test################################
###############################################################################

if __name__ == "__main__":
    # Create test context to set up db
    ctx = app.test_request_context()
    ctx.push()
    
    # Initialize flask-login
    init_login()

    # Create flask-admin
    admin = admin.Admin(app, 'SQLementary', index_view=MyAdminIndexView())

    # Add view
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Database, db.session))
    
    # End Authorization

    # Create db tables
    db.create_all()
    
    # Create default admin if it doesn't exist
    if not User.query.filter_by(login='admin').first():        
        u = User(login='admin',password="default",admin=True)
        db.session.add(u)
        db.session.commit()

    # Create samples databases if they don't exist
    if not Database.query.filter_by(db_type='sqlite').first():
        db_type = 'sqlite'
        full_name = 'static/sample_databases/Chinook_Sqlite.sqlite'
        alias = 'Chinook - Sqlite'
        d = Database(db_type, full_name, alias = alias)
        db.session.add(d)
        db.session.commit()
    if not Database.query.filter_by(db_type='oracle').first():
        db_type = 'oracle'
        host = 'localhost'
        port = '1521'
        full_name = 'xe'
        username = 'SYSTEM'
        password = 'password'
        alias = 'xe - Oracle'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password, alias = alias)
        db.session.add(d)   
        db.session.commit() 
    if not Database.query.filter_by(db_type='mysql').first():
        db_type = 'mysql'
        host = 'localhost'
        port = '3306'
        full_name = 'sakila'
        username = 'root'
        password = 'password'
        alias = 'Sakila  - MySql'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password, alias = alias)
        db.session.add(d)   
        db.session.commit()
    if not Database.query.filter_by(db_type='postgres').first():
        db_type = 'postgres'
        host = 'localhost'
        port = '5432'
        full_name = 'pg_catalog'
        username = 'postgres'
        password = 'password'
        alias = 'pg_catalog  - Postgres'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password, alias = alias)
        db.session.add(d)   
        db.session.commit() 
    if not Database.query.filter_by(db_type='mssql').first():
        db_type = 'mssql'
        host = 'localhost'
        port = '1433'
        full_name = 'master'
        username = 'sa'
        password = 'ASDqwe123'
        alias = 'master  - MS SQL Server'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password, alias = alias)
        db.session.add(d)   
        db.session.commit() 
        
    ctx.pop()    
    
    # Start server    
    app.debug = False    
    app.run()
    #port = int(os.environ.get("PORT", 80))
    #app.run('0.0.0.0', port)