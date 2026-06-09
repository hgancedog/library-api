class LibraryApiError(Exception):
    """Base exception for all library system errors."""

    pass


class BookError(LibraryApiError):
    """Raised for general book-related failures."""

    pass


class UserError(LibraryApiError):
    """Raised for validation or existence errors related to library members."""

    pass


class LoanError(LibraryApiError):
    """Raised when loan processing or validation fails."""

    pass


class BookNotFoundError(BookError):
    """Raised specifically when a book ID does not exist in the database."""

    pass


class BookAlreadyLoanedError(BookError):
    """Raised when attempting to loan a book that is already out."""

    pass
