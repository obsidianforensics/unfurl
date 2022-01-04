from unfurl.core import Unfurl
import unittest


class TestUrl(unittest.TestCase):

    def test_url(self):
        """ Test a generic URL with a query string"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.test-example.com/testing/1?2=3&4=5')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 12)
        self.assertEqual(test.total_nodes, 12)

        # confirm the scheme is parsed
        self.assertIn('https', test.nodes[2].label)

        # confirm the scheme is parsed
        self.assertEqual('/testing/1', test.nodes[4].label)

        # confirm the query string params parse
        self.assertEqual('4: 5', test.nodes[12].label)

    def test_lang_param(self):
        """ Test a URL with a language query string param"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.test-example.com/testing/1?2=3&4=5&lang=en')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 14)
        self.assertEqual(test.total_nodes, 14)

        # confirm the scheme is parsed
        self.assertIn('English', test.nodes[14].label)

    def test_file_path_url(self):
        """ Test a URL that ends with a file path"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://dfir.blog/content/images/2019/01/logo.png')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 13)
        self.assertEqual(test.total_nodes, 13)

        # confirm the scheme is parsed
        self.assertIn('File Extension: .png', test.nodes[13].label)


if __name__ == '__main__':
    unittest.main()
