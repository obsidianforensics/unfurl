from unfurl.core import Unfurl
import unittest


class TestDiscord(unittest.TestCase):

    def test_discord(self):
        """ Test a typical and a unique Discord url """
        
        # unit test for a unique Discord url.
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://discordapp.com/channels/427876741990711298/551531058039095296')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 22)
        self.assertEqual(test.total_nodes, 22)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
