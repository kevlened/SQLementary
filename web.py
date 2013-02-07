   
from flask import Flask, request, redirect, session, render_template, url_for
from jinja2 import Template
import json
import os

from SQLementary import build_elm_schema, run

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.htm')

@app.route('/sample<int:query_id>/schema', methods=['GET', 'POST'])
def get_schema(query_id):
    if query_id == 1:
        relchinookloc = url_for('static', filename='sample_databases/Chinook_Sqlite.sqlite')[1:] # Remove the leading forward slash        
        db, schema = build_elm_schema('%s:///%s' % ('sqlite', relchinookloc))
        schema_dict = {tab.name:[col.name for col in tab.elm_columns] for tab in schema}
        return json.dumps(schema_dict)
    
@app.route('/sample<int:query_id>/query', methods=['GET', 'POST'])
def get_query_data(query_id):
    data = request.json
    desiredcols = [col['table'] + '.' + col['column'] for col in data['desiredcolumns']]
    filters = [[fil['table'] + '.' + fil['column'], fil['operator'], fil['value1'], fil['value2']] for fil in data['filters']]
    relchinookloc = '%s:///%s' % ('sqlite', url_for('static', filename='sample_databases/Chinook_Sqlite.sqlite')[1:])
    row_count = data['rowlimit']
    dist = data['distinct'] == True
    sql, data = run(relchinookloc,desiredcols,constraints=filters,row_limit=row_count,distinct=dist)
    response = json.dumps({'sql': sql, 'data': data})
    return response

if __name__ == "__main__":
    # Start server    
    app.debug = False    
    app.run()
    #port = int(os.environ.get("PORT", 80))
    #app.run('0.0.0.0', port)