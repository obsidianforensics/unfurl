from unfurl.core import Unfurl
import unittest


class TestBitly(unittest.TestCase):

    def test_linkedin_shortlink(self):
        """ Test a LinkedIn shortlink; these work a little different than the rest"""
        
        test = Unfurl(remote_lookups=True)
        test.add_to_queue(data_type='url', key=None, value='https://lnkd.in/fDJnJ64')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 18)
        self.assertEqual(test.total_nodes, 18)

        self.assertEqual(test.nodes[4].value, '/fDJnJ64')
        self.assertEqual(test.nodes[11].value, 'thisweekin4n6.com')
        self.assertEqual(test.nodes[18].key, 4)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_twitter_shortlink(self):
        """ Test a Twitter shortlink; these use 301 redirects like most shortlinks"""

        test = Unfurl(remote_lookups=True)
        test.add_to_queue(data_type='url', key=None, value='https://t.co/g6VWYYwY12')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 18)
        self.assertEqual(test.total_nodes, 18)

        self.assertEqual(test.nodes[4].value, '/g6VWYYwY12')
        self.assertEqual(test.nodes[11].value, 'github.com')
        self.assertEqual(test.nodes[16].label, '1: obsidianforensics')

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_no_lookups(self):
        """ Test a shortlink with remote lookups disabled"""

        test = Unfurl()
        test.add_to_queue(data_type='url', key=None, value='https://t.co/g6VWYYwY12')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 8)
        self.assertEqual(test.total_nodes, 8)


if __name__ == '__main__':
    unittest.main()
