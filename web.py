import os
import json

import sqlalchemy
from jinja2 import Template
from flask import Flask, request, redirect, session, render_template, url_for

from config import Dev_Config
from models import db, Database
from SQLementary import build_elm_schema, run, get_connection

app = Flask(__name__)
app.config.from_object(Dev_Config)

db.init_app(app)

@app.route("/")
def index():
    return render_template('index.htm')

@app.route('/sample<int:query_id>/schema', methods=['GET', 'POST'])
def get_schema(query_id):
    if query_id == 1:       
        db_type = 'sqlite'
        host = None
        port = None
        full_name = 'static/sample_databases/Chinook_Sqlite.sqlite'
        username = None
        password = None
    elif query_id == 2:
        db_type = 'oracle'
        host = 'localhost'
        port = '1521'
        full_name = 'xe'
        username = 'SYSTEM'
        password = 'password'
    elif query_id == 3:
        db_type = 'mysql'
        host = 'localhost'
        port = '3306'
        full_name = 'sakila'
        username = 'root'
        password = 'password'
    elif query_id == 4:
        db_type = 'postgres'
        host = 'localhost'
        port = '5432'
        full_name = 'pg_catalog'
        username = 'postgres'
        password = 'password'
    elif query_id == 5:
        db_type = 'mssql'
        host = 'localhost'
        port = '1433'
        full_name = 'master'
        username = 'sa'
        password = 'ASDqwe123'
    else:
        raise Exception("That sample isn't available")
        
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
    
    
@app.route('/sample<int:query_id>/query', methods=['GET', 'POST'])
def get_query_data(query_id):
    if query_id:        
        data = request.json
        #desiredcols = [col['table'] + '.' + col['column'] for col in data['desiredcolumns']]
        desiredcols = [[col['table'],col['column'],col['aggregate']] for col in data['desiredcolumns']]
        #filters = [[fil['table'] + '.' + fil['column'], fil['operator'], fil['value1'], fil['value2']] for fil in data['filters']]
        filters = [(fil['table'],fil['column'], fil['aggregate'], fil['operator'], fil['value1'], fil['value2']) for fil in data['filters']]           
        row_count = data['rowlimit']
        dist = data['distinct'] == True
        
        if query_id == 1:
            db_type = 'sqlite'
            host = None
            port = None
            full_name = 'static/sample_databases/Chinook_Sqlite.sqlite'
            username = None
            password = None
        elif query_id == 2:
            db_type = 'oracle'
            host = 'localhost'
            port = '1521'
            full_name = 'xe'
            username = 'SYSTEM'
            password = 'password'
        elif query_id == 3:
            db_type = 'mysql'
            host = 'localhost'
            port = '3306'
            full_name = 'sakila'
            username = 'root'
            password = 'password'
        elif query_id == 4:
            db_type = 'postgres'
            host = 'localhost'
            port = '5432'
            full_name = 'pg_catalog'
            username = 'postgres'
            password = 'password'        
        elif query_id == 5:
            db_type = 'mssql'
            host = 'localhost'
            port = '1433'
            full_name = 'master'
            username = 'sa'
            password = 'ASDqwe123'
        else:
            raise Exception("That sample isn't available")       
#run(db_type, loc, returned_columns, host = None, port = None, username = None, password = None,  constraints = None, row_limit = None, sql = False, distinct = True, commandline = False):        
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
                tuple_string.append(str(item))
            data[t] = tuple(tuple_string)
                    
        response = json.dumps({'sql': sql, 'data': data})
        return response
    else:
        return "You must have a sample query number"

if __name__ == "__main__":
    # Create test context to set up db
    ctx = app.test_request_context()
    ctx.push()

    # Create db tables
    db.create_all()

    # Create samples databases if they don't exist
    if not Database.query.filter_by(db_type='sqlite').first():
        db_type = 'sqlite'
        full_name = 'static/sample_databases/Chinook_Sqlite.sqlite'
        d = Database(db_type, full_name, alias = 'Chinook Sqlite')
        db.session.add(d)
        db.session.commit()
    if not Database.query.filter_by(db_type='oracle').first():
        db_type = 'oracle'
        host = 'localhost'
        port = '1521'
        full_name = 'xe'
        username = 'SYSTEM'
        password = 'password'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password)
        db.session.add(d)   
        db.session.commit() 
    if not Database.query.filter_by(db_type='mysql').first():
        db_type = 'mysql'
        host = 'localhost'
        port = '3306'
        full_name = 'sakila'
        username = 'root'
        password = 'password'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password)
        db.session.add(d)   
        db.session.commit()
    if not Database.query.filter_by(db_type='postgres').first():
        db_type = 'postgres'
        host = 'localhost'
        port = '5432'
        full_name = 'pg_catalog'
        username = 'postgres'
        password = 'password'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password)
        db.session.add(d)   
        db.session.commit() 
    if not Database.query.filter_by(db_type='mysql').first():
        db_type = 'mssql'
        host = 'localhost'
        port = '1433'
        full_name = 'master'
        username = 'sa'
        password = 'ASDqwe123'
        d = Database(db_type, full_name,host = host, port = port, username = username, password = password)
        db.session.add(d)   
        db.session.commit() 
        
    ctx.pop()    
    
    # Start server    
    app.debug = False    
    app.run()
    #port = int(os.environ.get("PORT", 80))
    #app.run('0.0.0.0', port)