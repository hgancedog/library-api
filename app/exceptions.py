class LibraryApiError(Exception):
    pass


class BookError(LibraryApiError):
    pass


class UserError(LibraryApiError):
    pass


class BookNotFoundError(BookError):
    pass


class BookAlreadyLoanedError(BookError):
    pass
