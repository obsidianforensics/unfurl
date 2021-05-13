from unfurl.core import Unfurl
import unittest


class TestUuid(unittest.TestCase):

    def test_uuid_v1_null_ts_random_node_id(self):
        """ Test parsing of a UUIDv1, with a null timestamp and randomly-generated Node ID """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='00000000000010008f06a139ab18f414')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 6)
        self.assertEqual(test.total_nodes, 6)

        # confirm the Node ID is parsed as random
        self.assertEqual('The Node ID in this UUID is random', test.nodes[5].label)

        # confirm the time is parsed correctly
        self.assertIn('1582-10-15 00:00:00', test.nodes[6].label)

    def test_uuid_v1(self):
        """ Test parsing of a UUIDv1, with a legit timestamp and valid MAC address """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='a28cad70-0d73-11ea-aaef-0800200c9a66')
        test.parse_queue()

        # confirm the Node ID is parsed as a MAC address
        self.assertEqual('MAC address: 08:00:20:0C:9A:66', test.nodes[5].label)

        # confirm the time is parsed correctly
        self.assertIn('2019-11-22 22:01:28.775', test.nodes[6].label)

    def test_uuid_v4(self):
        """ Test parsing of a UUIDv4 """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='43c18e2b-6441-49e2-b907-f4c6262b22de')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 3)
        self.assertEqual(test.total_nodes, 3)

        # confirm the description is correct
        self.assertEqual('Version 4 UUID is randomly generated', test.nodes[3].label)


if __name__ == '__main__':
    unittest.main()
