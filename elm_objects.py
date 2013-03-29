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

'''Represents a constraint or collection of constraints on a column'''
class elm_constraint(object):    
    def __init__(self, table_name, column_name, operator, val1, val2, aggregate, bool_type, constraints):
        
        # The table this constraint acts on        
        self.table_name = table_name
        
        # Column name of associated table
        self.column_name = column_name
        
        # The boolean or comparative operator defining how to use val1 and val2
        self.operator = operator
        
        # For any non-BETWEEN operator, the value is in val1
        self.val1 = val1
        
        # If this constraint has a BETWEEN operator, the second value is val2
        self.val2 = val2
        
        # This tracks what type of aggregate this constraint uses (SUM,AVG,etc)
        self.aggregate = aggregate
        
        # This tracks what kind of comparison the associated constraints use
        self.bool_type = bool_type
        
        # If this track has a bool_type, the associated constraints are here
        self.constraints = constraints
    
    def __repr__(self):
        if self.val2:
            #return '%s.%s %s %s %s' % self.table_name, self.column_name, self.operator, self.val1, self.val2
            return self.table_name + '.' + self.column_name + ' ' + self.operator + ' ' + self.val1 + ' and ' + self.val2
        else:
            #return '%s.%s %s %s' % self.table_name, self.column_name, self.operator, self.val1
            return self.table_name + '.' + self.column_name + ' ' + self.operator + ' ' + self.val1
    
class elm_column(object):
    '''Represents a column within SQLementary'''
    def __init__(self, column_data):        
        self.data = column_data
        '''data (SQLAlchemy.column) = column as it's represented by SQLAlchemy'''
        
        self.name = self.data.name
        '''name (string) = column name'''
        
        self.parent_table = self.data._from_objects[0].name
        '''parent_table (string) = table name of the table this column belongs to'''
        
        self.type = column_data.type
        
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