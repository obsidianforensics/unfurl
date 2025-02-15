from unfurl.core import Unfurl
import unittest


class TestTimestamps(unittest.TestCase):

    def test_filetime_hex(self):
        """ Test a bare conversion of Windows FileTime (Hex) timestamp """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='01d15614cbaee92c')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(2, len(test.nodes.keys()))
        self.assertEqual(2, test.total_nodes)

        # confirm the timestamp is parsed
        self.assertIn('2016-01-23 19:32:28.702751', test.nodes[2].label)
        self.assertIn('Windows FileTime (hex)', test.nodes[2].hover)

    def test_epoch_seconds_hex(self):
        """ Test a bare conversion of Epoch Seconds (Hex) timestamp """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='54A48E00')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(2, len(test.nodes.keys()))
        self.assertEqual(2, test.total_nodes)

        # confirm the timestamp is parsed
        self.assertIn('2015-01-01 00', test.nodes[2].label)
        self.assertIn('Epoch seconds (hex)', test.nodes[2].hover)

if __name__ == '__main__':
    unittest.main()
