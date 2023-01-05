class HashTableNode:
    def __init__(self, key: any, value: any):
        self.key = key
        self.value = value
        self.next = None

    def __str__(self):
        return "<Node: (%s, %s), next: %s>" % (self.key, self.value, self.next != None)

    def __repr__(self):
	    return str(self)

class HashTable:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.size = 0
        self.buckets: list[HashTableNode | None] = [None] * self.capacity  # empty buckets (e.g. LLs)

    def insert(self, key: any, value: any):
        self.size += 1
        index = self.hash(key)
        node = self.buckets[index]
        if node is None:
            self.buckets[index] = HashTableNode(key, value)
            return
        prev = node
        while node is not None:
            prev = node
            node = node.next
        prev.next = HashTableNode(key, value)

    def find(self, key: any):
        index = self.hash(key)
        node = self.buckets[index]
        while node is not None and node.key != key:
            node = node.next

        if node is None:
            return None
        return node.value

    def hash(self, key):
        hashsum = 0
        for idx, c in enumerate(key):
            # Add (index + length of key) ^ (current char code)
            hashsum += (idx + len(key)) ** ord(c)
            # Perform modulus to keep hashsum in range [0, self.capacity - 1]
            hashsum = hashsum % self.capacity
        return hashsum