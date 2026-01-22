from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    username: str
    email: str
    id: int | None = None


@dataclass
class Book:
    title: str
    author: str
    is_available: bool = True
    id: int | None = None


@dataclass
class Loan:
    user_id: int
    book_id: int
    loan_date: date
    return_date: Optional[date] = None
    id: int | None = None
