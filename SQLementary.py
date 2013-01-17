

def run(database_type, database_url, returned_columns, schema = None, username = None, password = None,  constraints = None, row_limit = None):
    '''
    database_type (string) = sqlite, oracle, db2 etc. from the list of acceptable databases in SQLalchemy
    database_url (string) = location of the database
    schema (string) = optional database schema
    username (string), password (string) = optional database credentials
    returned_columns (list[string]) = columns that are expected in the resulting rows
    constraint (list[list[string,string,string,string=None]]) = optional columns to constrain. list[table.column,operator,val1,optional val2]
    row_limit = optional number of rows returned
    '''
    pass

def main():
    pass

if __name__ == '__main__':
    main()