from unfurl.core import Unfurl
import unittest


class TestBase64(unittest.TestCase):

    def test_padded_b64_ascii(self):
        """ Test a simple ASCII string that is base64-encoded."""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='dGVzdHl0ZXN0dGVzdA==')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 2)
        self.assertEqual(test.total_nodes, 2)

        # confirm that it was decoded from b64 to a string
        self.assertEqual('string', test.nodes[2].data_type)

        # confirm that text decoded correctly
        self.assertEqual('testytesttest', test.nodes[2].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_unpadded_b64_ascii(self):
        """ Test a simple ASCII string that is base64-encoded, with padding removed."""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='dGVzdHl0ZXN0dGVzdA')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 2)
        self.assertEqual(test.total_nodes, 2)

        # confirm that it was decoded from b64 to a string
        self.assertEqual('string', test.nodes[2].data_type)

        # confirm that text decoded correctly
        self.assertEqual('testytesttest', test.nodes[2].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_incorrect_padded_b64_ascii(self):
        """ Test a simple ASCII string that is base64-encoded, with incorrect padding"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='dGVzdHl0ZXN0dGVzdA=')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 2)
        self.assertEqual(test.total_nodes, 2)

        # confirm that it was decoded from b64 to a string
        self.assertEqual('string', test.nodes[2].data_type)

        # confirm that text decoded correctly
        self.assertEqual('testytesttest', test.nodes[2].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
