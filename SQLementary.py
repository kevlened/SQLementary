#-------------------------------------------------------------------------------
# Name:        SQLementary
# Purpose:     Return data or automatically generate SQL from an arbitrary
#              database using database access info, requested columns and  
#              constraints.
#
# Author:      Kevin (Len) Boyette
# Created:     01/22/2013
# Copyright:   (c) Len 2013
# License:     LGPL (http://www.gnu.org/licenses/lgpl-3.0.txt)
#-------------------------------------------------------------------------------


from elm_objects import elm_column, elm_constraint, elm_table
import sqlsoup
#from sqlalchemy import MetaData
from sqlalchemy.sql import column, table, select, join, compiler, between
#from sqlalchemy.orm import sessionmaker
import logging
from itertools import permutations
import sqlparse
import sys
from optparse import OptionParser
import operator
from sqlalchemy.engine.url import URL
import re

from sqlalchemy import func
from sqlalchemy.exc import AmbiguousForeignKeysError

logging.basicConfig(level=logging.CRITICAL)
#logging.basicConfig(filename='db.log', level=logging.CRITICAL)
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def build_elm_schema(db):
    elm_tables = []
    
    logging.info('Pulling table and column Metadata from database')
    if not len(db._metadata.tables):
        db._metadata.reflect()
    sqa_tables = db._metadata.tables.values()
    
    logging.info('Loading all tables and columns objects using Metadata')
    for sqa_table in sqa_tables:
        elm_tables.append(elm_table(sqa_table))
    
    return elm_tables

def get_connection(db_type, full_name, host = None, port = None, username = None, password = None):
    '''Allows us to define our own default database drivers'''
    if db_type == "sqlite":
        cnx = URL("sqlite", username = username, password = password, database = full_name)
        db = sqlsoup.SQLSoup(str(cnx))
    elif db_type == "oracle":
        cnx = URL("oracle+cx_oracle", username = username, password = password, database = full_name, host = host, port = port)
        db = sqlsoup.SQLSoup(str(cnx))
    elif db_type == "mysql":
        cnx = URL("mysql+mysqldb", username = username, password = password, database = full_name, host = host, port = port)
        db = sqlsoup.SQLSoup(str(cnx))
    elif db_type == "postgres":
        cnx = URL("postgres", username = username, password = password, database = full_name, host = host, port = port)
        db = sqlsoup.SQLSoup(str(cnx))
    elif db_type == "mssql":
        cnx = URL("mssql+pyodbc", username = username, password = password, database = full_name, host = host, port = port)
        db = sqlsoup.SQLSoup(str(cnx))
    else:
        raise Exception(db_type + " isn't a supported database type")
    return db

def run(db_type, loc, returned_columns, host = None, port = None, username = None, password = None,  constraints = None, row_limit = None, sql = False, distinct = True, commandline = False):
    
    db = get_connection(db_type, loc, host = host, port = port, username = username, password = password)
    elm_tables = build_elm_schema(db)
    elm_constraints = []
    
    logging.info('Pulling table and column Metadata from database')
    if not len(db._metadata.tables):
        db._metadata.reflect()
    sqa_tables = db._metadata.tables.values()
    
    logging.info('Loading all tables and columns objects using Metadata')
    for sqa_table in sqa_tables:
        elm_tables.append(elm_table(sqa_table))
    
    logging.info('Building a list of constraint objects from constraint list argument')
    if constraints:
        for c in constraints:
            table = c[0]
            column = c[1]
            aggregate = c[2]
            operator = c[3]
            value1 = c[4]            
            
            #Sanitize val2
            value2 = c[5] if len(c) == 6 else None
            value2 = None if value2 == '' else value2
            
            elm_constraints.append(elm_constraint(table, column, operator, value1, value2, aggregate))
    
    logging.info('Building a list of necessary tables')
    ret_cols = []
    for tab_col in returned_columns:
        table = tab_col[0]
        column = tab_col[1]
        ret_cols.append([table, column])
        
    tabs_temp = set([table_column[0] for table_column in ret_cols])    
    con_tabs_temp = set([con.table_name for con in elm_constraints])    
    tabs_temp = tabs_temp.union(con_tabs_temp)
    
    #Add the tables from the constraints to the validation
    col_tab_all = ret_cols[:]
    if len(elm_constraints) > 0:
        for con in elm_constraints:
            col_tab_all.append([con.table_name, con.column_name])
    
    #Validate the tables actually exist
    all_tables = set([t.name for t in sqa_tables])
    for tc in col_tab_all:
        ta  = str(tc[0])
        co = str(tc[1])
        if ta not in all_tables:
            raise Exception('Table ' + ta + ' doesn\'t exist in the current database')
        else:
            found = False
            for t in [t for t in sqa_tables if t.name == ta]:
                for tcn in [c.name for c in t._columns._all_cols]:
                    if tcn == co:
                        found = True
            if not found:
                raise Exception('Column ' + '%s.%s' % (ta,co) + ' doesn\'t exist in the current database') 
    
    #Find the optimal JOIN path
    joins = join_sequence(list(sqa_tables), list(tabs_temp))    
    
    #Remove JOIN redundancy http://stackoverflow.com/a/480227   
    seen = set()
    seen_add = seen.add
    new_joins =  [ x for x in joins if x not in seen and not seen_add(x)]
    joins = new_joins
    
    #Make it easy to find table data via a dictionary
    table_dict = {tab.name:tab.data for tab in elm_tables}
    
    #Instantiate the query -Needs to be the session.Query, not a simple select so we can add filters
    query = db.session.query()  
    
    def get_column(sqa_table,column_name):
        for ec in sqa_table._columns._all_cols:
            if ec.name == column_name:
                return ec
            
    #Build the joins
    #    -Needs to be performed before adding columns to prevent session.Query
    #    from generating excess joins
    query = query.select_from(table_dict[joins[0]])
    sqa_joins = table_dict[joins[0]]
    for i in range(1,len(joins)):
        second_table = table_dict[joins[i]]
        try:
            sqa_joins = sqa_joins.join(second_table)
            query = query.join(second_table)
        except AmbiguousForeignKeysError:
            #TODO: Assign a priority for primary keys from the order columns are requested
                                  
            first_column = None
            second_column = None
            
            first_table = table_dict[joins[i-1]]
            
            #Look through foreign keys of the second table
            for fk in second_table.foreign_keys:
                
                #If the key is both a primary key and from the first table
                if fk.column.primary_key and fk.column.table == first_table:
                    
                    #Assign the key found to the first table column
                    first_column = fk.column
                    
                    #Assign the associated foreign key in the second table to the second table column
                    second_column = fk.parent
                    
            sqa_joins = sqa_joins.join(second_table, first_column == second_column)
            query = query.join(second_table, first_column == second_column)
            
    #Build the columns to select
    sqa_select_cols = []
            
    #Find columns that don't have an aggregate
    #Find columns that do have an aggregate
    #Create list of columns to select
    #    -(must be done together to preserve order)
    sqa_non_aggregate = []
    sqa_aggregate = []
    for tc in returned_columns:
        t = tc[0]
        c = tc[1]
        a = tc[2]
        ec = get_column(table_dict[t],c)
        if a == '':
            sqa_non_aggregate.append(ec)
            sqa_select_cols.append(ec)
        else:
            sqa_aggregate.append((a,ec))
            aggregate = a
            column = ec
            if aggregate == 'COUNT':
                sqa_select_cols.append(func.count(column))
            elif aggregate == 'SUM':
                sqa_select_cols.append(func.sum(column))
            elif aggregate == 'AVG':
                sqa_select_cols.append(func.avg(column))
            elif aggregate == 'MIN':
                sqa_select_cols.append(func.min(column))
            elif aggregate == 'MAX':
                sqa_select_cols.append(func.max(column))
    
    query = query.add_columns(*sqa_select_cols)
    
    if len(sqa_aggregate) > 0:
        for na in sqa_non_aggregate:
            query = query.group_by(na)        
    
    #Add the constraints
    for ec in elm_constraints:
        if ec.operator == "=":
            query = query.filter(get_column(table_dict[ec.table_name],ec.column_name) == ec.val1)
        elif ec.operator == ">":
            query = query.filter(get_column(table_dict[ec.table_name],ec.column_name) > ec.val1)
        elif ec.operator == ">=":
            query = query.filter(get_column(table_dict[ec.table_name],ec.column_name) >= ec.val1)   
        elif ec.operator == "<":
            query = query.filter(get_column(table_dict[ec.table_name],ec.column_name) < ec.val1)   
        elif ec.operator == "<=":
            query = query.filter(get_column(table_dict[ec.table_name],ec.column_name) <= ec.val1)   
        elif ec.operator == "!=" or ec.operator == "<>":
            query = query.filter(get_column(table_dict[ec.table_name],ec.column_name) != ec.val1)
        elif ec.operator == "between" or ec.operator == "btw":
            query = query.filter(between(get_column(table_dict[ec.table_name],ec.column_name), ec.val1, ec.val2))
        
    #Make rows distinct
    if distinct:
        query = query.distinct()
    
    #Limit the number of returned rows
    if row_limit:
        query = query.limit(row_limit)
    
    #Execute the full statement                
    #db.engine._echo = True
    
    #TODO: fix the dialect hack
    dialect = select([get_column(table_dict[returned_columns[0][0]],returned_columns[0][1])]).bind.dialect
                             
    if commandline:
        if sql:
            sql = compile_query_sqlite(query,dialect)
            sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            logging.info('Returned query ' + sql)
            print sql
        else:
            res = query.all()
            for row in res:
                logging.info('Data row ' + str(row))
                print str(row)
    else:
        if db_type == "sqlite":
            sql = compile_query_sqlite(query,dialect)            
        elif db_type == "oracle":
            sql = compile_query_oracle(query,dialect)
        elif db_type == "mysql":
            sql = compile_query_mysql(query,dialect)
        else:
            sql = "Unable to generate sql for " + db_type
            
        sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
        logging.info('Returned query ' + sql)
        res = query.all()
        return sql, res

def compile_query_oracle(query, dialect):
    '''
    http://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
    As it turns out, I need to modify the compiler to be specific to SQLite or whatever db I want
    http://stackoverflow.com/questions/6350411/how-to-retrieve-executed-sql-code-from-sqlalchemy
    '''   
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    statement = str(statement).replace('\n', '')
    params = {}
    for k,v in comp.params.iteritems():
        if re.match('param_\d*', k):
            k = k.replace('param', 'ROWNUM')
        statement = re.sub(':' + str(k), str(v), statement)
    return statement

def compile_query_mysql(query, dialect):
    from sqlalchemy.sql import compiler
    from MySQLdb.converters import conversions, escape

    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    enc = dialect.encoding
    params = []
    for k in comp.positiontup:
        v = comp.params[k]
        if isinstance(v, unicode):
            v = v.encode(enc)
        params.append( escape(v, conversions) )
    return (comp.string.encode(enc) % tuple(params)).decode(enc)

def compile_query_sqlite(query, dialect):
    '''
    http://stackoverflow.com/questions/4617291/how-do-i-get-a-raw-compiled-sql-query-from-a-sqlalchemy-expression
    As it turns out, I need to modify the compiler to be specific to SQLite or whatever db I want
    '''   
    statement = query.statement
    comp = compiler.SQLCompiler(dialect, statement)
    comp.compile()
    enc = dialect.encoding
    params = {}
    for k,v in comp.params.iteritems():
        if isinstance(v, unicode):
            v = v.encode(enc)
        #split the key into field and count
        fc = k.rsplit('_',1)
        f = fc[0]
        c = fc[1]
        if not f in params:
            params[f] = []
        params[f].append((c,v)) #add a tuple
        
    #replace each dictionary with a sorted list to use as a queue
    for k,v in params.iteritems():
        params[k] = sorted(params[k], key=lambda k: k[0]) #sort by first val in tuple
        
    #loop through the encoded sql statement and replace the placeholders with values sequentially
    encoded = comp.string.encode(enc)
    sequence = []
    index = 0
    while index < len(encoded):
        index = encoded.find( '?', index)
        if index == -1:
            break
        
        param_dist = {}
        for k,v in params.iteritems():
            found_at = encoded.rfind(k,0,index)
            param_dist[k] = index - found_at
        best = sorted(param_dist.iteritems(), key=operator.itemgetter(1))[0][0]
        sequence.append(params[best].pop(0)[1])
        #Remove empty params
        for k in params.keys():
            if len(params[k]) < 1:
                params.pop(k)
        index += 1
        
    encoded = encoded.replace('?', '%s')
    with_params = encoded % tuple(sequence)
    decoded = with_params.decode(enc)
    return decoded

def join_sequence(sqa_tables, needed_table_names):
    
    logging.info('Determine the best JOIN sequence for ' + str(needed_table_names))
    adjacency_dict = build_adjacency_dict(sqa_tables)
    
    best_path = best_join(needed_table_names, adjacency_dict)
    
    for table_list in permutations(needed_table_names):
        path = best_join(table_list, adjacency_dict)        
        if len(path) < len(best_path):
            best_path = path
            
    logging.info('Best JOIN sequence for ' + str(needed_table_names) + ' is ' + str(best_path))
    return best_path
    
def build_adjacency_dict(sqa_tables):
    # This builds a dictionary containing all tables and their neighbors for Dijkstra's algorithm
    adjacency_dict = {}
    for table in sqa_tables:
        adjacency_dict[table.name] = set()
    for table in sqa_tables:            
        for fk in table.foreign_keys:
            # Relationships go both ways
            adjacency_dict[table.name].add(fk.column.table.name)
            adjacency_dict[fk.column.table.name].add(table.name)
    return adjacency_dict

def best_join(join_seq, adjacency_dict):
    path = []
    for i in range(0,len(join_seq)-1):
        tableA = join_seq[i]
        tableB = join_seq[i+1]
        path += shortest_path(tableA,tableB, adjacency_dict)
    path.append(join_seq[len(join_seq)-1])
    return path
        
def shortest_path(tableA, tableB, adjacency_dict):
    visited = set()
    #A set of all the tables you've visited so far
    distance = {tableA:0}
    #The distances (in joins) for each node
    joins_required = {tableA:[]}
    
    to_visit = set()
    #The current set of tables to visit
    next_to_visit = set()
    #The set of tables to visit after the current set is complete
    
    # first iteration
    for table_name in adjacency_dict[tableA]:
        #find the neighbors for each and make that the next round
        # the next tables take 1 join to get to
        distance[table_name] = 1
        # we start all joins with tableA
        joins_required[table_name] = [tableA]
        next_to_visit.add(table_name)
    visited.add(tableA)
        
    # subsequent iterations
    # having the table in the visited set guarantees we've passed it
    while tableB not in visited:
        # flush next_to_visit into to_visit
        to_visit = set(next_to_visit)
        next_to_visit = set()
        
        for table_name in to_visit:
            # find neighbors that we haven't visited
            for tname in adjacency_dict[table_name] - visited:
                # if the table is recursive, this is unnecessary
                if tname == table_name:
                    continue
                    
                if tname in distance.keys():
                    # If we have a distance recorded for a table
                    if distance[tname] > distance[table_name] + 1:
                        # and the recorded distance is greater than its possible distance
                        distance[tname] = distance[table_name] + 1
                        # replace the recorded distance with its new distance
                        joins_required[tname] = joins_required[table_name][:]
                        joins_required[tname].append(table_name)
                else:
                    distance[tname] = distance[table_name] + 1
                    joins_required[tname] = joins_required[table_name][:]
                    joins_required[tname].append(table_name)
                    
                next_to_visit.add(tname)
            visited.add(table_name)
    
    return joins_required[tableB]

parser = OptionParser()
parser.add_option("-t", "--type", dest="db_type", choices=['sqlite'], help="Define the database type. Only current option is sqlite")
parser.add_option("-l", "--location", type="string", dest="db_location", help="Define the database location.")
parser.add_option("-u", "--user", type="string", dest="username", help="(optional) Specify a database username")
parser.add_option("-p", "--password", type="string", dest="password", help="(optional) Specify a database password")
parser.add_option("-s", "--schema", type="string", dest="schema", help="(optional) Specify a database schema")
parser.add_option("-c", "--column", action="append", type="string", dest="columns", help="Define each column you want separately. Use the format TableName.ColumnName")
parser.add_option("-f", "--filter", action="append", type="string", dest="constraints", help="(optional) Define each filter you want separately. Use the format \"TableName.ColumnName , Operator, Value1, (optional) Value2\"")
parser.add_option("-r", "--rows", type="int", dest="row_limit", help="(optional) Define the number of rows you want returned")
parser.add_option("-q", "--sql", action="store_true", dest="sql", help="(optional) If flag is present, SQL is returned instead of data")

def main():
    (options, args) = parser.parse_args()
    #run('sqlite','C:\Chinook_Sqlite.sqlite',['Genre.Name', 'Customer.FirstName','InvoiceLine.UnitPrice'], constraints = [['InvoiceLine.UnitPrice','>=','.99',''],['InvoiceLine.UnitPrice','<','2','']], row_limit = 5, sql = False)
           
    if not options.db_type or not options.db_location or not options.columns:
        parser.error("You must provide at least the database type, database location, and desired columns. Type SQLementary.py -h to see how.")  
    
    cons = None
    if options.constraints:
        cons = [c.split(',') for c in options.constraints]
        
    run(options.db_type,
        options.db_location,
        options.columns,
        schema = options.schema,
        username = options.username,
        password = options.password,
        constraints = cons,
        row_limit = options.row_limit,
        sql = options.sql,
        commandline = True)
    
if __name__ == '__main__':
    main()