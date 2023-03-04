from unfurl.core import Unfurl
import unittest


class TestDNS(unittest.TestCase):

    def test_dns(self):
        """ Test a DNS DoH URL """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://dnsserver.example.net/dns-query?dns=AAABAAABAAAAAAAAA3d3dwdleGFtcGxlA2NvbQAAAQAB')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 25)
        self.assertEqual(test.total_nodes, 25)

        # test that the qname parsed correctly
        self.assertIn('www.example.com.', test.nodes[23].value)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
