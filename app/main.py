from .models import Book
from .protocols import DbProtocol
from .library_service import LibraryService
from .in_memory_database import InMemoryDatabase

if __name__ == "__main__":

    Db: DbProtocol = InMemoryDatabase()
    library: LibraryService = LibraryService(Db)

    book1: Book = Book("The Great Gatsby", "F. Scott Fitzgerald")
    book2: Book = Book("Moby Dick", "Herman Melville")
    book3: Book = Book("La Tabla de Flandes", "Arturo Perez Reverte")

    library.register_book(book1)
    library.register_book(book2)
    library.register_book(book3)

    book = library.get_book_by_title("the GREAT gATsby")
    print(book)
