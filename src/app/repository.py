from typing import Protocol

from app.models import (
    Book,
    BookID,
    BookNotFoundError,
    Loan,
    LoanID,
    LoanNotFoundError,
    User,
    UserID,
    UserNotFoundError,
)


class LibraryRepository(Protocol):
    def add_book(self, book: Book) -> BookID: ...
    def get_book(self, book_id: BookID) -> Book: ...
    def get_all_books(self) -> dict[BookID, Book]: ...
    def add_user(self, user: User) -> UserID: ...
    def get_user(self, user_id: UserID) -> User: ...
    def add_loan(self, loan: Loan) -> LoanID: ...
    def get_loan(self, loan_id: LoanID) -> Loan: ...
    def get_active_loans_by_user(self, user_id: UserID) -> list[Loan]: ...


class InMemoryRepository:
    def __init__(self):
        self._db_books: dict[BookID, Book] = {}
        self._db_users: dict[UserID, User] = {}
        self._db_loans: dict[LoanID, Loan] = {}
        self._next_book_id: BookID = 1
        self._next_user_id: UserID = 1
        self._next_loan_id: LoanID = 1

    def add_book(self, book: Book) -> BookID:
        book.book_id = self._next_book_id
        self._db_books[book.book_id] = book
        self._next_book_id += 1
        return book.book_id

    def get_book(self, book_id: BookID) -> Book:
        if book_id not in self._db_books:
            raise BookNotFoundError(f"Book with id {book_id} not found")
        return self._db_books[book_id]

    def get_all_books(self) -> dict[BookID, Book]:
        return dict(self._db_books)

    def add_user(self, user: User) -> UserID:
        user.user_id = self._next_user_id
        self._db_users[user.user_id] = user
        self._next_user_id += 1
        return user.user_id

    def get_user(self, user_id: UserID) -> User:
        if user_id not in self._db_users:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return self._db_users[user_id]

    def add_loan(self, loan: Loan) -> LoanID:
        loan.loan_id = self._next_loan_id
        self._db_loans[loan.loan_id] = loan
        self._next_loan_id += 1
        return loan.loan_id

    def get_loan(self, loan_id: LoanID) -> Loan:
        if loan_id not in self._db_loans:
            raise LoanNotFoundError(f"Loan with id {loan_id} not found")
        return self._db_loans[loan_id]

    def get_active_loans_by_user(self, user_id: UserID) -> list[Loan]:
        loans: list[Loan] = []

        for loan in self._db_loans.values():
            if user_id == loan.user_id and loan.is_active():
                loans.append(loan)

        return loans


_: LibraryRepository = InMemoryRepository()
