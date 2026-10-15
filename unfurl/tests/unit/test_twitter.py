from unfurl.core import Unfurl
import unittest


def get_nodes_by_type(unfurl_instance, data_type):
    return [n for n in unfurl_instance.nodes.values() if n.data_type == data_type]


class TestTwitter(unittest.TestCase):

    def test_twitter(self):
        """ Test a typical and a unique Twitter url """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None,
            value='https://twitter.com/_RyanBenson/status/1098230906194546688')
        test.parse_queue()

        # confirm that snowflake was detected
        snowflake_nodes = [
            n for n in get_nodes_by_type(test, 'url.path.segment')
            if n.value == '1098230906194546688']
        self.assertEqual(len(snowflake_nodes), 1)
        self.assertIn('Twitter Snowflakes', snowflake_nodes[0].hover)

        # embedded timestamp parses correctly
        timestamp_nodes = get_nodes_by_type(test, 'timestamp.epoch-milliseconds')
        self.assertEqual(len(timestamp_nodes), 1)
        self.assertIn('2019-02-20 14:40:26.837', timestamp_nodes[0].value)

        # make sure the queue finished empty
        self.assertTrue(test.queue.empty())

    def test_twitter_media_file_name_elsewhere(self):
        """ A Twitter image saved and re-hosted keeps its media ID as its file name """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='https://example.com/uploads/ErD8xv0VkAIBJe7.jpg')
        test.parse_queue()

        descriptors = [n.value for n in get_nodes_by_type(test, 'descriptor')]
        self.assertIn('File may originally be from Twitter (based on file name)', descriptors)
        self.assertEqual(1, len(get_nodes_by_type(test, 'timestamp.epoch-milliseconds')))

    def test_fifteen_character_file_names_are_not_all_twitter(self):
        """ Each of these decodes to a timestamp in range, but not to a plausible sequence """

        for file_name in ('FilesInspectorX.msi', 'IMG_0814-scaled.jpg', 'Artboard_1_copy.png'):
            with self.subTest(file_name=file_name):
                test = Unfurl()
                test.add_to_queue(
                    data_type='url', key=None, value=f'https://example.com/app/{file_name}')
                test.parse_queue()

                self.assertEqual([], get_nodes_by_type(test, 'timestamp.epoch-milliseconds'))
                self.assertNotIn(
                    'File may originally be from Twitter (based on file name)',
                    [n.value for n in get_nodes_by_type(test, 'descriptor')])


    def test_twitter_media_id_with_high_sequence(self):
        """ On Twitter, a media ID is decoded even with a sequence number too rare to trust elsewhere """

        test = Unfurl()
        test.add_to_queue(
            data_type='url', key=None, value='https://pbs.twimg.com/media/FilesInspectorX.jpg')
        test.parse_queue()

        self.assertIn('Sequence: 1511', [n.label for n in get_nodes_by_type(test, 'integer')])


if __name__ == '__main__':
    unittest.main()
