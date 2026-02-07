# --- Code 1: class variable shared by all objects ---

class Student:

    school = "KBTU"   # class variable

s1 = Student()
s2 = Student()

print(s1.school)
print(s2.school)

# --- Code 2: class and instance variables ---

class Student:

    school = "KBTU"

    def __init__(self, name):
        self.name = name   # instance variable

s1 = Student("Ali")
s2 = Student("Dana")

print(s1.name, s1.school)
print(s2.name, s2.school)

# --- Code 3: modify class variable ---

class Student:

    school = "KBTU"

s1 = Student()
s2 = Student()

Student.school = "NU"

print(s1.school)
print(s2.school)
