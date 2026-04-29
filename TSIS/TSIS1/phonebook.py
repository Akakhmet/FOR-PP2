import csv
import json
import os
from connect import connect

PAGE_SIZE = 5


def run_sql(sql, params=(), fetch=False):
    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                if fetch:
                    return cur.fetchall()
    finally:
        conn.close()
    return []


def apply_schema():
    """Apply schema.sql and procedures.sql once."""
    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                for fname in ("schema.sql", "procedures.sql"):
                    path = os.path.join(os.path.dirname(__file__), fname)
                    with open(path, encoding="utf-8") as f:
                        cur.execute(f.read())
        print("[OK] Schema and procedures applied.")
    finally:
        conn.close()


def print_contacts(rows):
    if not rows:
        print("  (no results)")
        return
    print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10} {'Phones'}")
    print("-" * 90)
    for r in rows:
        cid, name, email, bday, grp, phones = r
        print(f"{cid:<5} {str(name):<20} {str(email or ''):<25} "
              f"{str(bday or ''):<12} {str(grp or ''):<10} {phones or ''}")



def get_full_contacts(where="", params=(), order_by="c.name", limit=None, offset=None):
    """Return contacts joined with phones and groups."""
    limit_clause  = f"LIMIT {limit}"   if limit  is not None else ""
    offset_clause = f"OFFSET {offset}" if offset is not None else ""
    sql = f"""
        SELECT
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name  AS grp,
            STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups  g ON g.id = c.group_id
        LEFT JOIN phones  p ON p.contact_id = c.id
        {where}
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY {order_by}
        {limit_clause} {offset_clause}
    """
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()



def filter_by_group():
    groups = run_sql("SELECT id, name FROM groups ORDER BY name", fetch=True)
    if not groups:
        print("No groups found.")
        return
    print("\nGroups:")
    for gid, gname in groups:
        print(f"  {gid}. {gname}")
    choice = input("Enter group id: ").strip()
    if not choice.isdigit():
        print("Invalid input.")
        return
    rows = get_full_contacts(where="WHERE c.group_id = %s", params=(int(choice),))
    print_contacts(rows)
 

def search_by_email():
    query = input("Enter email fragment: ").strip()
    rows = get_full_contacts(where="WHERE c.email ILIKE %s", params=(f"%{query}%",))
    print_contacts(rows)

def sort_contacts():
    print("Sort by: 1) Name  2) Birthday  3) Date added")
    choice = input("Choice: ").strip()
    order = {"1": "c.name", "2": "c.birthday", "3": "c.created_at"}.get(choice, "c.name")
    rows = get_full_contacts(order_by=order)
    print_contacts(rows)


def paginated_browse():
    """Console loop using LIMIT/OFFSET."""
    page = 0
    while True:
        rows = get_full_contacts(limit=PAGE_SIZE, offset=page * PAGE_SIZE)
        print(f"\n--- Page {page + 1} ---")
        print_contacts(rows)
        cmd = input("  [n]ext / [p]rev / [q]uit: ").strip().lower()
        if cmd == "n":
            if len(rows) == PAGE_SIZE:
                page += 1
            else:
                print("Already on last page.")
        elif cmd == "p":
            if page > 0:
                page -= 1
            else:
                print("Already on first page.")
        elif cmd == "q":
            break
        
def delete_contact():
    name = input("Enter name to delete: ").strip()
    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM contacts WHERE name = %s", (name,))
        print(f"[OK] Deleted: {name}")
    finally:
        conn.close()
        
def update_contact():
    name = input("Enter name to update: ").strip()
    new_email = input("New email: ").strip() or None
    new_birthday = input("New birthday: ").strip() or None

    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE contacts SET email=%s, birthday=%s WHERE name=%s",
                    (new_email, new_birthday, name)
                )
        print(f"[OK] Updated: {name}")
    finally:
        conn.close()
        
def _upsert_contact(conn, name, email, birthday, group_name):
    with conn.cursor() as cur:
        group_id = None

        # group болса — create немесе алу
        if group_name:
            cur.execute(
                "INSERT INTO groups (name) VALUES (%s) ON CONFLICT DO NOTHING",
                (group_name,)
            )
            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
            row = cur.fetchone()
            if row:
                group_id = row[0]

        #проверка есть ли контакт
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        existing = cur.fetchone()

        if existing:
            return existing[0], True

        # жаңа контакт қосу
        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s,%s,%s,%s) RETURNING id",
            (name, email, birthday, group_id),
        )

        return cur.fetchone()[0], False
 


def extended_search():
    """Calls the search_contacts DB function (covers name, email, phones)."""
    query = input("Search (name / email / phone): ").strip()
    conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            rows = cur.fetchall()
    finally:
        conn.close()
    if not rows:
        print("  (no results)")
        return
    print(f"\n{'ID':<5} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group'}")
    print("-" * 75)
    for r in rows:
        print(f"{r[0]:<5} {str(r[1]):<20} {str(r[2] or ''):<25} {str(r[3] or ''):<12} {r[4] or ''}")


import os

def import_csv():
    """Extended CSV import (handles email, birthday, group, phone_type)."""
    path = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    
    
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, path)

    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    conn = connect()
    if conn is None:
        print("No DB connection")
        return

    count = 0
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name  = row.get("name", "").strip()
                if not name:
                    continue

                email    = row.get("email", "").strip() or None
                birthday = row.get("birthday", "").strip() or None
                group    = row.get("group", "").strip() or None
                phone    = row.get("phone", "").strip()
                ptype    = row.get("phone_type", "mobile").strip()

                with conn:
                    cid, _ = _upsert_contact(conn, name, email, birthday, group)
                    if phone:
                        with conn.cursor() as cur:
                            cur.execute(
                                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                                (cid, phone, ptype),
                            )
                count += 1
    finally:
        conn.close()

    print(f"[OK] {count} rows imported from contacts.csv")



def add_phone_ui():
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type (home/work/mobile) [mobile]: ").strip() or "mobile"
    conn  = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        print("[OK] Phone added.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()


def move_to_group_ui():
    name  = input("Contact name: ").strip()
    group = input("Group name: ").strip()
    conn  = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s)", (name, group))
        print("[OK] Contact moved.")
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        conn.close()
        
def add_contact():
    name = input("Name: ").strip()
    email = input("Email: ").strip() or None
    birthday = input("Birthday (YYYY-MM-DD): ").strip() or None
    group = input("Group: ").strip() or None

    conn = connect()
    try:
        with conn:
            cid, _ = _upsert_contact(conn, name, email, birthday, group)
        print(f"[OK] Contact added: {name}")
    finally:
        conn.close()



MENU = """

      PhoneBook               
  1. Browse (paginated)       
  2. Filter by group          
  3. Search by email          
  4. Sort contacts            
  5. Extended search          
  6. Add phone to contact     
  7. Move contact to group          
  8. Import from CSV    
  9. Add contact  
  10. Delete contact
  11. Update contact
  0. Exit                     

"""

ACTIONS = {
    "1": paginated_browse,
    "2": filter_by_group,
    "3": search_by_email,
    "4": sort_contacts,
    "5": extended_search,
    "6": add_phone_ui,
    "7": move_to_group_ui,
    "8": import_csv,
    "9": add_contact,
    "10": delete_contact,
    "11": update_contact,
}


def main():
    apply_schema()
    while True:
        print(MENU)
        choice = input("Choice: ").strip()
        if choice == "0":
            print("Bye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
