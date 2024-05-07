import unittest
from cache import LRUCache

class TestLRUCache(unittest.TestCase):

    def test_cache_operations(self):
        cache = LRUCache(3)  # Initialize cache with max size 3

        # Test cache insertion and retrieval
        cache.set(1, 'a')
        cache.set(2, 'b')
        cache.set(3, 'c')
        self.assertEqual(cache.get(1), 'a')  # Key 1 is still in cache
        self.assertEqual(cache.get(2), 'b')  # Key 2 is still in cache
        self.assertEqual(cache.get(3), 'c')  # Key 3 is still in cache

        # Test cache eviction on adding new key-value pairs
        cache.set(4, 'd')  # Adding new key-value pair, should evict least recently used key 1
        self.assertIsNone(cache.get(1))  # Key 1 should be evicted
        self.assertEqual(cache.get(2), 'b')  # Key 2 is still in cache
        self.assertEqual(cache.get(3), 'c')  # Key 3 is still in cache
        self.assertEqual(cache.get(4), 'd')  # Key 4 is in cache now

        # Test cache update
        cache.set(3, 'cc')  # Update value for key 3
        self.assertEqual(cache.get(3), 'cc')  # New value for key 3 should be retrieved

        # Test cache retrieval after update
        self.assertEqual(cache.get(2), 'b')  # Key 2 is still in cache
        self.assertEqual(cache.get(4), 'd')  # Key 4 is still in cache
        self.assertIsNone(cache.get(1))  # Key 1 is still evicted

    def test_cache_capacity(self):
        cache = LRUCache(3)  # Initialize cache with max size 3

        # Test cache capacity with max size 3
        cache.set(1, 'a')
        cache.set(2, 'b')
        cache.set(3, 'c')
        cache.set(4, 'd')  # Adding new key-value pair, should evict least recently used key 1
        self.assertIsNone(cache.get(1))  # Key 1 should be evicted
        self.assertEqual(cache.get(2), 'b')  # Key 2 is still in cache
        self.assertEqual(cache.get(3), 'c')  # Key 3 is still in cache
        self.assertEqual(cache.get(4), 'd')  # Key 4 is in cache now

    def test_cache_replacement_policy(self):
        cache = LRUCache(3)  # Initialize cache with max size 3

        # Test cache replacement policy - Least Recently Used
        cache.set(1, 'a')
        cache.set(2, 'b')
        cache.set(3, 'c')
        cache.get(1)  # Accessing key 1, should move it to the head
        cache.set(4, 'd')  # Adding new key-value pair, should evict least recently used key 2
        self.assertIsNone(cache.get(2))  # Key 2 should be evicted
        self.assertEqual(cache.get(1), 'a')  # Key 1 is still in cache
        self.assertEqual(cache.get(3), 'c')  # Key 3 is still in cache
        self.assertEqual(cache.get(4), 'd')  # Key 4 is in cache now

    def test_cache_edge_cases(self):
        cache = LRUCache(0)  # Initialize cache with max size 0

        # Test cache with max size 0
        cache.set(1, 'a')  # Adding key-value pair to an empty cache should not raise error
        self.assertIsNone(cache.get(1))  # Retrieving from an empty cache should return None

        # Test cache with max size 1
        cache = LRUCache(1)
        cache.set(1, 'a')  # Adding key-value pair to a cache with size 1
        cache.set(2, 'b')  # Adding new key-value pair, should evict key 1
        self.assertIsNone(cache.get(1))  # Key 1 should be evicted
        self.assertEqual(cache.get(2), 'b')  # Key 2 should be in cache


if __name__ == '__main__':
    unittest.main()
