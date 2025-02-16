from unfurl.core import Unfurl
import unittest


class TestMacAddr(unittest.TestCase):

    def test_mac_addr(self):
        """ Test a MAC address with colons"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='00:B0:D0:63:C2:26')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(3, len(test.nodes.keys()))
        self.assertEqual(3, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('MAC address', test.nodes[2].label)

        # confirm the vendor is parsed
        self.assertIn('Dell', test.nodes[3].label)


    def test_mac_addr_bare(self):
        """ Test a bare MAC address (no delimiters)"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='00B0D063C226')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(3, len(test.nodes.keys()))
        self.assertEqual(3, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('MAC address', test.nodes[2].label)

        # confirm the vendor is parsed
        self.assertIn('Dell', test.nodes[3].label)


    def test_mac_addr_dashes(self):
        """ Test a MAC address with dashes"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='00-B0-D0-63-C2-26')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(3, len(test.nodes.keys()))
        self.assertEqual(3, test.total_nodes)

        # confirm the scheme is parsed
        self.assertIn('MAC address', test.nodes[2].label)

        # confirm the vendor is parsed
        self.assertIn('Dell', test.nodes[3].label)


if __name__ == '__main__':
    unittest.main()
