

class elm_constraint(object):
    '''Represents a constraint on a particular column'''
    def __init__(self, table_name, column_name, operator, val1, val2 = None):
        '''
        table_name (string) = table name of associated column
        column_name (string) = column name of associated column
        operator (string) = boolean or comparative operators defining how to use val1 and val2
        val1 (string) = first and primary value
        val2 (string) = used for BETWEEN operator only
        '''
        #: table_name (string) = table name of associated column
        self.table_name = None
        #: column_name (string) = column name of associated column
        self.column_name = None
        #: operator (string) = boolean or comparative operators defining how to use val1 and val2
        self.operator = None
        #: val1 (string) = first and primary value
        self.val1 = None
        #: val2 (string) = used for BETWEEN operator only
        self.val2 = None
        pass
    
class elm_column(object):
    '''Represents a column within SQLementary'''
    def __init__(self, column_data):
        '''
        column_data (SQLAlchemy.column) = column as it's represented by SQLAlchemy
        '''
        #: name (string) = column name
        self.name = None
        #: parent_table (string) = table name of the table this column belongs to
        self.parent_table = None
        #: data (SQLAlchemy.column) = column as it's represented by SQLAlchemy
        self.data = column_data
        #: constraint (elm_constraint) = how the column should be constrained (operator & values)    
        self.constraint = None
        pass
    
class elm_table(object):
    '''Represents a table within SQLementary'''
    def __init__(self,table_data):
        '''
        table_data (SQLAlchemy.table) = table as it's represented by SQLAlchemy
        '''
        #: name (string) = table name
        self.name = None
        #: data (SQLAlchemy.table) = table as it's represented by SQLAlchemy
        self.data = None
        #: elm_columns (list[elm_column]) = all the columns in this tables
        self.elm_columns = None
        pass