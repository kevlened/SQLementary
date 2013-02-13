import unittest
from SQLementary import build_elm_schema, run
from web import get_schema

class MainEngineTest(unittest.TestCase):
    def setUp(self):
        self.full_db_loc = 'sqlite:///static/sample_databases/Chinook_Sqlite.sqlite'
    
    def test_build_elm_schema(self):
        db, elm_tables = build_elm_schema(self.full_db_loc)
        
class MainWebTest(unittest.TestCase):
    def test_get_schema(self):
        schema = get_schema(1)
        pass

if __name__ == '__main__':
    #unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(MainEngineTest)
    suite = unittest.TestLoader().loadTestsFromTestCase(MainWebTest)
    unittest.TextTestRunner(verbosity=2).run(suite)