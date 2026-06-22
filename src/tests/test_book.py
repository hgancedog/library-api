import pytest

from app.models import Book, BookError


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


def test_book_created_with_other_valid_data():
    book = Book(title="Foundation", author="Asimov")
    assert book.title == "Foundation"
    assert book.author == "Asimov"
    assert book.is_available is True


def test_available_book_can_be_loaned():
    book = Book(title="Meditations", author="Marcus Aurelius")
    assert book.can_be_loaned() is True
