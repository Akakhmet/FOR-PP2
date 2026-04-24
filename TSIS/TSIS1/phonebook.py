"""
PhoneBook — TSIS 1  (Extended Contact Management)
Requires: psycopg2-binary
"""

import csv
import json
import sys
from datetime import date, datetime

import psycopg2
from connect import get_connection, init_db
from config import PAGE_SIZE

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _row_to_dict(row, cur):
    """Convert a cursor row to a dict using column names."""
    cols = [d.name for d in cur.description]
    return dict(zip(cols, row))


def _print_contact(d: dict):
    name = d["first_name"] + (" " + d["last_name"] if d.get("last_name") else "")
    print(f"  [{d['id']}] {name}")
    if d.get("email"):
        print(f"       email   : {d['email']}")
    if d.get("birthday"):
        print(f"       birthday: {d['birthday']}")
    if d.get("group_name"):
        print(f"       group   : {d['group_name']}")
    if d.get("phones_agg"):
        print(f"       phones  : {d['phones_agg']}")


def _input_or_none(prompt: str):
    val = input(prompt).strip()
    return val if val else None


def _parse_date(s: str):
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    print(f"  [!] Cannot parse date '{s}'. Use YYYY-MM-DD.")
    return None


# ─── Group helpers ────────────────────────────────────────────────────────────

def _get_or_create_group(cur, name: str) -> int | None:
    if not name:
        return None
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s LIMIT 1", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]


def list_groups(cur) -> list[dict]:
    cur.execute("SELECT id, name FROM groups ORDER BY name")
    return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]


# ─── 3.2 Console Search & Filter ─────────────────────────────────────────────

def filter_by_group():
    """Show contacts belonging to a chosen group."""
    conn = get_connection()
    cur = conn.cursor()
    groups = list_groups(cur)
    print("\n── Groups ──")
    for g in groups:
        print(f"  {g['id']}. {g['name']}")
    choice = input("Enter group id or name: ").strip()
    # resolve
    if choice.isdigit():
        cur.execute("SELECT id, name FROM groups WHERE id = %s", (int(choice),))
    else:
        cur.execute("SELECT id, name FROM groups WHERE name ILIKE %s", (choice,))
    row = cur.fetchone()
    if not row:
        print("[!] Group not found.")
        cur.close(); conn.close(); return

    gid, gname = row
    cur.execute(
        """
        SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
               %s AS group_name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones_agg
        FROM contacts c
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.group_id = %s
        GROUP BY c.id
        ORDER BY c.first_name
        """,
        (gname, gid),
    )
    rows = cur.fetchall()
    print(f"\n── Contacts in '{gname}' ({len(rows)}) ──")
    for r in rows:
        _print_contact(_row_to_dict(r, cur))
    cur.close(); conn.close()


def search_by_email():
    """Partial email search."""
    query = input("Email pattern (e.g. gmail): ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
               g.name AS group_name,
               STRING_AGG(p.phone || ' (' || COALESCE(p.type,'?') || ')', ', ') AS phones_agg
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE c.email ILIKE %s
        GROUP BY c.id, g.name
        ORDER BY c.first_name
        """,
        (f"%{query}%",),
    )
    rows = cur.fetchall()
    print(f"\n── Email search '{query}' — {len(rows)} result(s) ──")
    for r in rows:
        _print_contact(_row_to_dict(r, cur))
    cur.close(); conn.close()


def search_all_fields():
    """Full search via DB function search_contacts()."""
    query = input("Search query: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()
    print(f"\n── Results for '{query}' — {len(rows)} contact(s) ──")
    for r in rows:
        _print_contact(_row_to_dict(r, cur))
    cur.close(); conn.close()


def paginated_browse():
    """Navigate all contacts page by page using get_contacts_page()."""
    sort_opts = {"1": "first_name", "2": "birthday", "3": "created_at"}
    print("\nSort by: 1) Name  2) Birthday  3) Date added")
    sort_key = sort_opts.get(input("Choice [1]: ").strip() or "1", "first_name")

    offset = 0
    while True:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM get_contacts_page(%s, %s, %s)",
                    (sort_key, PAGE_SIZE, offset))
        rows = cur.fetchall()
        cur.close(); conn.close()

        if not rows and offset == 0:
            print("No contacts found.")
            return

        page_num = offset // PAGE_SIZE + 1
        print(f"\n── Page {page_num} (sorted by {sort_key}) ──")
        if not rows:
            print("  [end of list]")
        for r in rows:
            _print_contact(dict(zip(
                ["id","first_name","last_name","email","birthday","group_name","phones_agg"], r
            )))

        cmd = input("\n[n]ext  [p]rev  [q]uit: ").strip().lower()
        if cmd == "n":
            if len(rows) < PAGE_SIZE:
                print("Already on last page.")
            else:
                offset += PAGE_SIZE
        elif cmd == "p":
            offset = max(0, offset - PAGE_SIZE)
        elif cmd == "q":
            break


# ─── 3.3 Import / Export ─────────────────────────────────────────────────────

def export_json():
    """Export all contacts (with phones and group) to contacts_export.json."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.id, c.first_name, c.last_name, c.email,
               c.birthday::text, g.name AS group_name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        ORDER BY c.first_name
        """
    )
    contacts_raw = cur.fetchall()
    result = []
    for row in contacts_raw:
        cid, fn, ln, email, bday, gname = row
        cur.execute(
            "SELECT phone, type FROM phones WHERE contact_id = %s", (cid,)
        )
        phones = [{"phone": p, "type": t} for p, t in cur.fetchall()]
        result.append({
            "first_name": fn,
            "last_name":  ln,
            "email":      email,
            "birthday":   bday,
            "group":      gname,
            "phones":     phones,
        })
    cur.close(); conn.close()

    filename = "contacts_export.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[✓] Exported {len(result)} contacts → {filename}")


def _import_single_contact(cur, contact: dict, overwrite: bool):
    """Insert one contact dict; returns 'inserted', 'updated', or 'skipped'."""
    fn    = contact.get("first_name", "").strip()
    ln    = (contact.get("last_name") or "").strip() or None
    email = (contact.get("email") or "").strip() or None
    bday  = _parse_date(contact.get("birthday") or "")
    gname = (contact.get("group") or "").strip() or None
    phones = contact.get("phones", [])

    if not fn:
        return "skipped"

    # Check duplicate
    cur.execute(
        "SELECT id FROM contacts WHERE first_name ILIKE %s AND "
        "(last_name ILIKE %s OR (last_name IS NULL AND %s IS NULL))",
        (fn, ln, ln),
    )
    existing = cur.fetchone()

    gid = _get_or_create_group(cur, gname)

    if existing:
        if not overwrite:
            return "skipped"
        cid = existing[0]
        cur.execute(
            "UPDATE contacts SET last_name=%s, email=%s, birthday=%s, group_id=%s WHERE id=%s",
            (ln, email, bday, gid, cid),
        )
        cur.execute("DELETE FROM phones WHERE contact_id=%s", (cid,))
        action = "updated"
    else:
        cur.execute(
            "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
            (fn, ln, email, bday, gid),
        )
        cid = cur.fetchone()[0]
        action = "inserted"

    for p in phones:
        pnum  = (p.get("phone") or "").strip()
        ptype = (p.get("type") or "mobile").strip()
        if ptype not in ("home", "work", "mobile"):
            ptype = "mobile"
        if pnum:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                (cid, pnum, ptype),
            )
    return action


def import_json():
    """Import contacts from a JSON file with duplicate handling."""
    filename = input("JSON file path [contacts_export.json]: ").strip() or "contacts_export.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[!] File not found: {filename}")
        return
    except json.JSONDecodeError as e:
        print(f"[!] Invalid JSON: {e}")
        return

    print(f"Found {len(data)} contacts in file.")
    policy = input("On duplicate — [s]kip or [o]verwrite? [s]: ").strip().lower() or "s"
    overwrite = policy == "o"

    conn = get_connection()
    cur = conn.cursor()
    counts = {"inserted": 0, "updated": 0, "skipped": 0}
    for contact in data:
        action = _import_single_contact(cur, contact, overwrite)
        counts[action] += 1
    conn.commit()
    cur.close(); conn.close()
    print(f"[✓] Done — inserted:{counts['inserted']}  updated:{counts['updated']}  skipped:{counts['skipped']}")


def import_csv():
    """
    Extended CSV import supporting new fields.
    Expected columns (order-independent, header row required):
    first_name, last_name, email, birthday, group, phone, phone_type
    """
    filename = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    try:
        with open(filename, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"[!] File not found: {filename}")
        return

    conn = get_connection()
    cur = conn.cursor()
    ok = err = 0
    for row in rows:
        fn = (row.get("first_name") or "").strip()
        if not fn:
            err += 1; continue
        ln    = (row.get("last_name") or "").strip() or None
        email = (row.get("email") or "").strip() or None
        bday  = _parse_date((row.get("birthday") or "").strip())
        gname = (row.get("group") or "").strip() or None
        phone = (row.get("phone") or "").strip() or None
        ptype = (row.get("phone_type") or "mobile").strip()
        if ptype not in ("home", "work", "mobile"):
            ptype = "mobile"

        gid = _get_or_create_group(cur, gname)

        cur.execute(
            "SELECT id FROM contacts WHERE first_name ILIKE %s AND "
            "(last_name ILIKE %s OR (last_name IS NULL AND %s IS NULL))",
            (fn, ln, ln),
        )
        existing = cur.fetchone()
        if existing:
            cid = existing[0]
            cur.execute(
                "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                (email, bday, gid, cid),
            )
        else:
            cur.execute(
                "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
                "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (fn, ln, email, bday, gid),
            )
            cid = cur.fetchone()[0]

        if phone:
            cur.execute(
                "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                (cid, phone, ptype),
            )
        ok += 1

    conn.commit()
    cur.close(); conn.close()
    print(f"[✓] CSV import done — {ok} processed, {err} skipped.")


# ─── 3.4 Stored-Procedure wrappers ───────────────────────────────────────────

def add_phone_ui():
    """Call the add_phone stored procedure."""
    name  = input("Contact name: ").strip()
    phone = input("Phone number: ").strip()
    ptype = input("Type [mobile/home/work] (default mobile): ").strip() or "mobile"
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("[✓] Phone added.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[!] {e.pgerror or e}")
    finally:
        cur.close(); conn.close()


def move_to_group_ui():
    """Call the move_to_group stored procedure."""
    name  = input("Contact name: ").strip()
    group = input("Group name  : ").strip()
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print("[✓] Contact moved.")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"[!] {e.pgerror or e}")
    finally:
        cur.close(); conn.close()


# ─── Add / Edit contact (basic CRUD) ─────────────────────────────────────────

def add_contact():
    print("\n── Add Contact ──")
    fn    = input("First name: ").strip()
    if not fn:
        print("[!] First name is required."); return
    ln    = _input_or_none("Last name  : ")
    email = _input_or_none("Email      : ")
    bday  = _parse_date(input("Birthday   (YYYY-MM-DD, blank to skip): ").strip())
    gname = _input_or_none("Group      (Family/Work/Friend/Other): ")

    conn = get_connection()
    cur = conn.cursor()
    gid = _get_or_create_group(cur, gname)
    cur.execute(
        "INSERT INTO contacts (first_name, last_name, email, birthday, group_id) "
        "VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (fn, ln, email, bday, gid),
    )
    cid = cur.fetchone()[0]

    # Phones
    while True:
        ph = _input_or_none("Phone number (blank to stop): ")
        if not ph:
            break
        pt = input("  Type [mobile/home/work]: ").strip() or "mobile"
        if pt not in ("home", "work", "mobile"):
            pt = "mobile"
        cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)", (cid, ph, pt))

    conn.commit()
    cur.close(); conn.close()
    print(f"[✓] Contact '{fn}' added (id={cid}).")


def delete_contact():
    name = input("First name (or full name) to delete: ").strip()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM contacts WHERE first_name ILIKE %s OR "
        "(first_name || ' ' || COALESCE(last_name,'')) ILIKE %s "
        "RETURNING id, first_name",
        (name, name),
    )
    deleted = cur.fetchall()
    conn.commit()
    cur.close(); conn.close()
    if deleted:
        for d in deleted:
            print(f"[✓] Deleted: id={d[0]}  name={d[1]}")
    else:
        print("[!] No contact found.")


# ─── Main menu ────────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════╗
║       PhoneBook — TSIS 1             ║
╠══════════════════════════════════════╣
║  1. Browse (paginated + sort)        ║
║  2. Search (all fields)              ║
║  3. Filter by group                  ║
║  4. Search by email                  ║
╠══════════════════════════════════════╣
║  5. Add contact                      ║
║  6. Delete contact                   ║
║  7. Add phone to contact             ║
║  8. Move contact to group            ║
╠══════════════════════════════════════╣
║  9. Export → JSON                    ║
║ 10. Import ← JSON                    ║
║ 11. Import ← CSV                     ║
╠══════════════════════════════════════╣
║  0. Exit                             ║
╚══════════════════════════════════════╝
"""

ACTIONS = {
    "1": paginated_browse,
    "2": search_all_fields,
    "3": filter_by_group,
    "4": search_by_email,
    "5": add_contact,
    "6": delete_contact,
    "7": add_phone_ui,
    "8": move_to_group_ui,
    "9": export_json,
    "10": import_json,
    "11": import_csv,
}


def main():
    print("Initialising database…")
    try:
        init_db()
    except Exception as e:
        print(f"[!] DB init failed: {e}")
        sys.exit(1)

    while True:
        print(MENU)
        choice = input("Choice: ").strip()
        if choice == "0":
            print("Bye!"); break
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"[ERROR] {e}")
        else:
            print("[!] Unknown option.")


if __name__ == "__main__":
    main()