class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class CircularLinkedList:
    def __init__(self):
        self.head = None
        self.current = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.head.next = self.head
        else:
            temp = self.head
            while temp.next != self.head:
                temp = temp.next
            temp.next = new_node
            new_node.next = self.head

    def getNext(self):
        if not self.current:
            self.current = self.head
        else:
            self.current = self.current.next
        if self.current:
            return self.current.data
        return None
    
    
    def clear(self):
        self.head = None
        self.current = None