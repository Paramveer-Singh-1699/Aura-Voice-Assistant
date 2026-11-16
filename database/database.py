import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "aura.db"


def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def initialize():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)


def add_note(content):
    with connect() as con:
        cur = con.execute(
            "INSERT INTO notes(content, created_at) VALUES (?, ?)",
            (content, datetime.now().isoformat(timespec="seconds"))
        )
        return cur.lastrowid


def get_notes(limit=20):
    with connect() as con:
        return con.execute(
            "SELECT id, content, created_at FROM notes ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()


def delete_note(note_id):
    with connect() as con:
        cur = con.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cur.rowcount > 0


def add_reminder(content, remind_at):
    with connect() as con:
        cur = con.execute(
            "INSERT INTO reminders(content, remind_at) VALUES (?, ?)",
            (content, remind_at)
        )
        return cur.lastrowid


def get_due_reminders(now_iso):
    with connect() as con:
        rows = con.execute(
            """SELECT id, content, remind_at FROM reminders
               WHERE completed = 0 AND remind_at <= ? ORDER BY remind_at""",
            (now_iso,)
        ).fetchall()
        if rows:
            con.executemany(
                "UPDATE reminders SET completed = 1 WHERE id = ?",
                [(row["id"],) for row in rows]
            )
        return rows


def get_pending_reminders():
    with connect() as con:
        return con.execute(
            """SELECT id, content, remind_at FROM reminders
               WHERE completed = 0 ORDER BY remind_at LIMIT 20"""
        ).fetchall()
