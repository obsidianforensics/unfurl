from unfurl import Unfurl

import unittest


class TestBitly(unittest.TestCase):

    def test_bitly(self):
        """ Test a Bitly url, including expansion via Bitly API """
        
        test = Unfurl()
        test.add_to_queue(data_type='url', key=None, value='http://bit.ly/36XFLt9')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 15)
        self.assertEqual(test.total_nodes, 15)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
