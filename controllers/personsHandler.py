from models import classes

class PersonHandler:
    def __init__(self):
        self.persons = classes.Queue()
    
    def add_person(self, name):
        if name:
            person = classes.Person(name)
            self.persons.enqueue(person)
            return person
        return None
    
    def show_next_person(self):
        return self.persons.peek()
    
    def serve_person(self):
        return self.persons.dequeue()
    
    def get_queue(self):
        return list(self.persons.items)