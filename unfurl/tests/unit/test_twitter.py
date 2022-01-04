from unfurl.core import Unfurl
import unittest


class TestTwitter(unittest.TestCase):

    def test_twitter(self):
        """ Test a typical and a unique Twitter url """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://twitter.com/_RyanBenson/status/1098230906194546688')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 14)
        self.assertEqual(test.total_nodes, 14)

        # confirm that snowflake was detected
        self.assertIn('Twitter Snowflakes', test.nodes[9].hover)

        # embedded timestamp parses correctly
        self.assertEqual('2019-02-20 14:40:26.837', test.nodes[14].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
