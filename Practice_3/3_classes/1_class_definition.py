# --- Code 1: simple class ---

class Person:
    pass

# create object
p1 = Person()

print(p1)

# --- Code 2: class with variable ---

class Animal:
    species = "Dog"

a1 = Animal()

print(a1.species)


# --- Code 3: multiple objects ---

class Car:
    brand = "Toyota"

car1 = Car()
car2 = Car()

print(car1.brand)
print(car2.brand)
