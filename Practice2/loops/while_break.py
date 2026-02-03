
secret = 7

while True:
    guess = int(input("Guess number: "))

    if guess == secret:
        print("Correct!")
        break

    print("Wrong, try again")
