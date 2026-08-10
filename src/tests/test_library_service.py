"""Tests for LibraryService orchestration layer.

Uses InMemoryRepository (CRUD-only) as a lightweight test double.
The service is tested independently of any real persistence.
"""

import pytest

from app.library_service import LibraryService
from app.models import (
    Book,
    BookAlreadyLoanedError,
    BookNotFoundError,
    BookNotLoanedError,
    Email,
    User,
    UserNotFoundError,
)
from app.repository import InMemoryRepository, LibraryRepository


@pytest.fixture
def repo() -> InMemoryRepository:
    """Return a fresh CRUD-only in-memory repository."""
    return InMemoryRepository()


@pytest.fixture
def service(repo: LibraryRepository) -> LibraryService:
    """Return a service backed by the CRUD-only repo."""
    return LibraryService(repo)


# ── loan_book ────────────────────────────────────────────────────────


def test_loan_book_raises_error_when_book_not_found(
    service: LibraryService,
):
    with pytest.raises(BookNotFoundError):
        service.loan_book(999999, 1)


def test_loan_book_raises_error_when_user_not_found(
    service: LibraryService,
    repo: InMemoryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))

    with pytest.raises(UserNotFoundError):
        service.loan_book(book_id, 999999)


def test_loan_book_raises_error_when_book_already_loaned(
    service: LibraryService,
    repo: InMemoryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="alice", email=Email("alice@example.com")))
    another_user_id = repo.add_user(
        User(username="bob", email=Email("bob@example.com"))
    )
    service.loan_book(book_id, user_id)

    with pytest.raises(BookAlreadyLoanedError):
        service.loan_book(book_id, another_user_id)


def test_loan_book_creates_loan_and_marks_book_as_loaned(
    service: LibraryService,
    repo: InMemoryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="hector", email=Email("hector@example.com")))

    loan_id = service.loan_book(book_id, user_id)

    loan = repo.get_loan(loan_id)
    assert loan.book_id == book_id
    assert loan.user_id == user_id
    assert loan.is_active()

    book = repo.get_book(book_id)
    assert not book.is_available


# ── return_book ──────────────────────────────────────────────────────


def test_return_book_raises_error_when_book_not_found(
    service: LibraryService,
):
    with pytest.raises(BookNotFoundError):
        service.return_book(999999)


def test_return_book_raises_error_when_book_not_loaned(
    service: LibraryService,
    repo: InMemoryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))

    with pytest.raises(BookNotLoanedError):
        service.return_book(book_id)


def test_return_book_marks_book_and_loan_as_returned(
    service: LibraryService,
    repo: InMemoryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="hector", email=Email("hector@example.com")))
    loan_id = service.loan_book(book_id, user_id)

    service.return_book(book_id)

    book = repo.get_book(book_id)
    assert book.is_available

    loan = repo.get_loan(loan_id)
    assert not loan.is_active()
