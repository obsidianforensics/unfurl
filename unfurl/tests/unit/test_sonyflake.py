from unfurl.core import Unfurl
import unittest


class TestSonyflake(unittest.TestCase):

    def test_sonyflake(self):
        """ Test of a Sonyflake """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='45eec4a4600041b')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 5)
        self.assertEqual(test.total_nodes, 5)

        # confirm the machine ID is parsed correctly
        self.assertIn('4.27', test.nodes[4].label)

        # confirm the time is parsed correctly
        self.assertIn('2020-08-12 17:35:29.98', test.nodes[5].label)


if __name__ == '__main__':
    unittest.main()
