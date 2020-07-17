from unfurl.unfurl import Unfurl
import unittest


class TestGoogle(unittest.TestCase):

    def test_google_search_with_rlz(self):
        """ Test a Google search URL with a RLZ param """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.google.com/search?rlz=1C1GCAB_enUS907US907q=dfir+data')
        test.parse_queue()

        # Check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 18)
        self.assertEqual(test.total_nodes, 18)

        # Confirm that RLZ AP parsed
        self.assertEqual('Application: C1', test.nodes[12].label)

        # Language parses
        self.assertEqual('Language: English (en)', test.nodes[15].label)

        # Search cohort parses
        self.assertIn('United States the week of 2020-06-22', test.nodes[17].label)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
