from unfurl.core import Unfurl
import unittest


class TestHashDetection(unittest.TestCase):

    def test_md5_hash_no_lookups(self):
        """ Test detecting a MD5 in a URL with lookups disabled """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='http://test-hashes.com/test?1=5f4dcc3b5aa765d61d8327deb882cf99')
        test.parse_queue()

        # check the number of nodes
        self.assertEqual(len(test.nodes.keys()), 9)
        self.assertEqual(test.total_nodes, 9)

        # confirm that detected as MD5
        self.assertIn('Potential MD5 hash', test.nodes[9].label)


if __name__ == '__main__':
    unittest.main()
