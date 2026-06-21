import re
from dataclasses import dataclass


class LibraryApiError(Exception):
    """Base exception for all library API errors."""


class BookError(LibraryApiError):
    """Raised for general book-related failures."""


_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not _EMAIL_RE.match(self.value):
            raise ValueError("Invalid email format")
        object.__setattr__(self, "value", self.value.lower())


@dataclass
class Book:
    title: str
    author: str
    is_available: bool = True

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise BookError("Book must have a title")
        if not self.author or not self.author.strip():
            raise BookError("Book must have an author")
