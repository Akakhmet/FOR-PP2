# --- Code 1: basic inheritance ---

class Animal:

    def speak(self):
        print("Animal makes a sound")

class Dog(Animal):
    pass

d = Dog()

d.speak()


# --- Code 2: child adds method ---

class Animal:

    def speak(self):
        print("Animal sound")

class Cat(Animal):

    def meow(self):
        print("Meow")

c = Cat()

c.speak()
c.meow()

# --- Code 3: inheritance with constructor ---

class Person:

    def __init__(self, name):
        self.name = name

class Student(Person):
    pass

s = Student("Ali")

print(s.name)
