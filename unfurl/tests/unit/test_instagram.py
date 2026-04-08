from unfurl.core import Unfurl
import unittest


def has_node(unfurl_instance, **criteria):
    """Check if a node matching all given criteria exists."""
    for node in unfurl_instance.nodes.values():
        if all(getattr(node, attr, None) == val for attr, val in criteria.items()):
            return True
    return False


class TestInstagram(unittest.TestCase):

    def _unfurl(self, url):
        u = Unfurl(remote_lookups=False)
        u.add_to_queue(data_type='url', key=None, value=url)
        u.parse_queue()
        return u

    def test_post_with_carousel(self):
        """Post URL parses shortcode, extracts timestamp, and parses img_index"""
        u = self._unfurl('https://www.instagram.com/p/DW1nTDiDvnF/?img_index=1')
        self.assertTrue(has_node(u, data_type='instagram.shortcode', value='DW1nTDiDvnF'))
        # Timestamp: 2026-04-07
        self.assertTrue(has_node(u, data_type='epoch-milliseconds', value=1775580510621))
        self.assertTrue(has_node(u, data_type='instagram.carousel_index', value='1'))
        # Shard and sequence should be present
        self.assertTrue(has_node(u, label='Shard ID: 958'))
        self.assertTrue(has_node(u, label='Sequence: 453'))

    def test_reels_plural_url(self):
        """Reels URL (plural /reels/) parses shortcode and extracts timestamp"""
        u = self._unfurl('https://www.instagram.com/reels/DWbNC2OEilE/')
        self.assertTrue(has_node(u, data_type='instagram.shortcode', value='DWbNC2OEilE'))
        self.assertTrue(has_node(u, data_type='epoch-milliseconds'))
        self.assertFalse(has_node(u, data_type='instagram.username', value='reels'))

    def test_reel_singular_url(self):
        """Reel URL (singular /reel/) parses shortcode"""
        u = self._unfurl('https://www.instagram.com/reel/DWbNC2OEilE/')
        self.assertTrue(has_node(u, data_type='instagram.shortcode', value='DWbNC2OEilE'))
        self.assertTrue(has_node(u, data_type='epoch-milliseconds'))

    def test_profile_not_parsed_as_shortcode(self):
        """Profile URL should not produce shortcode or username nodes
        (too few path segments for parse_url to split)"""
        u = self._unfurl('https://www.instagram.com/xkcd/')
        self.assertFalse(has_node(u, data_type='instagram.shortcode'))
        self.assertFalse(has_node(u, data_type='epoch-milliseconds'))

    def test_redirect_url(self):
        """l.instagram.com redirect parses destination URL"""
        u = self._unfurl('https://l.instagram.com/?u=https%3A%2F%2Fexample.com%2Fpage&e=ATMnj6KS')
        self.assertTrue(has_node(u, value='example.com'))
        self.assertTrue(has_node(u, data_type='instagram.redirect_tracking', value='ATMnj6KS'))

    def test_share_id_igshid(self):
        """igshid query parameter"""
        u = self._unfurl('https://instagram.com/user123?igshid=NTc4MTIwNjQ2YQ==')
        self.assertTrue(has_node(u, data_type='instagram.share_id', value='NTc4MTIwNjQ2YQ=='))

    def test_share_id_igsh(self):
        """igsh query parameter (newer format)"""
        u = self._unfurl('https://www.instagram.com/reel/DWbNC2OEilE/?igsh=MWdkOWZ3NHZ0ZngzMQ==')
        self.assertTrue(has_node(u, data_type='instagram.share_id', value='MWdkOWZ3NHZ0ZngzMQ=='))

    def test_language_param(self):
        """hl language parameter"""
        u = self._unfurl('https://www.instagram.com/p/DWbNC2OEilE/?hl=hr')
        self.assertTrue(has_node(u, data_type='instagram.language', value='hr'))

    def test_no_profile_on_static_pages(self):
        """Static pages should not be labeled as profiles"""
        u = self._unfurl('https://www.instagram.com/explore/tags/photography/')
        self.assertFalse(has_node(u, data_type='instagram.username', value='explore'))


if __name__ == '__main__':
    unittest.main()
