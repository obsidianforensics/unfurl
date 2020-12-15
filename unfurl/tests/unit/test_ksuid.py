from unfurl.core import Unfurl
import unittest


class TestKsuid(unittest.TestCase):

    def test_ksuid(self):
        """ Test of a typical ksuid """

        # unit test for a unique ksuid.
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='0o5Fs0EELR0fUjHjbCnEtdUwQe3')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 5)
        self.assertEqual(test.total_nodes, 5)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
