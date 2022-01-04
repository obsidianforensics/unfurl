from unfurl.core import Unfurl
import unittest


class TestMetasploit(unittest.TestCase):

    def test_metasploit_payload_uuid(self):
        """ Test a Metasploit payload UUID url """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://test-example.com/4PGoVGYmx8l6F3sVI4Rc8g1wms758YNVXPczHlPobpJENARS'
                  'uSHb57lFKNndzVSpivRDSi5VH2U-w-pEq_CroLcB--cNbYRroyFuaAgCyMCJDpWbws/')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 11)
        self.assertEqual(test.total_nodes, 11)

        # confirm that unique id parsed
        self.assertIn('Unique ID: e0f1a8546626c7c9', test.nodes[7].label)

        # confirm that arch parsed
        self.assertIn('Architecture: X64', test.nodes[9].label)

        # confirm embedded timestamp parsed
        self.assertEqual(1502815973, test.nodes[10].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_metasploit_checksum_url(self):
        """ Test a Metasploit checksum url """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://test-example.com/WsJH')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 7)
        self.assertEqual(test.total_nodes, 7)

        # confirm that unique id parsed
        self.assertIn('Matches Metasploit URL checksum for Windows', test.nodes[7].label)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
