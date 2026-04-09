import sqlite3

DB = "instance/data.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        note TEXT,
        last_time INTEGER,
        seen_time INTEGER
    )
    """)

    conn.commit()
    conn.close()

def get_orders():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM orders")
    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "code": r[1],
            "note": r[2],
            "last_time": r[3],
            "seen_time": r[4]
        } for r in rows
    ]

def add_order(code, note):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO orders (code, note) VALUES (?, ?)", (code, note))
    conn.commit()
    conn.close()

def delete_order(id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM orders WHERE id=?", (id,))
    conn.commit()
    conn.close()

def update_time(id, last_time, seen_time):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        UPDATE orders
        SET last_time=?, seen_time=?
        WHERE id=?
    """, (last_time, seen_time, id))
    conn.commit()
    conn.close()
