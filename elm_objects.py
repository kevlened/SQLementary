
class elm_constraint(object):
    '''Represents a constraint on a particular column'''
    def __init__(self, table_name, column_name, operator, val1, val2):
                
        self.table_name = table_name
        '''table_name (string) = table name of associated column'''
        
        self.column_name = column_name
        '''column_name (string) = column name of associated column'''
        
        self.operator = operator
        '''operator (string) = boolean or comparative operators defining how to use val1 and val2'''
        
        self.val1 = val1
        '''val1 (string) = first and primary value'''
        
        self.val2 = val2
        '''val2 (string) = used for BETWEEN operator only'''
        pass
    
class elm_column(object):
    '''Represents a column within SQLementary'''
    def __init__(self, column_data):        
        self.data = column_data
        '''data (SQLAlchemy.column) = column as it's represented by SQLAlchemy'''
        
        self.name = self.data.name
        '''name (string) = column name'''
        
        self.parent_table = self.data._from_objects[0].name
        '''parent_table (string) = table name of the table this column belongs to'''
        
        self.constraint = None
        '''constraint (elm_constraint) = how the column should be constrained (operator & values)'''
        pass
    
class elm_table(object):
    '''Represents a table within SQLementary'''
    def __init__(self,table_data):
        self.data = table_data
        '''data (SQLAlchemy.table) = table as it's represented by SQLAlchemy'''
        
        self.name = self.data.name
        '''name (string) = table name'''
        
        self.elm_columns = []
        '''elm_columns (list[elm_column]) = all the columns in this tables'''
        
        for sqa_column in self.data._columns._all_cols:
            self.elm_columns.append(elm_column(sqa_column))
        pass