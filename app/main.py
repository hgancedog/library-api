from .models import Book
from .protocols import DbProtocol
from .library_service import LibraryService
from .in_memory_database import InMemoryDatabase

if __name__ == "__main__":

    Db: DbProtocol = InMemoryDatabase()
    library: LibraryService = LibraryService(Db)

    book1: Book = Book("The Great Gatsby", "F. Scott Fitzgerald")
    library.register_book(book1)

    print(library.get_all_books())
