from unfurl.core import Unfurl
import unittest


class TestHashDetection(unittest.TestCase):

    def test_md5_hash_no_lookups(self):
        """ Test detecting a MD5 in a URL with lookups disabled """

        test = Unfurl()
        test.remote_lookups = False
        test.add_to_queue(
            data_type='url', key=None,
            value='http://test-hashes.com/test?1=5f4dcc3b5aa765d61d8327deb882cf99')
        test.parse_queue()

        # confirm that detected as MD5
        md5_node = next(n for n in test.nodes.values() if n.data_type == 'hash.md5')
        self.assertIn('Potential MD5 hash', md5_node.label)


if __name__ == '__main__':
    unittest.main()
