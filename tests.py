import unittest
from SQLementary import get_connection, build_elm_schema, run
from web import get_schema, get_query_data

class EngineTest(unittest.TestCase):    
    def test_get_connection(self):
        db = get_connection(self.db_type, self.full_name, host = self.host, port = self.port, username = self.username, password = self.password)
    
    def test_build_elm_schema(self):       
        db = get_connection(self.db_type, self.full_name, host = self.host, port = self.port, username = self.username, password = self.password)         
        elm_tables = build_elm_schema(db)
        
    def test_get_schema(self):
        schema = get_schema(self.sample_id)
        
#    def test_get_query_data_1(self):
#        result = get_query_data(1)

class MainSqliteTest(EngineTest):
    def setUp(self):
        self.db_type = 'sqlite'
        self.host = None
        self.port = None
        self.full_name = 'static/sample_databases/Chinook_Sqlite.sqlite'
        self.username = None
        self.password = None
        self.sample_id = 1

class MainOracleTest(EngineTest):
    def setUp(self):
        self.db_type = 'oracle'
        self.host = 'localhost'
        self.port = '1521'
        self.full_name = 'xe'
        self.username = 'SYSTEM'
        self.password = 'password'
        self.sample_id = 2
        
class MainMySQLTest(EngineTest):
    def setUp(self):
        self.db_type = 'mysql'
        self.host = 'localhost'
        self.port = '3306'
        self.full_name = 'sakila'
        self.username = 'root'
        self.password = 'password'
        self.sample_id = 3
        
class MainPostgresTest(EngineTest):
    '''http://psycopg.lighthouseapp.com/projects/62710/tickets/31-importerror-dll-load-failed-the-specified-module-could-not-be-found'''
    def setUp(self):
        self.db_type = 'postgres'
        self.host = 'localhost'
        self.port = '5432'
        self.full_name = 'pg_catalog'
        self.username = 'postgres'
        self.password = 'password'
        self.sample_id = 4
        
class MainMSsqlTest(EngineTest):
    '''https://groups.google.com/d/msg/sqlalchemy/K9wJReDp-gM/LDn5xKStvEcJ'''
    def setUp(self):
        self.db_type = 'mssql'
        self.host = 'localhost'
        self.port = '1433'
        self.full_name = 'master'
        self.username = 'sa'
        self.password = 'ASDqwe123'
        self.sample_id = 5

if __name__ == '__main__':    
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainSqliteTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainOracleTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainMySQLTest))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainPostgresTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainMSsqlTest))
#    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainWebTest))
    unittest.TextTestRunner(verbosity=2).run(suite)