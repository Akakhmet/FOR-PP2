# --- Code 1: child overrides parent method ---

class Animal:

    def speak(self):
        print("Animal sound")

class Dog(Animal):

    def speak(self):
        print("Dog barks")

d = Dog()

d.speak()


# --- Code 2: different classes override differently ---

class Animal:

    def speak(self):
        print("Animal sound")

class Cat(Animal):

    def speak(self):
        print("Cat meows")

class Cow(Animal):

    def speak(self):
        print("Cow moos")

c = Cat()
w = Cow()

c.speak()
w.speak()
