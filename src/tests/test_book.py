import pytest

from app.models import Book, BookAlreadyLoanedError, BookError, BookNotLoanedError


def test_book_requires_title():
    with pytest.raises(BookError):
        Book(title="", author="Julio Verne")


def test_book_requires_author():
    with pytest.raises(BookError):
        Book(title="El Quijote", author="")


def test_book_created_with_valid_data():
    book = Book(title="The Odyssey", author="Homer")
    assert book.title == "The Odyssey"
    assert book.author == "Homer"
    assert book.is_available is True


def test_available_book_can_be_loaned():
    book = Book(title="Meditations", author="Marcus Aurelius")
    assert book.can_be_loaned() is True


def test_loaned_book_cannot_be_loaned():
    book = Book(title="Pride and Prejudice", author="Jane Austen")
    book.mark_as_loaned()
    assert book.can_be_loaned() is False


def test_book_can_be_loaned_again():
    book = Book(title="The Aeneid", author="Virgil")
    book.mark_as_loaned()
    book.mark_as_returned()
    assert book.can_be_loaned() is True


def test_cannot_mark_as_loaned_twice():
    book = Book(title="The Divine Comedy", author="Dante")
    book.mark_as_loaned()
    with pytest.raises(BookAlreadyLoanedError):
        book.mark_as_loaned()


def test_cannot_mark_as_returned_when_available():
    book = Book(title="Don Quixote", author="Miguel de Cervantes")
    with pytest.raises(BookNotLoanedError):
        book.mark_as_returned()
