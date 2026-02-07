# --- Code 1: super() calls parent constructor ---

class Person:

    def __init__(self, name):
        self.name = name

class Student(Person):

    def __init__(self, name, grade):
        super().__init__(name)   # call parent __init__
        self.grade = grade

s = Student("Ali", 5)

print(s.name)
print(s.grade)

# --- Code 2: super() calls parent method ---

class Animal:

    def speak(self):
        print("Animal sound")

class Dog(Animal):

    def speak(self):
        super().speak()
        print("Dog barks")

d = Dog()

d.speak()
