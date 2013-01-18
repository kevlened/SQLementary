

class elm_constraint(object):
    '''Represents a constraint on a particular column'''
    def __init__(self, table_name, column_name, operator, val1, val2 = None):
                
        self.table_name = None
        '''table_name (string) = table name of associated column'''
        
        self.column_name = None
        '''column_name (string) = column name of associated column'''
        
        self.operator = None
        '''operator (string) = boolean or comparative operators defining how to use val1 and val2'''
        
        self.val1 = None
        '''val1 (string) = first and primary value'''
        
        self.val2 = None
        '''val2 (string) = used for BETWEEN operator only'''
        pass
    
class elm_column(object):
    '''Represents a column within SQLementary'''
    def __init__(self, column_data):
        
        self.name = None
        '''name (string) = column name'''
        
        self.parent_table = None
        '''parent_table (string) = table name of the table this column belongs to'''
        
        self.data = column_data
        '''data (SQLAlchemy.column) = column as it's represented by SQLAlchemy'''
        
        self.constraint = None
        '''constraint (elm_constraint) = how the column should be constrained (operator & values)'''
        pass
    
class elm_table(object):
    '''Represents a table within SQLementary'''
    def __init__(self,table_data):
        
        self.name = None
        '''name (string) = table name'''
        
        self.data = table_data
        '''data (SQLAlchemy.table) = table as it's represented by SQLAlchemy'''
        
        self.elm_columns = None
        '''elm_columns (list[elm_column]) = all the columns in this tables'''
        pass