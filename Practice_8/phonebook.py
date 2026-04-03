from connect import get_connection


def upsert():
    name = input("Name: ")
    phone = input("Phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))

    conn.commit()
    cur.close()
    conn.close()


def search():
    pattern = input("Search: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def pagination():
    limit = int(input("Limit: "))
    offset = int(input("Offset: "))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def delete():
    value = input("Enter name or phone: ")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("CALL delete_contact(%s)", (value,))

    conn.commit()
    cur.close()
    conn.close()


def menu():
    while True:
        print("\n1. Add/Update")
        print("2. Search")
        print("3. Pagination")
        print("4. Delete")
        print("5. Exit")

        choice = input("Choose: ")

        if choice == "1":
            upsert()
        elif choice == "2":
            search()
        elif choice == "3":
            pagination()
        elif choice == "4":
            delete()
        elif choice == "5":
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()