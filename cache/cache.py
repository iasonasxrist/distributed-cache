

class LRUCache:

    def __init__(self, max_size):
        self.cache = {}
        self.max_size = max_size
        self.DLL = DLL(max_size)

    def get(self, key):
        return self.DLL.search(key)

    def set(self, key, value):
        self.DLL.insert(key, value)
        

class Node:
    def __init__(self, key, value):
        self.value = value
        self.key = key
        self.next = None
        self.previous =None

class DLL:

    def __init__(self, max_size):
        self.head = None
        self.tail = None
        self.map = {}
        self.max_size = max_size

    def moveNodeToHead(self, node):
        if node is None:
            return None
        if self.head == None:
            self.head = node
            self.tail = node
        else:
            self.head.previous = node
            node.next = self.head
            self.head = node
            self.head.previous = None

    """
    New elements will be appended only in head in order to implement
    the behavior of the LRU cache. The most fresh element is always at
    the head of the list and the older in tail
    """
    def insert(self, key, value):

        nodeToMoveInHead = None
        #If key already existed the value is updated and we move the node to the head
        if key in self.map:
            nodeToUpdate = self.map[key]
            nodeToUpdate.value = value
            nodeToMoveInHead = nodeToUpdate
            
        else:
            nodeToMoveInHead = Node(key, value)

        if nodeToMoveInHead:
           self.removeElement(nodeToMoveInHead)
           self.moveNodeToHead(nodeToMoveInHead)
        self.map[key] = nodeToMoveInHead
        
        #Capacity and LRU drop
        while len(self.map) > self.max_size:
            nodeToDeleteInTail = self.tail
            self.removeElement(nodeToDeleteInTail)
            del self.map[nodeToDeleteInTail.key]
        return nodeToMoveInHead
            

    def removeElement(self, node):
        if node is None:
            return None
        if self.tail == node and self.tail is not None:
            self.tail = self.tail.previous
        if self.head == node and self.head is not None:
            self.head = self.head.next
        prev_node = node.previous
        next_node = node.next
        if prev_node != None:
            prev_node.next = next_node
        if next_node != None:
            next_node.previous = prev_node
        return node



    def search (self, key):
        if key in self.map:
            self.moveNodeToHead(self.removeElement(self.map[key]))
            return self.map[key].value
        else:
            return None
        



        


        
        
        
        
        