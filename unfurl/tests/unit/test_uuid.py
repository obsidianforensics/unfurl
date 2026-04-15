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

    def test_uuid_v6(self):
        """ Test parsing of a UUIDv6 (time-ordered variant of UUIDv1) """

        # This is the UUIDv6 equivalent of the v1 UUID in test_uuid_v1; same timestamp and node.
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='1ea0d73a-28ca-6d70-aaef-0800200c9a66')
        test.parse_queue()

        # test number of nodes (includes MAC vendor lookup node)
        self.assertEqual(7, len(test.nodes.keys()))
        self.assertEqual(7, test.total_nodes)

        # confirm the description is correct
        self.assertIn('Version 6 UUID', test.nodes[3].label)

        # confirm the MAC address is parsed (same node as in the v1 test)
        self.assertEqual('MAC address: 08:00:20:0C:9A:66', test.nodes[5].label)

        # confirm the timestamp matches the v1 equivalent
        self.assertIn('2019-11-22 22:01:28.775', test.nodes[6].label)

    def test_uuid_v7(self):
        """ Test parsing of a UUIDv7 (Unix epoch timestamp) """

        # Reference UUID from RFC 9562: unix_ts_ms = 0x017F22E279B0 = 2022-02-22 19:22:22.000 UTC
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='017F22E2-79B0-7CC3-98C4-DC0C0C07398F')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(5, len(test.nodes.keys()))
        self.assertEqual(5, test.total_nodes)

        # confirm the description is correct
        self.assertIn('Version 7 UUID', test.nodes[3].label)

        # confirm the timestamp is parsed correctly
        self.assertIn('2022-02-22 19:22:22', test.nodes[5].label)

    def test_uuid_v8(self):
        """ Test parsing of a UUIDv8 (vendor-specific) """

        # Reference UUID from RFC 9562 Appendix
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='320C3D4D-CC00-875B-8EC9-32D5F69181C0')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(3, len(test.nodes.keys()))
        self.assertEqual(3, test.total_nodes)

        # confirm the description notes it is vendor-specific
        self.assertIn('Version 8 UUID', test.nodes[3].label)
        self.assertIn('vendor-specific', test.nodes[3].label)


if __name__ == '__main__':
    unittest.main()
