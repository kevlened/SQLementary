import unittest
from SQLementary import get_connection, build_elm_schema, run
from web import get_schema, get_query_data

class EngineTest(unittest.TestCase):    
    def test_get_connection(self):
        db = get_connection(self.db_type, self.full_name, host = self.host, port = self.port, username = self.username, password = self.password)
    
    def test_build_elm_schema(self):       
        db = get_connection(self.db_type, self.full_name, host = self.host, port = self.port, username = self.username, password = self.password)         
        elm_tables = build_elm_schema(db)

class MainSqliteTest(EngineTest):
    def setUp(self):
        self.db_type = 'sqlite'
        self.host = None
        self.port = None
        self.full_name = 'static/sample_databases/Chinook_Sqlite.sqlite'
        self.username = None
        self.password = None

class MainOracleTest(EngineTest):
    def setUp(self):
        self.db_type = 'oracle'
        self.host = 'localhost'
        self.port = '1521'
        self.full_name = 'xe'
        self.username = 'SYSTEM'
        self.password = 'password'
        
class MainWebTest(unittest.TestCase):
    def test_get_schema_1(self):
        schema = get_schema(1)
    
    def test_get_query_data_1(self):
        result = get_query_data(1)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainSqliteTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainOracleTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MainWebTest))
    unittest.TextTestRunner(verbosity=2).run(suite)