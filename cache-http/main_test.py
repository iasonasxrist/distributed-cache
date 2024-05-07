import unittest
from unittest.mock import patch, MagicMock
from cacheHTTPNode import CacheHTTPNode
# from zookeeper.zookeeperClient import zookeeperClient


class TestCacheHTTPNode(unittest.TestCase):
    def setUp(self):
        self.cache_node = CacheHTTPNode()

    def test_insert(self):
        # Mocking the behavior of amICacheLeader to return True
        self.cache_node.amICacheLeader = MagicMock(return_value=True)

        # Testing insertion when the node is the leader
        key = '13'
        value = 'test_value'
        self.cache_node.insert(key, value)

        # Assert that the cache has been updated
        self.assertEqual(self.cache_node.cache.get(key), value)

    @patch('cache_http.CacheHTTPNode.redirectToLeader')
    def test_insert_redirect(self, mock_redirect):
        # Mocking the behavior of amICacheLeader to return False
        self.cache_node.amICacheLeader = MagicMock(return_value=False)

        # Testing insertion redirection when the node is not the leader
        key = '13'
        value = 'test_value'
        self.cache_node.insert(key, value)

        # Assert that redirectToLeader has been called with the correct arguments
        mock_redirect.assert_called_once_with(key, value)

    def test_retrieve(self):
        key = '13'
        value = 'test_value'

        # Insert a value into the cache
        self.cache_node.cache.set(key, value)

        # Testing retrieval from cache
        retrieved_value = self.cache_node.retrieve(key)

        # Assert that the retrieved value is correct
        self.assertEqual(retrieved_value, value)

    # Add more test cases as needed

if __name__ == '__main__':
    unittest.main()
