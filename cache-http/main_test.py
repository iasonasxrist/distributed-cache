import unittest
from unittest.mock import patch, MagicMock
from cacheHTTPNode import CacheHTTPNode
from zookeeper.zookeeperClient import zookeeperClient

class TestCacheHTTPNode(unittest.TestCase):
    def setUp(self):
        self.cache_node = CacheHTTPNode()

    def test_insert(self):
        self.cache_node.amICacheLeader = MagicMock(return_value=True)

        key = '13'
        value = 'test_value'
        self.cache_node.insert(key, value)

        self.assertEqual(self.cache_node.cache.get(key), value)

    @patch('cache_http.CacheHTTPNode.redirectToLeader')
    def test_insert_redirect(self, mock_redirect):
        self.cache_node.amICacheLeader = MagicMock(return_value=False)
        key = '13'
        value = 'test_value'
        self.cache_node.insert(key, value)

        mock_redirect.assert_called_once_with(key, value)

    def test_retrieve(self):
        key = '13'
        value = 'test_value'

        self.cache_node.cache.set(key, value)

        retrieved_value = self.cache_node.retrieve(key)

        self.assertEqual(retrieved_value, value)

if __name__ == '__main__':
    unittest.main()
