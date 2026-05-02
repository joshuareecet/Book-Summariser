from __future__ import annotations

import re
from enum import IntEnum
from pathlib import Path

from config import load_config
from core import Book, Bookshelf
from database import Database
from summariser import get_summary, summarise_book
from ui import get_file_path, get_int

_BANNER = r"""
  ___           _     ___                           _
 | _ ) ___  ___| |__ / __|_  _ _ __  _ __  __ _ _ _(_)___ ___ _ _
 | _ \/ _ \/ _ \ / / \__ \ || | '  \| '  \/ _` | '_| (_-</ -_) '_|
 |___/\___/\___/_\_\ |___/\_,_|_|_|_|_|_|_\__,_|_| |_/__/\___|_|
"""


class BookType(IntEnum):
    NON_FICTION = 1
    FICTION = 2


class SummaryScope(IntEnum):
    WHOLE_BOOK = 1
    SINGLE_CHAPTER = 2


class App:
    def __init__(self) -> None:
        self._config = load_config()
        self._db = Database()
        self._shelf = Bookshelf(self._db)

    def run(self) -> None:
        print(_BANNER)
        try:
            while True:
                self._main_menu()
        except KeyboardInterrupt:
            return

    # ── Menus ─────────────────────────────────────────────────────────────────

    def _main_menu(self) -> None:
        mode = get_int(
            "\nSelect a mode:\n"
            "  1. Upload a book\n"
            "  2. Summarise from library\n"
            "  3. Remove a book\n"
            "> ",
            min_val=0,
            max_val=4,
        )
        if mode == 1:
            self._upload_book()
        elif mode == 2:
            self._pick_and_summarise()
        elif mode == 3:
            self._remove_book()

    # ── Book management ───────────────────────────────────────────────────────

    def _upload_book(self) -> None:
        try:
            path = get_file_path()
        except KeyboardInterrupt:
            print("Cancelled.")
            return
        self._shelf.add_book(path)

    def _remove_book(self) -> None:
        if not self._shelf.books:
            print("Library is empty.")
            return
        self._shelf.list_books()
        idx = get_int(
            "Enter book number to remove (0 to cancel): ",
            min_val=-1,
            max_val=len(self._shelf) + 1,
        )
        if idx == 0:
            return
        book = self._shelf.get_book(idx - 1)
        self._shelf.remove_book(book)
        print(f'Removed "{book.title}".')

    # ── Summarisation ─────────────────────────────────────────────────────────

    def _pick_and_summarise(self) -> None:
        if not self._shelf.books:
            print("Library is empty. Upload a book first.")
            return
        self._shelf.list_books()
        idx = get_int(
            "Enter book number to summarise: ",
            min_val=0,
            max_val=len(self._shelf) + 1,
        )
        self._summarise_flow(self._shelf.get_book(idx - 1))

    def _summarise_flow(self, book: Book) -> None:
        scope = SummaryScope(
            get_int(
                "Summarise:\n  1. Whole book\n  2. Single chapter\n> ",
                min_val=0,
                max_val=3,
            )
        )
        book_type = BookType(
            get_int(
                "Book type:\n  1. Non-fiction\n  2. Fiction\n> ",
                min_val=0,
                max_val=3,
            )
        )

        p = self._config.prompts
        if book_type == BookType.NON_FICTION:
            chunk_prompt = p.get("chunk_non_fiction", "")
            combine_prompt = p.get("combine_chunk_non_fiction", "")
            chapter_prompt = p.get("query_non_fiction", "")
        else:
            chunk_prompt = p.get("chunk_fiction", "")
            combine_prompt = p.get("combine_chunk_fiction", "")
            chapter_prompt = p.get("query_fiction", "")

        flags = self._ask_for_flags()
        flag_suffix = f"\nAdditional instructions: {flags}\n" if flags else ""

        if scope == SummaryScope.WHOLE_BOOK:
            result = summarise_book(book, chunk_prompt + flag_suffix, combine_prompt, self._config)
            self._save_summary(book, result)
        else:
            self._summarise_one_chapter(book, chapter_prompt + flag_suffix)

    def _ask_for_flags(self) -> str:
        choice = get_int(
            "Add custom instructions to the prompt?\n  1. Yes\n  2. No\n> ",
            min_val=0,
            max_val=3,
        )
        return input("Enter custom instructions: ").strip() if choice == 1 else ""

    def _summarise_one_chapter(self, book: Book, prompt: str) -> None:
        for title in book.chapter_titles():
            print(f"  {title}")
        idx = get_int(
            "Enter chapter number: ",
            min_val=-1,
            max_val=book.length,
        )
        result = get_summary(book.chapter_text(idx), prompt, self._config)
        print("\n" + result)

    def _save_summary(self, book: Book, summary: str) -> None:
        safe_title = re.sub(r"[^\w\s-]", "", book.title).strip()
        path = Path(f"Book Summary {safe_title}.txt")
        path.write_text(summary, encoding="utf-8")
        print("\n" + summary)
        print(f'\nSummary saved to "{path}".')


if __name__ == "__main__":
    App().run()

