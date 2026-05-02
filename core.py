from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from rapidfuzz import fuzz

from database import Database

_EBOOKS_DIR = Path(__file__).parent / "ebooks"
_MIN_CHAPTER_CHARS = 2000



class Book:
    """Represents an ebook. Content is loaded lazily on first access."""

    def __init__(
        self,
        file_path: str | Path,
        *,
        book_id: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        lang: Optional[str] = None,
        length: Optional[int] = None,
    ) -> None:
        self._path = Path(file_path)
        self._epub: Optional[ebooklib.epub.EpubBook] = None
        self._chapter_titles: list[str] = []
        self._chapter_texts: list[str] = []
        self._length: int = length or 0

        if book_id is not None:
            # Reconstructed from the database — trust the stored metadata
            self._id: str = book_id
            self._title: str = title or "Unknown Title"
            self._author: str | list[str] = author or "Unknown Author"
            self._language: str = lang or "Unknown Language"
        else:
            # New book — read metadata directly from the epub file
            self._open_epub()
            self._id = self._meta("identifier") or str(self._path.stem)
            self._title = self._meta("title") or "Unknown Title"
            self._author = self._all_meta("author") or "Unknown Author"
            self._language = self._meta("language") or "Unknown Language"

    # ── Private helpers ───────────────────────────────────────────────────────

    def _open_epub(self) -> None:
        if self._epub is None:
            if not self._path.exists():
                raise FileNotFoundError(f"Ebook file not found: {self._path}")
            self._epub = epub.read_epub(self._path)

    def _meta(self, key: str) -> Optional[str]:
        self._open_epub()
        items = self._epub.get_metadata("DC", key)
        return items[0][0] if items else None

    def _all_meta(self, key: str) -> list[str]:
        self._open_epub()
        return [str(item[0]) for item in self._epub.get_metadata("DC", key)]

    def _ensure_content(self) -> None:
        """Parses chapters from the epub. No-op if already done."""
        if self._chapter_texts:
            return
        self._open_epub()
        chapters_html: list[bytes] = []
        backup_titles: list[str] = []

        for item in self._epub.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                content = item.get_content()
                if len(content) > _MIN_CHAPTER_CHARS:
                    chapters_html.append(content)
                    backup_titles.append(item.file_name)

        for index, (html, fallback) in enumerate(zip(chapters_html, backup_titles)):
            soup = BeautifulSoup(html, "lxml-xml")
            self._chapter_titles.append(self._parse_title(soup, index, fallback))
            self._chapter_texts.append(soup.get_text())

        self._length = len(self._chapter_texts)

    @staticmethod
    def _parse_title(soup: BeautifulSoup, index: int, fallback: str) -> str:
        for tag_name in ("title", "head", "h1", "h2"):
            tag = soup.find(tag_name)
            if tag:
                if tag.attrs and "title" in tag.attrs:
                    return f"{index}: {tag['title']}"
                if tag.string:
                    return f"{index}: {tag.string}"
        return f"{index}: {fallback}"

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("Title must be a string.")
        self._title = value

    @property
    def author(self) -> str | list[str]:
        return list(self._author) if isinstance(self._author, list) else self._author

    @author.setter
    def author(self, value: str | list[str]) -> None:
        if not isinstance(value, (str, list)):
            raise TypeError("Author must be str or list[str].")
        self._author = value

    @property
    def language(self) -> str:
        return self._language

    @property
    def length(self) -> int:
        if self._length == 0:
            self._ensure_content()
        return self._length
    
    def __len__(self):
        return self.length

    # ── Content accessors ─────────────────────────────────────────────────────

    def chapter_titles(self) -> list[str]:
        self._ensure_content()
        return list(self._chapter_titles)

    def chapter_text(self, index: int) -> str:
        self._ensure_content()
        return self._chapter_texts[index]

    # ── Persistence ───────────────────────────────────────────────────────────

    def to_db_record(self) -> list:
        author = (
            self._author
            if isinstance(self._author, str)
            else ", ".join(self._author)
        )
        return [self._id, str(self._path), self._title, author, self._language, self._length]

    def __repr__(self) -> str:
        return f"Book(title={self._title!r}, author={self._author!r})"


class Bookshelf:
    """A collection of Books backed by a SQLite database."""

    def __init__(self, db: Database) -> None:
        self._db = db
        self._books: list[Book] = []
        self._reload()

    def _reload(self) -> None:
        self._books = []
        for book_id, path, title, author, language, length in self._db.get_all_books():
            self._books.append(
                Book(
                    path,
                    book_id=book_id,
                    title=title,
                    author=author,
                    lang=language,
                    length=length,
                )
            )

    @property
    def books(self) -> list[Book]:
        return list(self._books)

    def add_book(self, path: str | Path) -> Book:
        source = Path(path)
        dest = _EBOOKS_DIR / source.name
        if not dest.exists():
            shutil.copy2(source, dest)

        book = Book(dest)
        if self._db.book_exists(book.id):
            print(f'"{book.title}" is already in your library.')
            return book

        self._db.add_book(book.to_db_record())
        self._books.append(book)
        print(f'Added "{book.title}" to library.')
        return book

    def remove_book(self, book: Book) -> None:
        self._db.remove_book(book.id)
        self._books.remove(book)

    def get_book(self, index: int) -> Book:
        return self._books[index]

    def search_by_title(self, term: str, threshold: int = 80) -> list[tuple[int, Book]]:
        """Returns (index, Book) pairs whose title fuzzy-matches *term*."""
        return [
            (i, b)
            for i, b in enumerate(self._books)
            if fuzz.partial_ratio(b.title.lower(), term.lower()) > threshold
        ]

    def list_books(self) -> None:
        if not self._books:
            print("Your library is empty.")
            return
        print("Library:")
        for i, book in enumerate(self._books, start=1):
            print(f"  {i}. {book.title}")

    def __len__(self) -> int:
        return len(self._books)

    def __iter__(self):
        return iter(self._books)