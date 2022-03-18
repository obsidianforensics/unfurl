import unittest

from unfurl.core import app as my_app


class TestApi(unittest.TestCase):

    def setUp(self):
        my_app.config["testing"] = True
        self.client = my_app.test_client()

    def test_home_ok(self):
        self.assertEqual(self.client.get("/", follow_redirects=True).status_code, 200)

    def test_api_without_url_ok(self):
        response = self.client.get("/json/visjs", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_api_call_ok(self):
        response = self.client.get("/https://mastodon.cloud/@TimDuran/103453805855961797", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
