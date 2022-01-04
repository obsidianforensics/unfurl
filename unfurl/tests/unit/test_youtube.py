from unfurl.core import Unfurl
import unittest


class TestYouTube(unittest.TestCase):

    def test_youtube(self):
        """ Test a YouTube.com URL, with t in seconds"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.youtube.com/watch?v=LnhSTZgzKuY&list=PLlFGZ98XmfGfV6RAY9fQSeRfyIuhVGSdm&index=2&t=42s')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 16)
        self.assertEqual(test.total_nodes, 16)

        # Test query parsing
        self.assertEqual('Video will start playing at 42 seconds', test.nodes[16].label)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)

    def test_youtu_be(self):
        """ Test a youtu.be URL, with t as int"""

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://youtu.be/LnhSTZgzKuY?list=PLlFGZ98XmfGfV6RAY9fQSeRfyIuhVGSdm&t=301')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 14)
        self.assertEqual(test.total_nodes, 14)

        # Test query parsing
        self.assertEqual('Video will start playing at 05:01 (mm:ss)', test.nodes[14].label)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
