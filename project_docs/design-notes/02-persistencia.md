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

### Decisión 0.2 — Dos fixtures en `test_library_service.py`: fábrica y consumidor

**Qué:** `test_library_service.py` usa dos fixtures de pytest donde una sola
instancia de `InMemoryRepository` se comparte con dos anotaciones de tipo
distintas:

```python
@pytest.fixture
def repo() -> InMemoryRepository:              # tipo CONCRETO
    return InMemoryRepository()

@pytest.fixture
def service(repo: LibraryRepository) -> LibraryService:  # tipo ABSTRACTO
    return LibraryService(repo)
```

**Por qué dos fixtures en vez de uno:** Stage 1 también usaba fixtures:
`test_repository.py` tenía un solo `repo: LibraryRepository`. Pero en Stage 1
el repositorio era a la vez almacén de datos Y SUT — `loan_book()` y
`return_book()` eran métodos del repositorio. Un solo fixture bastaba para
Arrange, Act y Assert. En Stage 2, `loan_book()` y `return_book()` se mueven
al `LibraryService`, separando dos preocupaciones que antes compartían fixture:

| Fixture | Rol | ¿Para qué lo usan los tests? |
|---|---|---|
| `repo` | Canal de Arrange + Assert | Poblar datos antes del test (`add_book`, `add_user`) y verificar estado después (`get_book`, `get_loan`) |
| `service` | SUT — System Under Test | Ejecutar la operación bajo prueba (`loan_book`, `return_book`) |

Separarlos permite que cada test declare solo lo que necesita:

```python
# Este test solo necesita el servicio — no toca el repo
def test_loan_book_raises_error_when_book_not_found(service):
    with pytest.raises(BookNotFoundError):
        service.loan_book(999999, 1)

# Este test necesita ambos — setup con repo, act con service, assert con repo
def test_loan_book_creates_loan(service, repo):
    book_id = repo.add_book(Book(...))
    user_id = repo.add_user(User(...))
    loan_id = service.loan_book(book_id, user_id)
    assert repo.get_loan(loan_id).is_active()
```

**Qué cambió respecto a Stage 1 y qué no:**

Los tests de modelos de dominio (`test_book.py`, `test_user.py`,
`test_loan.py`, `test_email.py`) nunca tuvieron fixtures — ni en Stage 1
ni ahora. Son tests puros que crean objetos directamente sin depender de
nada externo. Pasan intactos de una etapa a otra.

El único test de Stage 1 que usaba fixtures era `test_repository.py`:

```python
# Stage 1 — un solo fixture, el repo era datos + SUT
@pytest.fixture
def repo() -> LibraryRepository:
return InMemoryRepository()
```

En Stage 2 ese archivo desaparece y se reemplaza por dos:

| Stage 1 | Stage 2 |
|---|---|
| `test_repository.py` — 1 fixture (`repo`) | ❌ Eliminado |
| — | `test_library_service.py` — 2 fixtures (`repo` + `service`) |
| — | `test_sqlite_repository.py` — 0 fixtures (usa SQLite `:memory:`) |

El motivo por el que ahora hay 2 fixtures en vez de 1 es precisamente
mover `loan_book()` y `return_book()` al servicio: al separar el SUT del
almacén de datos, necesitas un fixture para cada rol. Los tests de modelos
(`test_book.py`, etc.) son idénticos — nunca necesitaron fixtures y siguen
sin necesitarlos.

**Por qué las anotaciones de tipo son distintas siendo el mismo objeto:**

El fixture `repo` declara `-> InMemoryRepository` porque es la **fábrica**:
sabe exactamente qué construye. El fixture `service` declara
`repo: LibraryRepository` porque es el **consumidor**: solo le importa el
contrato, no la implementación concreta.

```
repo() devuelve → InMemoryRepository (instancia concreta)
                        │
                        └── misma referencia → service(repo=...)
                                                        │
                                                self._repo = esa instancia
```

Python en runtime ignora las anotaciones — es el mismo objeto, con el mismo
`id()` en memoria. Pyright acepta que `InMemoryRepository` se pase donde se
espera `LibraryRepository` porque `LibraryRepository` es un `Protocol`:
verifica que `InMemoryRepository` tenga todos los métodos requeridos
(`add_book`, `get_book`, `add_user`, …) sin exigir herencia explícita.

Esto es el **Dependency Inversion Principle** (la D de SOLID) en la práctica:

> «Depende de abstracciones, no de concreciones»

| Capa | Anotación | ¿Por qué? |
|---|---|---|
| Fábrica (`repo`) | `InMemoryRepository` | Sabe exactamente qué construye |
| Consumidor (`service`) | `LibraryRepository` | Solo necesita el contrato — no le importa si es `InMemoryRepository`, `SQLiteRepository` o `MongoRepository` |

**Beneficio real:** si mañana `repo` cambia para devolver `SQLiteRepository`,
el fixture `service` **no se toca**. Si se hubiera anotado
`service(repo: InMemoryRepository)`, habría que modificar también el consumidor.
Eso es acoplamiento innecesario. La anotación no describe el objeto — describe
**lo que ese código necesita saber sobre el objeto**.

**Por qué `InMemoryRepository` sobrevive en Stage 2:** el roadmap original
planeaba eliminar `InMemoryRepository` al introducir `SQLiteRepository`. Pero
`test_library_service.py` necesita un doble de test rápido y sin I/O para
probar la orquestación del servicio. `InMemoryRepository` cumple ese rol
perfectamente: mismo protocolo, cero dependencias externas, ejecución
instantánea. `SQLiteRepository` se prueba aparte en `test_sqlite_repository.py`
con tests de integración sobre SQLite `:memory:`.

---

## Parte II

Patrones y principios descubiertos

> Esta sección crece con el proyecto. Los patrones se documentan cuando emergen de
> los tests, no se declaran de antemano.

| Patrón / Principio | Fuente | Dónde aparece | Qué resuelve |
|---|---|---|---|
| **Dependency Inversion** | SOLID (Robert C. Martin) | Fixtures de `test_library_service.py` — `repo` (tipo concreto) vs `service` (tipo abstracto) | La fábrica conoce la implementación; el consumidor solo el contrato. Cambiar `InMemoryRepository` por `SQLiteRepository` no toca el fixture `service`. |
| **Protocol** | Python `typing.Protocol` (PEP 544) | `LibraryRepository` en `repository.py` | Structural subtyping: cualquier clase con los métodos correctos cumple el contrato sin heredar de una clase base. |
| **Service Layer** | DDD / Fowler (PoEAA) | `LibraryService` en `library_service.py` | Orquestación multi-entidad separada del repositorio. El servicio coordina; el repositorio solo persiste.
