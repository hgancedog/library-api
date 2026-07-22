import pytest

from app.models import Book, BookID, BookNotFoundError
from app.repository import InMemoryRepository, LibraryRepository


@pytest.fixture
def repo() -> LibraryRepository:
    return InMemoryRepository()


def test_book_is_retrieved_by_id(repo: LibraryRepository):
    book = Book(title="Moby-Dick", author="Herman Melville")

    book_id = repo.add_book(book)
    retrieved = repo.get_book(book_id)

    assert retrieved == book
    assert retrieved.book_id == book_id


def test_book_raises_error_when_not_found(repo: LibraryRepository):
    with pytest.raises(BookNotFoundError):
        repo.get_book(999999)


def test_book_ids_increment(repo: LibraryRepository):
    id_1 = repo.add_book(Book(title="Moby-Dick", author="Herman Melville"))
    id_2 = repo.add_book(Book(title="1984", author="George Orwell"))

    assert id_1 != id_2
    assert id_2 > id_1
    assert repo.get_book(id_1).title == "Moby-Dick"
    assert repo.get_book(id_2).title == "1984"


def test_book_returns_all_books(repo: LibraryRepository):
    book_id_1 = repo.add_book(Book(title="Moby-Dick", author="Herman Melville"))
    book_id_2 = repo.add_book(Book(title="1984", author="George Orwell"))
    books: dict[BookID, Book] = repo.get_all_books()

    assert books[book_id_1].title == "Moby-Dick"
    assert books[book_id_2].title == "1984"
