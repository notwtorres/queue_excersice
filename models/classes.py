from collections import deque

class Queue:
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, elemento):
        self.items.append(elemento)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        return None
    
    def is_empty(self):
        return len(self.items) == 0 
    
    def peek(self):
        if not self.is_empty():
            return self.items[0]
        return None

class Person:
    def __init__(self, name):
        self.name = name
         
    def __str__(self):
        return f"{self.name}"