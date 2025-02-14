from unfurl.core import Unfurl
import unittest


class TestIp(unittest.TestCase):

    def test_ip(self):
        """ Test a generic IP with a scheme and path"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://216.58.199.78/test')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(4, len(test.nodes.keys()))
        self.assertEqual(4, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('https', test.nodes[2].label)

        # confirm the IP is parsed
        self.assertEqual('216.58.199.78', test.nodes[3].label)

        # confirm the path is parsed
        self.assertIn('path', test.nodes[4].hover)


    def test_almost_ip(self):
        """ Test a domain that looks almost like an IP, with a scheme and path"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://216.58.199.com/test')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(7, len(test.nodes.keys()))
        self.assertEqual(7, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('https', test.nodes[2].label)

        # confirm the domain is parsed
        self.assertEqual('Domain Name: 199.com', test.nodes[6].label)

        # confirm the path is parsed
        self.assertIn('path', test.nodes[4].hover)


    def test_int_ip(self):
        """ Test an IP represented as an integer, with a scheme and path"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://3627730766/test')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(5, len(test.nodes.keys()))
        self.assertEqual(5, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('https', test.nodes[2].label)

        # confirm the IP is parsed
        self.assertEqual('216.58.199.78', test.nodes[5].label)

        # confirm the path is parsed
        self.assertIn('path', test.nodes[4].hover)


    def test_hex_ip(self):
        """ Test an IP represented as hex, with a scheme and path"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://0xD83AC74E/test')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(6, len(test.nodes.keys()))
        self.assertEqual(6, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('https', test.nodes[2].label)

        # confirm the IP is parsed
        self.assertEqual('216.58.199.78', test.nodes[6].label)

        # confirm the path is parsed
        self.assertIn('path', test.nodes[4].hover)


    def test_octal_ip(self):
        """ Test an IP represented as octal, with a scheme and path"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://0330.0072.0307.0116/test')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(5, len(test.nodes.keys()))
        self.assertEqual(5, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('https', test.nodes[2].label)

        # confirm the IP is parsed
        self.assertEqual('216.58.199.78', test.nodes[5].label)

        # confirm the path is parsed
        self.assertIn('path', test.nodes[4].hover)


if __name__ == '__main__':
    unittest.main()
