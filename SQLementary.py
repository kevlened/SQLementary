from elm_objects import elm_column, elm_constraint, elm_table
import sqlsoup
from sqlalchemy import MetaData
from sqlalchemy.sql import column, table, select, join
import logging
from itertools import permutations
import sqlparse

logging.basicConfig(level=logging.INFO)

def run(database_type, database_url, returned_columns, schema = None, username = None, password = None,  constraints = None, row_limit = None, data = False):
    '''
    Returns SQL without the need to understand the SQL logic
    @type database_type: string
    @param database_type: sqlite, oracle, db2 etc. from the list of acceptable databases in SQLalchemy
    @type database_url: string
    @param database_url: location of the database
    @type schema: string
    @param schema: optional database schema
    @type username: string
    @param username: optional database credentials
    @type password: string
    @param password: optional database credentials
    @type returned_columns: list[string]
    @param returned_columns: columns that are expected in the resulting rows
    @type constraint: list[list[string,string,string,string]]
    @param constraint: optional columns to constrain. list[table.column,operator,val1,optional val2]
    @type row_limit: integer
    @param row_limit: optional number of rows returned
    @return: SQL as a string
    '''
    
    db_full_loc = '%s:///%s' % (database_type, database_url)
    db = sqlsoup.SQLSoup(db_full_loc)
    
    elm_tables = []
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
            '''Sanitize val2'''
            if len(c) == 4:
                c.append(None)
            if c[4] == '':
                c[4] = None
            else:
                raise Exception (c + ' is not a valid constraint')
            
            tab_col = c[0].split('.')
            if len(tab_col) != 2:
                raise Exception ('The column ' + str(c[0]) + ' is ambiguous or not in the right format')
                                  
            tab = tab_col[0]
            col = tab_col[1]
            op = c[2]
            v1 = c[3]
            v2 = c[4]
            
            elm_constraints.append(elm_constraint(tab,col,op,v1,v2))
    
    logging.info('Building a list of necessary tables')
    ret_cols = []
    for tab_col in returned_columns:
        tc = tab_col.split('.')
        if len(tc) != 2:
            raise Exception ('The column ' + tab_col + ' is ambiguous or not in the right format')
        ret_cols.append([tc[0], tc[1]])
        
    tabs_temp = set([table_column[0] for table_column in ret_cols])    
    con_tabs_temp = set([con.table_name for con in elm_constraints])    
    tabs_temp = tabs_temp.union(con_tabs_temp)
    
    col_tab_all = ret_cols[:]
    if len(elm_constraints) > 0:
        col_tab_all.append([[con.table_name, con.column_name] for con in elm_constraints])
    
    '''Validate the tables actually exist'''
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
    
    joins = join_sequence(list(sqa_tables), list(tabs_temp))
    
    table_dict = {tab.name:tab.data for tab in elm_tables}
    
    '''Build the columns to select'''
    sqa_select_cols = []
    for tc in ret_cols:
        t = tc[0]
        c = tc[1]
        for ec in table_dict[t]._columns._all_cols:
            if ec.name == c:
                sqa_select_cols.append(ec)
                break
    
    '''Build the tables to join'''  
    sqa_joins = None
    if len(joins) == 1:
        sqa_joins = table_dict[joins[0]]
    else:
        sqa_joins = join(table_dict[joins[0]], table_dict[joins[1]])
        for i in range(2,len(joins)):
            sqa_joins = join(sqa_joins, table_dict[joins[i]])
            
    '''Build the full select statement'''
    sqa_select = select(sqa_select_cols, from_obj=[sqa_joins]).distinct()
    if row_limit:
        sqa_select = sqa_select.limit(row_limit)
    
    '''Execute the full statement'''
    if data:
        conn = db.engine.connect()
        res = conn.execute(sqa_select).fetchall()
        for row in res:
            logging.info('Data row ' + str(row))
    else:    
        compile_engine = sqa_select.compile()
        compile_engine.statement.use_labels = True
        sql = str(compile_engine.statement)
        logging.info('Returned query ' + sqlparse.format(sql, reindent=True, keyword_case='upper'))

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
    '''A set of all the tables you've visited so far'''
    distance = {tableA:0}
    '''The distances (in joins) for each node'''
    joins_required = {tableA:[]}
    
    to_visit = set()
    '''The current set of tables to visit'''
    next_to_visit = set()
    '''The set of tables to visit after the current set is complete'''
    
    # first iteration
    for table_name in adjacency_dict[tableA]:
        '''find the neighbors for each and make that the next round'''
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
                    ''' If we have a distance recorded for a table'''
                    if distance[tname] > distance[table_name] + 1:
                        ''' and the recorded distance is greater than its possible distance'''
                        distance[tname] = distance[table_name] + 1
                        ''' replace the recorded distance with its new distance'''
                        joins_required[tname] = joins_required[table_name][:]
                        joins_required[tname].append(table_name)
#                    if len(joins_required[tname]) > len(joins_required[table_name]) + 1:
#                        joins_required[tname].append(table_name)
                else:
                    distance[tname] = distance[table_name] + 1
                    joins_required[tname] = joins_required[table_name][:]
                    joins_required[tname].append(table_name)
                    
                next_to_visit.add(tname)
            visited.add(table_name)
    
    return joins_required[tableB]

def main():
    run('sqlite','C:\Chinook_Sqlite.sqlite',['Album.Title', 'Track.Name', 'MediaType.Name', 'Genre.Name'], row_limit = None, data = False)

if __name__ == '__main__':
    main()