# --- Code 1: basic __init__ ---

class Person:

    def __init__(self, name):
        self.name = name

p1 = Person("Ali")

print(p1.name)

# --- Code 2: multiple attributes ---

class Student:

    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student("Dana", 18)

print(s1.name)
print(s1.age)

# --- Code 3: multiple objects ---

class Car:

    def __init__(self, brand):
        self.brand = brand

car1 = Car("Toyota")
car2 = Car("BMW")

print(car1.brand)
print(car2.brand)
