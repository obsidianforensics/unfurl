from unfurl.core import Unfurl
import unittest


class TestMongo(unittest.TestCase):

    def test_mongo_objectid(self):
        """ Test parsing of a MongoDB ObjectID submitted directly """

        # ObjectID breakdown:
        #   65920080   = 0x65920080 = 1704067200 = 2024-01-01 00:00:00 UTC
        #   aabbccddee = machine identifier (MongoDB < 4.0) or random value (MongoDB 4.0+)
        #   112233     = counter (0x112233 = 1122867)
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='65920080aabbccddee112233')
        test.parse_queue()

        # test number of nodes:
        #   1: initial url
        #   2: mongo.objectid
        #   3: epoch-seconds (raw timestamp)
        #   4: descriptor (machine/process bytes)
        #   5: integer (counter)
        #   6: timestamp.epoch-seconds (human-readable, added by parse_timestamp.py)
        self.assertEqual(6, len(test.nodes.keys()))
        self.assertEqual(6, test.total_nodes)

        # confirm MongoDB ObjectID is detected
        self.assertIn('MongoDB ObjectID', test.nodes[2].label)

        # confirm timestamp is decoded correctly
        self.assertIn('2024-01-01 00:00:00', test.nodes[6].label)

        # confirm counter is parsed correctly
        self.assertEqual('Counter: 1122867', test.nodes[5].label)

    def test_mongo_objectid_in_url(self):
        """ Test that a MongoDB ObjectID embedded in a URL path is detected """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://example.com/api/products/65920080aabbccddee112233')
        test.parse_queue()

        # confirm MongoDB ObjectID is detected somewhere in the graph
        found_oid = any(
            node.label and 'MongoDB ObjectID' in node.label
            for node in test.nodes.values()
        )
        self.assertTrue(found_oid)

        # confirm timestamp is decoded somewhere in the graph
        found_ts = any(
            node.label and '2024-01-01 00:00:00' in node.label
            for node in test.nodes.values()
        )
        self.assertTrue(found_ts)

    def test_non_mongo_hex_ignored(self):
        """ Test that a 24-char hex string with a timestamp outside MongoDB's range is not parsed """

        # 00000001 = timestamp 1 (1970-01-01), well outside the 2009-2030 filter
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='00000001aabbccddee112233')
        test.parse_queue()

        # should produce only the initial node — not detected as a MongoDB ObjectID
        found_oid = any(
            node.label and 'MongoDB ObjectID' in node.label
            for node in test.nodes.values()
        )
        self.assertFalse(found_oid)


if __name__ == '__main__':
    unittest.main()
