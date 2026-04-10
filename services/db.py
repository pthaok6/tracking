import sqlite3
import os

DB_PATH = "/data/app.db"

def get_conn():
    os.makedirs("/data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        note TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE
    )
    """)

    conn.commit()
    conn.close()


# ======================
# ORDERS
# ======================
def add_order(code, note):
    conn = get_conn()
    conn.execute(
        "INSERT INTO orders (code, note) VALUES (?, ?)",
        (code, note)
    )
    conn.commit()
    conn.close()


def get_orders():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_order(order_id):
    conn = get_conn()
    conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


# ======================
# USERS
# ======================
def add_user(user_id):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
    conn.close()def add_order(code, note):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (code, note) VALUES (%s, %s)",
        (code, note)
    )
    conn.commit()
    conn.close()


def get_orders():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


def delete_order(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))
    conn.commit()
    conn.close()# ORDERS
# ======================
def add_order(code, note):
    conn = get_conn()
    conn.execute(
        "INSERT INTO orders (code, note) VALUES (?, ?)",
        (code, note)
    )
    conn.commit()
    conn.close()


def get_orders():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM orders").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_order(order_id):
    conn = get_conn()
    conn.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


# ======================
# USERS
# ======================
def add_user(user_id):
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    )
    conn.commit()
    conn.close()
