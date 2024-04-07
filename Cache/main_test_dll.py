import unittest
from main import DLL

class TestDLL(unittest.TestCase):

    def test_dll_insertion(self):
        dll = DLL(3)  # Initialize DLL with max size 3

        # Test insertion and head update
        dll.insert(1, 'a')
        self.assertEqual(dll.head.key, 1)  # Key 1 should be in head after insertion
        dll.insert(2, 'b')
        self.assertEqual(dll.head.key, 2)  # Key 2 should be in head after insertion
        dll.insert(3, 'c')
        self.assertEqual(dll.head.key, 3)  # Key 3 should be in head after insertion

    def test_dll_retrieval(self):
        dll = DLL(3)  # Initialize DLL with max size 3
        dll.insert(1, 'a')
        dll.insert(2, 'b')
        dll.insert(3, 'c')

        # Test retrieval and head update
        dll.search(1)  # Accessing key 1, should move it to the head
        self.assertEqual(dll.head.key, 1)  # Key 1 should be in head after retrieval
        dll.search(2)  # Accessing key 2, should move it to the head
        self.assertEqual(dll.head.key, 2)  # Key 2 should be in head after retrieval
        dll.search(3)  # Accessing key 3, should move it to the head
        self.assertEqual(dll.head.key, 3)  # Key 3 should be in head after retrieval

    def test_dll_capacity(self):
        dll = DLL(3)  # Initialize DLL with max size 3
        dll.insert(1, 'a')
        dll.insert(2, 'b')
        dll.insert(3, 'c')

        # Test capacity maintenance
        dll.insert(4, 'd')  # Adding new key-value pair, should evict least recently used key 1
        self.assertIsNone(dll.search(1))  # Key 1 should be evicted
        self.assertEqual(dll.head.key, 4)  # Key 4 should be in head after insertion

    def test_dll_edge_cases(self):
        dll = DLL(0)  # Initialize DLL with max size 0

        # Test insertion and retrieval with max size 0
        dll.insert(1, 'a')  # Adding key-value pair to an empty DLL should not raise error
        self.assertIsNone(dll.search(1))  # Retrieving from an empty DLL should return None

        # Test insertion and retrieval with max size 1
        dll = DLL(1)
        dll.insert(1, 'a')  # Adding key-value pair to a DLL with size 1
        self.assertEqual(dll.head.key, 1)  # Key 1 should be in head after insertion
        dll.insert(2, 'b')  # Adding new key-value pair, should evict key 1
        self.assertIsNone(dll.search(1))  # Key 1 should be evicted
        self.assertEqual(dll.head.key, 2)  # Key 2 should be in head after insertion

if __name__ == '__main__':
    unittest.main()
