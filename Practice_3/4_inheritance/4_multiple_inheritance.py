# --- Code 1: inherit from two classes ---

class Father:

    def drive(self):
        print("Father can drive")

class Mother:

    def cook(self):
        print("Mother can cook")

class Child(Father, Mother):
    pass

c = Child()

c.drive()
c.cook()


# --- Code 2: child adds new ability ---

class Father:

    def skill1(self):
        print("Driving")

class Mother:

    def skill2(self):
        print("Cooking")

class Child(Father, Mother):

    def skill3(self):
        print("Programming")

c = Child()

c.skill1()
c.skill2()
c.skill3()
