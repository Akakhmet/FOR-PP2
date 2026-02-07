# --- Code 1: simple method ---

class Person:

    def __init__(self, name):
        self.name = name

    def greet(self):
        print("Hello, my name is", self.name)

p1 = Person("Ali")

p1.greet()


# --- Code 2: method with return ---

class Calculator:

    def add(self, a, b):
        return a + b

calc = Calculator()

result = calc.add(5, 7)

print(result)


# --- Code 3: method modifies object ---

class Counter:

    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

c = Counter()

c.increment()
c.increment()

print(c.count)

