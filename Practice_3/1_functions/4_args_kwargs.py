# --- Code 1: *args example ---

def sum_numbers(*args):
    total = sum(args)
    print("Sum:", total)

sum_numbers(1, 2, 3)
sum_numbers(5, 10, 15, 20)


# --- Code 2: **kwargs example ---

def show_info(**kwargs):
    print(kwargs)

show_info(name="Ali", age=18)
show_info(city="Almaty", year=2026)

# --- Code 3: *args and **kwargs together ---

def show_all(*args, **kwargs):
    print("Args:", args)
    print("Kwargs:", kwargs)

show_all(1, 2, 3, name="Dana", city="Astana")

