from unfurl.core import Unfurl
import unittest


class TestLinkedIn(unittest.TestCase):

    def test_linkedin_profile_id(self):
        """ Test parsing of a LinkedIn Profile ID"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://linkedin.com/in/charolette-pare-93b3a220a')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 10)
        self.assertEqual(test.total_nodes, 10)

        # embedded ID parses correctly
        self.assertEqual(890781887, test.nodes[10].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_linkedin_id(self):
        """ Test parsing of a LinkedIn ID"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.linkedin.com/messaging/thread/6685980502161199104/')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 13)
        self.assertEqual(test.total_nodes, 13)

        # embedded timestamp parses correctly
        self.assertEqual('2020-07-06 18:59:31.226', test.nodes[13].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_linkedin_message_id_v2(self):
        """ Test parsing of a LinkedIn Message ID v2"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.linkedin.com/messaging/thread/2-ODEzNDk4YWQtMzA3Mi01NjlmLWE0M2YtY2YwNzFhMjM1YTAzXzAxMw==/')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 12)
        self.assertEqual(test.total_nodes, 12)

        # embedded timestamp parses correctly
        self.assertEqual('813498ad-3072-569f-a43f-cf071a235a03_013', test.nodes[12].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
