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

        # confirm the scheme is parsed
        self.assertIn('English', test.nodes[14].label)

    def test_file_path_url(self):
        """ Test a URL that ends with a file path"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://dfir.blog/content/images/2019/01/logo.png')
        test.parse_queue()

        # confirm the scheme is parsed
        self.assertIn('File Extension: .png', test.nodes[13].label)


    def test_query_param_no_value(self):
        """Test that query parameters with no value are preserved."""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.facebook.com/photo.php?type=3&theater')
        test.parse_queue()

        # confirm that both query params are present, including the valueless "theater"
        query_pairs = {node.key: node.value for node in test.nodes.values()
                       if node.data_type == 'url.query.pair'}
        self.assertIn('type', query_pairs)
        self.assertIn('theater', query_pairs)
        self.assertEqual('3', query_pairs['type'])
        self.assertEqual('', query_pairs['theater'])


if __name__ == '__main__':
    unittest.main()
