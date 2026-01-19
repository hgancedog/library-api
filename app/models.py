from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    id: int
    username: str
    email: str


@dataclass
class Book:
    id: int
    title: str
    author: str
    is_available: bool = True


@dataclass
class Loan:
    id: int
    user_id: int
    book_id: int
    loan_date: date
    return_date: Optional[date] = None
