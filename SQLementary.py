from elm_objects import elm_column, elm_constraint, elm_table
import sqlsoup
from sqlalchemy import MetaData
import logging

logging.basicConfig(level=logging.INFO)

def run(database_type, database_url, returned_columns, schema = None, username = None, password = None,  constraints = None, row_limit = None):
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
                raise Exception (str(c[0]) + ' is ambiguous or not in the right format')
                                  
            tab = tab_col[0]
            col = tab_col[1]
            op = c[2]
            v1 = c[3]
            v2 = c[4]
            
            elm_constraints.append(elm_constraint(tab,col,op,v1,v2))
    
    logging.info('Building a list of all necessary columns to find necessary tables')
    ret_cols_temp = []        
    for tab_col in returned_columns:
        tc = tab_col.split('.')
        if len(tc) != 2:
            raise Exception (tab_col + ' is ambiguous or not in the right format')
        ret_cols_temp.append([tc[0], tc[1]])
        
    tabs_temp = set([table_column[0] for table_column in ret_cols_temp])
    con_tabs_temp = set([con.table_name for con in elm_constraints])
    
    tabs_temp = tabs_temp.union(con_tabs_temp)
    
    '''TODO: We have the names of the tables we need in tabs_temp. These need to have the optimal joins'''
    
    
    pass

def main():
    run('sqlite','C:\Chinook_Sqlite.sqlite',['Track.Name', 'Artist.Name'])

if __name__ == '__main__':
    main()