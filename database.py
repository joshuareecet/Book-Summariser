from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

_DB_PATH = Path(__file__).parent / "bookshelf.db"

# NOTE: If upgrading from an older version of this project, the existing
# bookshelf.db will retain its original schema (no PRIMARY KEY). It will
# still work correctly; the `book_exists()` guard prevents duplicate inserts.
_CREATE_TABLE = (
    "CREATE TABLE IF NOT EXISTS bookshelf "
    "(id TEXT PRIMARY KEY, path TEXT, title TEXT, author TEXT, language TEXT, length INTEGER)"
)


class Database:
    """Handles all SQLite persistence for the bookshelf."""

    def __init__(self, db_path: Path = _DB_PATH) -> None:
        self._con = sqlite3.connect(db_path)
        self._cur = self._con.cursor()
        self._cur.execute(_CREATE_TABLE)
        self._con.commit()

    def get_all_books(self) -> list[tuple]:
        return self._cur.execute("SELECT * FROM bookshelf").fetchall()

    def add_book(self, record: list[Any]) -> None:
        self._cur.execute(
            "INSERT OR IGNORE INTO bookshelf VALUES(?, ?, ?, ?, ?, ?)", record
        )
        self._con.commit()

    def remove_book(self, book_id: str) -> None:
        self._cur.execute("DELETE FROM bookshelf WHERE id=?", (book_id,))
        self._con.commit()

    def book_exists(self, book_id: str) -> bool:
        return (
            self._cur.execute(
                "SELECT 1 FROM bookshelf WHERE id=?", (book_id,)
            ).fetchone()
            is not None
        )

    def close(self) -> None:
        self._con.close()
