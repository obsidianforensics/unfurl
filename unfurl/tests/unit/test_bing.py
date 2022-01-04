from unfurl.core import Unfurl
import unittest


class TestBing(unittest.TestCase):

    def test_bing(self):
        """ Test a typical and a unique Bing url """
        
        # test a Bing search url
        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://www.bing.com/search?q=digital+forensics&qs=n&form=QBLH&sp=-1'
                  '&pq=digital+forensic&sc=8-16&sk=&cvid=77BF13B59CF84B98B13C067AAA3DB701')
        test.parse_queue()

        # test number of nodes
        self.assertEqual(len(test.nodes.keys()), 26)
        self.assertEqual(test.total_nodes, 26)

        # Test query parsing
        self.assertEqual('q: digital forensics', test.nodes[9].label)

        # is processing finished empty
        self.assertTrue(test.queue.empty())
        self.assertEqual(len(test.edges), 0)


if __name__ == '__main__':
    unittest.main()
