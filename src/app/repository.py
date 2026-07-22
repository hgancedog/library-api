from typing import Protocol

from app.models import Book, BookID, BookNotFoundError


class LibraryRepository(Protocol):
    def add_book(self, book: Book) -> BookID: ...
    def get_book(self, book_id: BookID) -> Book: ...
    def get_all_books(self) -> dict[BookID, Book]: ...


class InMemoryRepository:
    def __init__(self):
        self._db_books: dict[BookID, Book] = {}
        self._next_id: BookID = 1

    def add_book(self, book: Book) -> BookID:
        book.book_id = self._next_id
        self._db_books[book.book_id] = book
        self._next_id += 1
        return book.book_id

    def get_book(self, book_id: BookID) -> Book:
        if book_id not in self._db_books:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        return self._db_books[book_id]

    def get_all_books(self) -> dict[BookID, Book]:
        return dict(self._db_books)


_: LibraryRepository = InMemoryRepository()
