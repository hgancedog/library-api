from datetime import date

import pytest

from app.models import (
    Book,
    BookID,
    BookNotFoundError,
    BookNotLoanedError,
    Email,
    Loan,
    LoanNotFoundError,
    User,
    UserNotFoundError,
)
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


def test_user_raises_error_when_not_found(repo: LibraryRepository):
    with pytest.raises(UserNotFoundError):
        repo.get_user(999999)


def test_user_is_retrieved_by_id(repo: LibraryRepository):
    user = User(username="hector", email=Email("hector@example.com"))

    user_id = repo.add_user(user)
    retrieved = repo.get_user(user_id)

    assert retrieved == user
    assert retrieved.user_id == user_id


def test_user_ids_increment(repo: LibraryRepository):
    id_1 = repo.add_user(User(username="alice", email=Email("alice@example.com")))
    id_2 = repo.add_user(User(username="bob", email=Email("bob@example.com")))

    assert id_1 != id_2
    assert id_2 > id_1
    assert repo.get_user(id_1).username == "alice"
    assert repo.get_user(id_2).username == "bob"


def test_loan_is_retrieved_by_id(repo: LibraryRepository):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="hector", email=Email("hector@example.com")))

    loan_id = repo.add_loan(Loan(book_id, user_id, date.today()))
    retrieved = repo.get_loan(loan_id)

    assert retrieved.loan_id == loan_id
    assert retrieved.book_id == book_id
    assert retrieved.user_id == user_id


def test_loan_raises_error_when_not_found(repo: LibraryRepository):
    with pytest.raises(LoanNotFoundError):
        repo.get_loan(999999)


def test_loan_ids_increment(repo: LibraryRepository):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="alice", email=Email("alice@example.com")))

    id_1 = repo.add_loan(Loan(book_id=book_id, user_id=user_id, loan_date=date.today()))
    id_2 = repo.add_loan(Loan(book_id=book_id, user_id=user_id, loan_date=date.today()))

    assert id_1 != id_2
    assert id_2 > id_1
    assert repo.get_loan(id_1).loan_id == id_1
    assert repo.get_loan(id_2).loan_id == id_2


def test_loan_get_active_loans_for_user(repo: LibraryRepository):
    book_1_id = repo.add_book(Book(title="1984", author="George Orwell"))
    book_2_id = repo.add_book(Book(title="Dune", author="Frank Herbert"))
    user = User("Hector", Email("hector_gan@gmail.com"))
    user_id = repo.add_user(user)

    loan_1_id = repo.add_loan(Loan(book_1_id, user_id, date.today()))
    loan_2_id = repo.add_loan(Loan(book_2_id, user_id, date.today()))

    loans: list[Loan] = repo.get_active_loans_by_user(user_id)

    assert len(loans) == 2
    returned_ids = [loan.loan_id for loan in loans]
    assert loan_1_id in returned_ids
    assert loan_2_id in returned_ids


def test_loan_get_active_loans_for_user_returns_empty_when_no_loans(
    repo: LibraryRepository,
):
    user = User(username="alice", email=Email("alice@example.com"))
    user_id = repo.add_user(user)

    assert repo.get_active_loans_by_user(user_id) == []


def test_loan_get_active_loans_for_user_excludes_returned(
    repo: LibraryRepository,
):
    book_1_id = repo.add_book(Book(title="1984", author="George Orwell"))
    book_2_id = repo.add_book(Book(title="Dune", author="Frank Herbert"))
    user = User(username="alice", email=Email("alice@example.com"))
    user_id = repo.add_user(user)

    active_loan_id = repo.add_loan(Loan(book_1_id, user_id, date.today()))
    returned_loan_id = repo.add_loan(Loan(book_2_id, user_id, date.today()))
    returned_loan = repo.get_loan(returned_loan_id)
    returned_loan.mark_as_returned()

    loans = repo.get_active_loans_by_user(user_id)

    active_ids = [loan.loan_id for loan in loans]
    assert active_loan_id in active_ids
    assert returned_loan_id not in active_ids


def test_loan_get_active_loan_by_book_returns_none_when_no_loans(
    repo: LibraryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    assert repo.get_active_loan_by_book(book_id) is None


def test_loan_get_active_loan_by_book_returns_none_when_returned(
    repo: LibraryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(
        User(username="hector", email=Email("hectorbarak@mail.com"))
    )
    loan_id = repo.add_loan(Loan(book_id, user_id, date.today()))
    loan = repo.get_loan(loan_id)
    loan.mark_as_returned()
    assert repo.get_active_loan_by_book(book_id) is None


def test_loan_get_active_loan_by_book_returns_loan(repo: LibraryRepository):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(
        User(username="hector", email=Email("hectorbarak@mail.com"))
    )
    loan_id = repo.add_loan(Loan(book_id, user_id, date.today()))
    loan = repo.get_loan(loan_id)
    assert repo.get_active_loan_by_book(book_id) is loan


def test_return_book_raises_error_when_book_not_found(
    repo: LibraryRepository,
):
    with pytest.raises(BookNotFoundError):
        repo.return_book(999999)


def test_return_book_raises_error_when_book_not_loaned(
    repo: LibraryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))

    with pytest.raises(BookNotLoanedError):
        repo.return_book(book_id)


def test_return_book_marks_book_and_loan_as_returned(
    repo: LibraryRepository,
):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="hector", email=Email("hector@example.com")))
    loan_id = repo.add_loan(Loan(book_id, user_id, date.today()))

    repo.return_book(book_id)

    book = repo.get_book(book_id)
    assert book.is_available

    loan = repo.get_loan(loan_id)
    assert not loan.is_active()
