class StackNode:
    def __init__(self, value) -> None:
        self.value = value
        self.next = None
        self.prev = None

class Stack:
    def __init__(self, head: StackNode, size: int) -> None:
        self.head = head
        self.size = size

    def push(self, node: StackNode):
        temp = self.head
        node.next = temp.next
        self.head.next = node
        node.prev = temp
        self.size += 1

    def pop(self) -> StackNode:
        if size <= 0:
            raise Exception("Cannot pop a stack with no elements!")
        size -= 1
        self.head = 
        