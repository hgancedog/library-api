# Persistencia — library-api

> Stage 2 · `stage2-persistence`
> Inicio: julio 2026
> Autor: Hector Gancedo Grade · con asistencia de IA (Pi Agent Harness)

---

## Propósito

Este documento registra todas las decisiones de diseño tomadas durante Stage 2
(Persistence). Cada decisión incluye su contexto y por qué.

**Estructura:**

- [Parte I](#parte-i) — Decisiones de arquitectura y diseño del sistema
- [Parte II](#parte-ii) — Patrones y principios descubiertos

---

## Parte I

Decisiones de arquitectura y diseño del sistema

---

## Sesión 0 — Preparación y decisiones de arquitectura

> Fecha: julio 2026

Arranca Stage 2 con una decisión de arquitectura que corrige deuda detectada en Stage 1
antes de escribir el `SQLiteRepository`.

### Decisión 0.1 — Separar `LibraryService` del repositorio

**Qué:** se crea una capa de servicio (`LibraryService`) que asume la orquestación
de operaciones multi-entidad. El protocolo `LibraryRepository` se reduce a CRUD puro.
`loan_book()` y `return_book()` salen del repositorio y pasan al servicio.

**Estado actual (Stage 1):**

```python
# repository.py — el repositorio orquesta y persiste
class InMemoryRepository:
    def loan_book(self, book_id, user_id):
        book = self.get_book(book_id)       # persistencia: leer
        self.get_user(user_id)              # persistencia: validar
        book.mark_as_loaned()               # dominio: lógica de negocio
        return self.add_loan(Loan(...))     # persistencia: guardar

    def return_book(self, book_id):
        book = self.get_book(book_id)       # persistencia: leer
        loan = self.get_active_loan_by_book(book_id)  # persistencia: consultar
        book.mark_as_returned()             # dominio: lógica de negocio
        loan.mark_as_returned()             # dominio: lógica de negocio
```

El método `loan_book()` mezcla tres responsabilidades:

1. Recuperar datos (persistencia)
2. Validar reglas de negocio (dominio)
3. Guardar resultados (persistencia)

La orquestación entre ellas no es trabajo de un repositorio. Un repositorio
persiste y recupera. Punto.

**Estado deseado (Stage 2):**

```python
# repository.py — solo CRUD
class LibraryRepository(Protocol):
    def add_book(self, book: Book) -> BookID: ...
    def get_book(self, book_id: BookID) -> Book: ...
    def add_user(self, user: User) -> UserID: ...
    def get_user(self, user_id: UserID) -> User: ...
    def add_loan(self, loan: Loan) -> LoanID: ...
    def get_loan(self, loan_id: LoanID) -> Loan: ...
    def get_active_loans_by_user(self, user_id: UserID) -> list[Loan]: ...
    def get_active_loan_by_book(self, book_id: BookID) -> Loan | None: ...

# library_service.py — orquestación
class LibraryService:
    def __init__(self, repository: LibraryRepository) -> None:
        self._repo = repository

    def loan_book(self, book_id: BookID, user_id: UserID) -> LoanID:
        book = self._repo.get_book(book_id)
        self._repo.get_user(user_id)       # validar existencia
        book.mark_as_loaned()              # delega en el modelo de dominio
        return self._repo.add_loan(Loan(book_id, user_id))

    def return_book(self, book_id: BookID) -> None:
        book = self._repo.get_book(book_id)
        loan = self._repo.get_active_loan_by_book(book_id)
        if loan is None:
            raise BookNotLoanedError(f"Book {book_id} is not currently loaned")
        book.mark_as_returned()
        loan.mark_as_returned()
```

**Por qué ahora y no en Stage 3:**

| Razón | Explicación |
|-------|-------------|
| **DRY entre implementaciones** | `SQLiteRepository` replicaría la misma orquestación que `InMemoryRepository`. Sin servicio, cada implementación del protocolo reescribe la lógica de `loan_book()`. El servicio la escribe una vez y cualquier repositorio la aprovecha. |
| **El protocolo debe ser mínimo** | Un protocolo con 12 métodos donde 2 son orquestación fuerza a cada implementación a conocer reglas de negocio. Reducido a 10 métodos CRUD, el contrato es claro: «dame datos, yo decido qué hacer con ellos». |
| **Testabilidad** | El servicio se prueba con un test double ligero (mock o fake del repositorio), sin I/O. El repositorio se prueba con SQLite real. Cada categoría de test prueba una preocupación distinta. |
| **Puerta abierta a Stage 3** | Stage 3 introducirá validación con Pydantic en los puntos de entrada. Tener un servicio ahora evita duplicar validación en cada repositorio o tener que crear el servicio + migrar métodos + añadir validación todo de golpe. |
| **Coste mínimo ahora** | Son ~30 líneas de servicio. Hacerlo en Stage 3 costaría lo mismo en escritura más el refactor de tests. Hacerlo en Stage 7 (microservicios) sería un problema serio. |

**Qué cambia en el protocolo:**

```diff
  class LibraryRepository(Protocol):
      def add_book(self, book: Book) -> BookID: ...
      def get_book(self, book_id: BookID) -> Book: ...
      def get_all_books(self) -> dict[BookID, Book]: ...
-     def return_book(self, book_id: BookID) -> None: ...
-     def loan_book(self, book_id: BookID, user_id: UserID) -> LoanID: ...
      def add_user(self, user: User) -> UserID: ...
      def get_user(self, user_id: UserID) -> User: ...
      def add_loan(self, loan: Loan) -> LoanID: ...
      def get_loan(self, loan_id: LoanID) -> Loan: ...
      def get_active_loans_by_user(self, user_id: UserID) -> list[Loan]: ...
      def get_active_loan_by_book(self, book_id: BookID) -> Loan | None: ...
```

**Qué desaparece:**

- `InMemoryRepository` — deja de ser necesario. Sus métodos de orquestación se van al servicio y los de persistencia son reemplazados por `SQLiteRepository`. Los tests de modelos de dominio (`test_book.py`, `test_user.py`, `test_loan.py`, `test_email.py`) no lo usan.
- `test_repository.py` — reemplazado por `test_library_service.py` (unitario, con doble de test) y `test_sqlite_repository.py` (integración, con SQLite `:memory:`).

**Impacto en tests de Stage 1:**

| Archivo | ¿Se modifica? | Motivo |
|---------|:---:|--------|
| `test_book.py` | No | Prueba el modelo `Book`. No depende de repositorio ni servicio. |
| `test_user.py` | No | Prueba el modelo `User`. Ídem. |
| `test_loan.py` | No | Prueba el modelo `Loan`. Ídem. |
| `test_email.py` | No | Prueba el VO `Email`. Ídem. |
| `test_repository.py` | Sí | Se reemplaza por `test_library_service.py` + `test_sqlite_repository.py`. La cobertura no se pierde: el comportamiento probado antes contra `InMemoryRepository` se prueba ahora contra el servicio + el repositorio SQL. |

---

## Parte II

Patrones y principios descubiertos

> Esta sección crece con el proyecto. Los patrones se documentan cuando emergen de
> los tests, no se declaran de antemano.
