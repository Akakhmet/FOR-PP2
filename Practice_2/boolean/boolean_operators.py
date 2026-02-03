
age = int(input("Age: "))
has_id = input("Has ID? (yes/no): ").lower() == "yes"
is_drunk = input("Drunk? (yes/no): ").lower() == "yes"

can_enter = age >= 18 and has_id and not is_drunk

print("Age OK:", age >= 18)
print("Has ID:", has_id)
print("Not drunk:", not is_drunk)
print("Can enter:", can_enter)
