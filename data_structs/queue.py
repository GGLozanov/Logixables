class QueueNode:
    def __init__(self, data):
        self.data = data
        self.next = None

    def __str__(self) -> str:
        return f"{self.data}" + ("->" if self.next != None else "")

    def __repr__(self) -> str:
        return self.__str__()
 
class Queue:
    def __init__(self, head: QueueNode | None = None):
        self.head = self.rear = head
 
    def is_empty(self):
        return self.head == None
 
    def enqueue(self, item: QueueNode):
        if self.rear == None:
            self.head = self.rear = item
            return
        self.head.next = item
        self.head = item
 
    def dequeue(self) -> QueueNode | None:
        if self.is_empty():
            return None
        temp = self.head
        self.head = temp.next
 
        if(self.head == None):
            self.rear = None
        return temp

    def __str__(self) -> str:
        output = ""
        temp = self.rear
        while temp != None:
            output += str(temp)
            temp = temp.next
        return output

    def __repr__(self) -> str:
        return self.__str__()

    