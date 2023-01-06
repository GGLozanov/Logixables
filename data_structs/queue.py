class QueueNode:
    def __init__(self, data):
        self.data = data
        self.next = None

    def __str__(self) -> str:
        return f"{self.data}" + ("<-" if self.next != None else "")

    def __repr__(self) -> str:
        return self.__str__()
 
class Queue: 
    def __init__(self, front: QueueNode | None = None):
        self.rear = self.front = front
        self.size = 0
 
    def dequeue(self) -> QueueNode:
        if self.front is None:
            print('Queue Underflow')
            exit(-1)
 
        temp = self.front
        self.front = self.front.next
 
        if self.front is None:
            self.rear = None
 
        self.size -= 1
 
        return temp
 
    def enqueue(self, node: QueueNode):
        if self.front is None:
            self.front = node
            self.rear = node
        else:
            self.rear.next = node
            self.rear = node
 
        self.size += 1

    def is_empty(self):
        return self.rear is None and self.front is None

    def __str__(self) -> str:
        output = ""
        temp = self.front
        while temp != None:
            output += str(temp)
            temp = temp.next
        return output

    def __repr__(self) -> str:
        return self.__str__()

    