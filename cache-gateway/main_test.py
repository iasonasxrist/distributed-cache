import unittest
from CircularLinkedList import CircularLinkedList

class TestCircularLinkedList(unittest.TestCase):

    def setUp(self):
        self.cll = CircularLinkedList()
        
    def test_append_single_element(self):
        self.cll.append(1)
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

    def test_get_next(self):
        self.cll.append(1)
        self.cll.append(2)
        self.cll.append(3)
        self.assertEqual(self.cll.getNext(), 1)
        self.assertEqual(self.cll.getNext(), 2)
        self.assertEqual(self.cll.getNext(), 3)
        self.assertEqual(self.cll.getNext(), 1)
        
    def test_clear(self):
        self.cll.append(1)
        self.cll.append(2)
        self.cll.append(3)
        self.cll.clear()
        self.assertIsNone(self.cll.head)
        self.assertIsNone(self.cll.current)
        
    def test_get_next_on_empty_list(self):
        self.assertIsNone(self.cll.getNext())

if __name__ == '__main__':
    unittest.main()