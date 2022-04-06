from unfurl.core import Unfurl
import unittest


class TestGoogle(unittest.TestCase):

    def test_google_search_with_rlz(self):
        """ Test a Google search URL with a RLZ param """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.google.com/search?rlz=1C1GCAB_enUS907US907&q=dfir+data')
        test.parse_queue()

        # Check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 22)
        self.assertEqual(test.total_nodes, 22)

        # Confirm that RLZ AP parsed
        self.assertEqual('Application: C1', test.nodes[15].label)

        # Language parses
        self.assertEqual('Language: English (en)', test.nodes[18].label)

        # Search cohort parses
        self.assertIn('United States the week of 2020-06-22', test.nodes[20].label)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_google_search_with_rlz_different_weeks(self):
        """ Test a Google search URL with a RLZ param with different cohort weeks """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.google.com/search?rlz=1C1GCAB_esUS97US1007&q=dfir+data')
        test.parse_queue()

        # Check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 22)
        self.assertEqual(test.total_nodes, 22)

        # Confirm that RLZ AP parsed
        self.assertEqual('Application: C1', test.nodes[15].label)

        # Language parses
        self.assertEqual('Language: Spanish (es)', test.nodes[18].label)

        # Install cohort parses (2 digit week)
        self.assertIn('United States the week of 2004-12-13', test.nodes[19].label)

        # Search cohort parses (4 digit week)
        self.assertIn('United States the week of 2022-05-23', test.nodes[20].label)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_google_search_with_aqs(self):
        """ Test a Google search URL with a AQS param """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.google.com/search?q=dfir&oq=dfir'
                  '&aqs=chrome.1.69i60j0i433i512j0i512j69i60l2j69i61j69i60j69i65.2855j0j7')
        test.parse_queue()

        # Check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 44)
        self.assertEqual(test.total_nodes, 44)

        # Confirm that clicked suggestion parsed
        self.assertEqual('Clicked Suggestion: 1', test.nodes[17].label)

        # Check that 1st autocomplete match parsed
        self.assertEqual('Autocomplete Match (0): 69i60', test.nodes[18].label)

        # Check that match type of 1st autocomplete match parsed
        self.assertIn('Type: Native Chrome Suggestion', test.nodes[28].label)

        # Check that match subtype of autocomplete match 5 parsed
        self.assertIn('Subtype: Omnibox History Title', test.nodes[39].label)

        # Check that Query Formulation Time parsed
        self.assertIn('2.855 seconds', test.nodes[25].label)

        # Check that page classification was parsed and looked up
        self.assertIn('(with omnibox as starting focus)', test.nodes[44].label)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
