import unittest
from CircularLinkedList import CircularLinkedList

class TestCircularLinkedList(unittest.TestCase):
    def setUp(self):
        self.cll = CircularLinkedList()

    def test_append_to_empty_list(self):
        self.cll.append(1)
        self.assertIsNotNone(self.cll.head)
        self.assertEqual(self.cll.head.data, 1)
        self.assertEqual(self.cll.head.next, self.cll.head)

    def test_append_multiple_elements(self):
        self.cll.append(1)
        self.cll.append(2)
        self.cll.append(3)
        
        self.assertEqual(self.cll.head.data, 1)
        self.assertEqual(self.cll.head.next.data, 2)
        self.assertEqual(self.cll.head.next.next.data, 3)
        self.assertEqual(self.cll.head.next.next.next, self.cll.head)
        
    def test_get_next_node(self):
        self.cll.append(1)
        self.cll.append(2)
        self.cll.append(3)
        
        current = self.cll.head
        self.assertEqual(current.data, 1)
        next_node = self.cll.get_next_node(current)
        self.assertEqual(next_node.data, 2)

        current = next_node
        next_node = self.cll.get_next_node(current)
        self.assertEqual(next_node.data, 3)

        current = next_node
        next_node = self.cll.get_next_node(current)
        self.assertEqual(next_node.data, 1)

    def test_get_next_node_single_element(self):
        self.cll.append(1)
        current = self.cll.head
        next_node = self.cll.get_next_node(current)
        self.assertEqual(next_node.data, 1)
        self.assertEqual(next_node, self.cll.head)
    
    def test_get_next_node_none(self):
        self.assertIsNone(self.cll.get_next_node(None))

    def test_first_node(self):
        self.assertIsNone(self.cll.first_node())
        
        self.cll.append(1)
        self.assertEqual(self.cll.first_node().data, 1)
        self.cll.append(2)
        self.assertEqual(self.cll.first_node().data, 1)

if __name__ == "__main__":
    unittest.main()
