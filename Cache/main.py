

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
            nodeToUpdate.previous.next = nodeToUpdate.next
            nodeToUpdate.next = nodeToUpdate.prev
            
        else:
            nodeToMoveInHead = Node(key, value)
            self.map[key] = nodeToMoveInHead

        if nodeToMoveInHead:
            self.moveNodeToHead(nodeToMoveInHead)
        
        #Capacity and LRU drop
        while len(self.map) > self.max_size:
            self.removeElementInTail()




    def removeElementInTail(self):
     
        if self.tail == None:
            return
        
        if self.tail == self.head:
            del self.map[self.tail.key]
            self.tail = self.head = None
            return
        
        del self.map[self.tail.key]
        tempNode = self.tail.previous
        tempNode.next= None
        self.tail.previous = None
        self.tail = tempNode
    
        

    def search (self, key):
        if key in self.map:
            self.moveNodeToHead(self.map[key])
            return self.map[key].value
        else:
            return None
        



        


        
        
        
        
        