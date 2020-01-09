from unfurl import Unfurl

import unittest

class TestTwitter(unittest.TestCase):

    def test_twitter(self):
        """ Test a tyipcal and a unique Discord url """
        
        # unit test for a unique Discord url.
        test = Unfurl()
        test.add_to_queue(data_type='url', key=None, 
            value='https://twitter.com/_RyanBenson/status/1098230906194546688')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 13)
        self.assertEqual(test.total_nodes, 13)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

if __name__ == '__main__':
    unittest.main()