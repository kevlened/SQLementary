

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
    @type constraint: list[list[string,string,string,string=None]]
    @param constraint: optional columns to constrain. list[table.column,operator,val1,optional val2]
    @type row_limit: integer
    @param row_limit: optional number of rows returned
    @return: SQL as a string
    '''
    pass

def main():
    pass

if __name__ == '__main__':
    main()