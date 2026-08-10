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
| **El protocolo debe ser mínimo** | Un protocolo con 11 métodos donde 2 son orquestación fuerza a cada implementación a conocer reglas de negocio. Reducido a 9 métodos CRUD, el contrato es claro: «dame datos, yo decido qué hacer con ellos». |
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

**Qué desaparece y qué cambia de rol:**

- `test_repository.py` — eliminado. Se reemplaza por `test_library_service.py` (unitario, con doble de test) y `test_sqlite_repository.py` (integración, con SQLite `:memory:`).
- `InMemoryRepository` — cambia de rol: deja de ser el SUT y pasa a ser un test double ligero para `test_library_service.py`. Sus métodos de orquestación (`loan_book`, `return_book`) se van al servicio; sus métodos CRUD permanecen intactos. No se elimina porque el servicio necesita un doble de test rápido y sin I/O (ver Decisión 0.2).

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

## Sesión 1 — Implementación de LibraryService

> Fecha: julio 2026

Implementamos `LibraryService` con sus dos métodos de orquestación y los
7 tests que los verifican. El refactor fue puramente mecánico: mover
`loan_book()` y `return_book()` del repositorio al servicio, delegando
persistencia al protocolo y lógica de negocio a los modelos de dominio.

### Decisión 1.1 — `loan_book()`: secuencia de validación

**Qué:** el método `loan_book()` orquesta un préstamo en cuatro pasos:

```python
def loan_book(self, book_id: BookID, user_id: UserID) -> LoanID:
    book = self._repo.get_book(book_id)       # 1. Validar que el libro existe
    self._repo.get_user(user_id)               # 2. Validar que el usuario existe
    book.mark_as_loaned()                      # 3. Marcar libro + crear préstamo
    return self._repo.add_loan(Loan(book_id, user_id))
```

**Por qué esa secuencia:**

| Paso | Operación | ¿Qué valida? | ¿Quién lanza el error? |
|---|---|---|---|
| 1 | `get_book(book_id)` | El libro existe | `BookNotFoundError` (repo) |
| 2 | `get_user(user_id)` | El usuario existe | `UserNotFoundError` (repo) |
| 3 | `book.mark_as_loaned()` | El libro no está ya prestado | `BookAlreadyLoanedError` (modelo) |

El orden importa: primero se validan las referencias externas (libro y usuario
existen en el repositorio), luego el estado interno (el libro no está prestado).
Si el libro no existe, no tiene sentido comprobar si está disponible.

**Quién lanza cada error:**

| Error | Lo lanza | Por qué |
|---|---|---|
| `BookNotFoundError` | `repo.get_book()` | Es responsabilidad del repositorio saber si un ID existe |
| `UserNotFoundError` | `repo.get_user()` | Ídem |
| `BookAlreadyLoanedError` | `book.mark_as_loaned()` | Es el modelo de dominio quien protege su propio estado |

El servicio no conoce los detalles de cómo el repositorio busca ni cómo
el modelo valida. Solo orquesta: «trae esto, valida aquello, ejecuta esto otro».

**Por qué `self._repo.get_user(user_id)` sin asignar el resultado:** el
servicio solo necesita confirmar que el usuario existe. No usa el objeto
`User` para nada más. `get_user()` lanza `UserNotFoundError` si el ID no
existe; si no lanza, el usuario es válido. Es una **validación por efecto
lateral**, no por valor de retorno.

### Decisión 1.2 — `return_book()`: diseño y validación de préstamo activo

**Qué:** el método `return_book()` orquesta una devolución en cuatro pasos:

```python
def return_book(self, book_id: BookID) -> None:
    book = self._repo.get_book(book_id)              # 1. Validar que el libro existe
    loan = self._repo.get_active_loan_by_book(book_id)  # 2. Buscar préstamo activo
    if loan is None:                                    # 3. Validar que hay préstamo
        raise BookNotLoanedError(f"Book with id {book_id} is not currently loaned")
    book.mark_as_returned()                             # 4. Marcar devolución
    loan.mark_as_returned()
```

**Por qué `get_active_loan_by_book()` devuelve `Loan | None` en vez de lanzar
error:** `BookNotLoanedError` es un error de **orquestación**, no de
persistencia. El repositorio no sabe qué es «no estar prestado» como concepto
de negocio — solo sabe buscar datos. Devolver `None` deja que el servicio
decida si eso es un error o un estado válido. Es la misma lógica que
`dict.get()` vs `dict[]`: el repositorio devuelve datos; el servicio les
da significado de negocio.

**Por qué `BookNotLoanedError` se lanza desde el servicio y no desde el
modelo:** a diferencia de `BookAlreadyLoanedError`, que protege una invariante
interna de `Book` («no pases a prestado lo que ya está prestado»),
«no hay préstamo activo» no es una invariante del modelo — es una condición
que solo tiene sentido en el contexto de una devolución. `Book` no sabe ni
debe saber si tiene un préstamo activo; eso lo determina el servicio a partir
de los datos que le devuelve el repositorio. El repositorio solo busca datos
(`get_active_loan_by_book()` → `Loan | None`); el servicio les da significado
de negocio (`None` → `BookNotLoanedError`).

### Decisión 1.3 — Tests de `loan_book()`

**Qué:** 4 tests cubren el método `loan_book()`. Siguen el mismo orden que
los tests de entidades en Stage 1: negativos primero, positivo al final.

**Test 1 — Libro no encontrado:**

```python
def test_loan_book_raises_error_when_book_not_found(service):
    with pytest.raises(BookNotFoundError):
        service.loan_book(999999, 1)
```

| Aspecto | Detalle |
|---|---|
| Tipo | Negativo |
| Fixtures | Solo `service` — no necesita repo porque no hay datos que preparar |
| Qué prueba | Que un ID de libro inexistente lanza `BookNotFoundError` |
| Por qué sin repo | El error ocurre en la primera llamada a `get_book()`. No hace falta poblar nada. |

**Test 2 — Usuario no encontrado:**

```python
def test_loan_book_raises_error_when_user_not_found(service, repo):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    with pytest.raises(UserNotFoundError):
        service.loan_book(book_id, 999999)
```

| Aspecto | Detalle |
|---|---|
| Tipo | Negativo |
| Fixtures | Ambos — `repo` para crear un libro válido, `service` para el SUT |
| Qué prueba | Que con libro existente pero usuario inexistente, el error es `UserNotFoundError` |
| Por qué necesita repo | Hay que crear un libro real para que `get_book()` no falle antes. El test aísla el fallo del usuario. |

**Test 3 — Libro ya prestado:**

```python
def test_loan_book_raises_error_when_book_already_loaned(service, repo):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="alice", email=Email("alice@example.com")))
    another_user_id = repo.add_user(
        User(username="bob", email=Email("bob@example.com"))
    )
    service.loan_book(book_id, user_id)  # primer préstamo — OK

    with pytest.raises(BookAlreadyLoanedError):
        service.loan_book(book_id, another_user_id)  # segundo — ERROR
```

| Aspecto | Detalle |
|---|---|
| Tipo | Negativo |
| Fixtures | Ambos — `repo` para crear libro, dos usuarios y ejecutar el primer préstamo |
| Qué prueba | Que un libro ya prestado no puede prestarse otra vez, aunque sea a otro usuario |
| Por qué dos usuarios | Para demostrar que el bloqueo es sobre el **libro**, no sobre el usuario. Si solo hubiera un usuario, el test no distinguiría entre «el usuario ya tiene el libro» y «el libro ya está prestado». |

**Test 4 — Préstamo exitoso:**

```python
def test_loan_book_creates_loan_and_marks_book_as_loaned(service, repo):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="hector", email=Email("hector@example.com")))

    loan_id = service.loan_book(book_id, user_id)

    loan = repo.get_loan(loan_id)
    assert loan.book_id == book_id
    assert loan.user_id == user_id
    assert loan.is_active()

    book = repo.get_book(book_id)
    assert not book.is_available
```

| Aspecto | Detalle |
|---|---|
| Tipo | Positivo |
| Fixtures | Ambos — `repo` para setup y verificación, `service` para el SUT |
| Qué prueba | El ciclo completo: se crea un préstamo con los datos correctos y el libro queda no disponible |
| Asserts | 5: `book_id` correcto, `user_id` correcto, préstamo activo, `book.is_available` es `False`, libro existe |

**Por qué 4 tests en vez de 3:** los dos primeros tests negativos (`book not
found`, `user not found`) podrían parecer redundantes — ambos prueban
«referencia externa no existe». Pero validan **errores distintos** lanzados
por **métodos distintos** del repositorio (`get_book` vs `get_user`). Un solo
test que pasara `book_id=999, user_id=999` sería ambiguo: si falla por
`BookNotFoundError`, nunca sabrías si `get_user` también habría funcionado.

**Patrón de los tests de servicio:**

| Fase | ¿Quién la ejecuta? | Ejemplo |
|---|---|---|
| Arrange | `repo` | `repo.add_book(...)`, `repo.add_user(...)` |
| Act | `service` | `service.loan_book(book_id, user_id)` |
| Assert | `repo` | `repo.get_loan(loan_id)`, `repo.get_book(book_id)` |

El servicio no expone métodos de consulta — solo comandos. Por eso la
verificación (Assert) siempre vuelve al repositorio: es la única fuente de
verdad sobre el estado persistido.

### Decisión 1.4 — Tests de `return_book()`

**Qué:** 3 tests cubren el método `return_book()`. Misma estructura:
negativos primero, positivo al final.

**Test 1 — Libro no encontrado:**

```python
def test_return_book_raises_error_when_book_not_found(service):
    with pytest.raises(BookNotFoundError):
        service.return_book(999999)
```

Análogo al test 1 de `loan_book`. Sin repo porque el error ocurre en la
primera línea del método. No hay nada que preparar.

**Test 2 — Libro no prestado:**

```python
def test_return_book_raises_error_when_book_not_loaned(service, repo):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    with pytest.raises(BookNotLoanedError):
        service.return_book(book_id)
```

| Aspecto | Detalle |
|---|---|
| Tipo | Negativo |
| Qué prueba | Que devolver un libro que existe pero no está prestado lanza `BookNotLoanedError` |
| Por qué `BookNotLoanedError` | Es un error de orquestación (ver Decisión 1.2), no una invariante interna de `Book` |

**Test 3 — Devolución exitosa:**

```python
def test_return_book_marks_book_and_loan_as_returned(service, repo):
    book_id = repo.add_book(Book(title="1984", author="George Orwell"))
    user_id = repo.add_user(User(username="hector", email=Email("hector@example.com")))
    loan_id = service.loan_book(book_id, user_id)  # primero se presta

    service.return_book(book_id)  # luego se devuelve

    book = repo.get_book(book_id)
    assert book.is_available         # el libro vuelve a estar disponible

    loan = repo.get_loan(loan_id)
    assert not loan.is_active()      # el préstamo ya no está activo
```

| Aspecto | Detalle |
|---|---|
| Tipo | Positivo |
| Qué prueba | El ciclo completo: préstamo → devolución → libro disponible + préstamo inactivo |
| Asserts | 2: `book.is_available` es `True`, `loan.is_active()` es `False` |

**Por qué el test positivo de `return_book` pasa primero por `loan_book`:**
`return_book()` no puede probarse de forma aislada — requiere un préstamo
activo previo. En vez de manipular el repositorio directamente para crear un
préstamo (lo cual acoplaría el test a detalles internos), el test usa
`service.loan_book()`. Esto prueba el ciclo real de negocio: préstamo →
devolución. Si `loan_book()` tuviera un bug, este test también lo
detectaría.

### Decisión 1.5 — `models.py` intacto: los modelos de dominio no cambiaron

**Qué:** los modelos `Book`, `User`, `Loan` y el VO `Email` permanecen
idénticos a Stage 1. Ni una línea modificada.

**Por qué:** la separación en capas (servicio / repositorio) es un cambio
arquitectónico que no afecta al dominio. Los modelos ya tenían los métodos
necesarios (`mark_as_loaned()`, `mark_as_returned()`, `is_active()`) desde
Stage 1. El servicio solo los conecta con el repositorio. Es la prueba de
que el diseño original era sólido: añadir una capa nueva no rompió nada de
lo existente.

**Evidencia:**

```bash
git diff main..stage2-persistence -- src/app/models.py
# (sin salida — el archivo no se tocó)
```

Los únicos archivos modificados en Stage 2 (hasta ahora):

| Archivo | Cambio |
|---|---|
| `src/app/repository.py` | `LibraryRepository` pierde `loan_book()` y `return_book()`; `InMemoryRepository` ídem |
| `src/app/library_service.py` | **Nuevo** — `LibraryService` con `loan_book()` y `return_book()` |
| `src/tests/test_library_service.py` | **Nuevo** — 7 tests con dos fixtures |
| `src/tests/test_repository.py` | Eliminado — reemplazado por `test_library_service.py` |
| `src/app/models.py` | Sin cambios |
| `src/tests/test_book.py` | Sin cambios |
| `src/tests/test_user.py` | Sin cambios |
| `src/tests/test_loan.py` | Sin cambios |
| `src/tests/test_email.py` | Sin cambios |

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
