

class elm_constraint(object):
    def __init__(self,operator, val1, val2 = None):
        '''
        operator (string) = boolean or comparative operators defining how to use val1 and val2
        val1 (string) = first and primary value
        val2 (string) = used for BETWEEN operator only
        '''
        pass
    
class elm_column(object):
    '''Represents a column within SQLementary'''
    def __init__(self, column_data):
        '''
        column_data (SQLAlchemy.column) = column as it's represented by SQLAlchemy
        '''
        #: name (string) = column name
        #: parent_table (string) = table name of the table this column belongs to
        #: data (SQLAlchemy.column) = column as it's represented by SQLAlchemy
        #: constraint (elm_constraint) = how the column should be constrained (operator & values)        
        pass
    
class elm_table(object):
    '''Represents a table within SQLementary'''
    def __init__(self,table_data):
        '''
        table_data (SQLAlchemy.table) = table as it's represented by SQLAlchemy
        '''
        #: name (string) = table name
        #: data (SQLAlchemy.table) = table as it's represented by SQLAlchemy
        #: elm_columns (list[elm_column]) = all the columns in this tables
        pass