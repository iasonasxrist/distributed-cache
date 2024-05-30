class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class CircularLinkedList:
    def __init__(self):
        self.head = None
    
    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            self.head.next = self.head
        else:
            temp = self.head
            while temp.next != self.head:
                temp = temp.next
            
            temp.next = new_node
            new_node.next = self.head

    def get_next_node(self, current_node):
        if current_node is None:
            return None
        next_node = current_node.next
        return next_node

    def first_node(self):
        return self.head
    
c =  CircularLinkedList()
c.append(1)
c.append(2)
c.append(3)
a = c.first_node()
b = c.get_next_node(a)
print(b.data)
d = c.get_next_node(b)
print(d.data)