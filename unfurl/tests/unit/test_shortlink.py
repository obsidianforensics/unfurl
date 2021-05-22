from unfurl.core import Unfurl
import unittest


class TestBitly(unittest.TestCase):

    def test_linkedin_shortlink(self):
        """ Test a LinkedIn shortlink; these work a little different than the rest"""
        
        test = Unfurl(remote_lookups=True)
        test.add_to_queue(data_type='url', key=None, value='https://lnkd.in/fDJnJ64')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 16)
        self.assertEqual(test.total_nodes, 16)

        self.assertEqual(test.nodes[4].value, '/fDJnJ64')
        self.assertEqual(test.nodes[9].value, 'thisweekin4n6.com')
        self.assertEqual(test.nodes[16].key, 4)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_twitter_shortlink(self):
        """ Test a Twitter shortlink; these use 301 redirects like most shortlinks"""

        test = Unfurl(remote_lookups=True)
        test.add_to_queue(data_type='url', key=None, value='https://t.co/g6VWYYwY12')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 15)
        self.assertEqual(test.total_nodes, 15)

        self.assertEqual(test.nodes[4].value, '/g6VWYYwY12')
        self.assertEqual(test.nodes[12].value, 'github.com')
        self.assertEqual(test.nodes[14].label, '1: obsidianforensics')

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_no_lookups(self):
        """ Test a shortlink with remote lookups disabled"""

        test = Unfurl()
        test.add_to_queue(data_type='url', key=None, value='https://t.co/g6VWYYwY12')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 6)
        self.assertEqual(test.total_nodes, 6)


if __name__ == '__main__':
    unittest.main()
