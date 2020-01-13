import unittest
from unfurl.Unfurl import app

class TestApi(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()

    def test_home(self):
        result = self.app.get('/')
        print(result)


if __name__ == '__main__':
    unittest.main()