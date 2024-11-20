from unfurl.core import Unfurl
import unittest


class TestBluesky(unittest.TestCase):

    def test_bluesky_post(self):
        """ Test a typical Bluesky post URL """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://bsky.app/profile/jay.bsky.team/post/3lbd2ebt3wk2r')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 13)
        self.assertEqual(test.total_nodes, 13)

        # confirm that TID was detected
        self.assertIn('timestamp identifiers', test.nodes[12].hover)

        # confirm that TID was extracted correctly
        self.assertEqual(1732040395098000, test.nodes[12].value)

        # embedded timestamp parses correctly
        self.assertEqual('2024-11-19 18:19:55.098000+00:00', test.nodes[13].value)

    def test_bluesky_bare_tid(self):
        """ Test parsing a Bluesky/ATProto TID"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='3laulgolrfz2f')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 3)
        self.assertEqual(test.total_nodes, 3)

        # confirm that TID was detected
        self.assertIn('timestamp identifiers', test.nodes[2].hover)

        # confirm that TID was extracted correctly
        self.assertEqual(1731543333133695, test.nodes[2].value)

        # embedded timestamp parses correctly
        self.assertEqual('2024-11-14 00:15:33.133695+00:00', test.nodes[3].value)

if __name__ == '__main__':
    unittest.main()
