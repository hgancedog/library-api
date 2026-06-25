# TDD desde cero — library-api

> Rama: `stage1-tdd-from-scratch`
> Inicio: junio 2026
> Autor: Hector Gancedo Grade · con asistencia de IA (Pi Agent Harness)

---

## Propósito

Este documento es el **registro único** de todas las decisiones tomadas durante la
reconstrucción de library-api aplicando TDD estricto desde cero. Cada decisión
incluye su por qué. Incluye también un [apéndice](#apéndice) con la guía TDD paso a paso como
referencia práctica.

No solo se documenta el TDD: se documenta cada elección de herramienta, estructura,
diseño y conocimiento adquirido.

---

## Sesión 0 — Configuración inicial

### Decisión 0.1 — Partir desde un commit sin design notes

**Qué:** la rama `stage1-tdd-from-scratch` bifurca desde `90fbb83`, el último
commit anterior a cualquier design note.

**Por qué:** los design notes (`01-diseno-por-dominio.md`, `02-decisiones-stage1.md`)
documentan un diseño hecho sin TDD. Si el diseño va a emerger de los tests, no tiene
sentido arrastrar documentos que dicen cómo se hizo la primera vez. La rama original
(`stage1-inmemory`) conserva todo para comparación posterior.

> ⚠️ **Corrección posterior (Decisión 2.5):** este commit también traía código de
> producción escrito sin TDD (`models.py`, `exceptions.py`, etc.). En la Sesión 2
> se eliminó todo ese código para empezar realmente desde cero.

```bash
git checkout -b stage1-tdd-from-scratch 90fbb83
```

### Decisión 0.2 — Plantilla TDD como documento 00

**Qué:** la plantilla de desarrollo TDD se importa de la rama original y se renombra
a `00-plantilla-tdd.md`.

**Por qué:** el prefijo `00-` indica que es una herramienta de referencia, no parte
del aprendizaje secuencial. El diario real arranca en `01`.

```bash
git checkout stage1-inmemory -- project_docs/design-notes/04-plantilla-tdd.md
git mv project_docs/design-notes/04-plantilla-tdd.md project_docs/design-notes/00-plantilla-tdd.md
```

### Decisión 0.3 — Python 3.14 como intérprete del proyecto

**Qué:** el proyecto usa Python 3.14.4, la versión instalada en el sistema.

**Por qué:** `pyproject.toml` declara `requires-python = ">=3.10"`. 3.14 lo cumple
sin problemas. Instalar una versión anterior sería trabajo extra sin beneficio,
especialmente en Stage 1 donde no hay dependencias externas que exijan una versión
concreta.

```bash
python3 --version   # Python 3.14.4
```

> ⚠️ Ruff tiene `target-version = "py313"`. Se actualizará a `py314` cuando
> aparezca el primer error de lint relacionado. No se toca antes por el principio
> TDD: no arregles lo que no está roto.

### Decisión 0.4 — Dependencias mínimas en pyproject.toml

**Qué:** el `pyproject.toml` heredado de la rama original contenía dependencias
para Stage 7 (FastAPI, Pydantic, Uvicorn). Se reduce a lo necesario para Stage 1:

```toml
# Producción: Python puro, sin frameworks
dependencies = []

[project.optional-dependencies]
dev = [
  "pytest>=8.0",       # framework de tests
  "pytest-cov>=6.0",   # cobertura de código
  "pyright==1.1.410",  # type checker estático
  "pre-commit==4.5.1", # hooks de calidad pre-commit
  "ruff==0.15.0",      # linter + formateador
]
```

**Por qué cada herramienta:**

| Dependencia | Rol | ¿Por qué esta y no otra? |
|---|---|---|
| pytest | Ejecutar tests | Estándar de la industria. Simple: busca funciones `test_*` y las ejecuta. Sin configuración inicial. |
| pytest-cov | Medir cobertura | Integración directa con pytest (`--cov`). Muestra qué líneas no pasan los tests. |
| pyright | Type checker | Análisis estático de tipos en modo strict (`pyrightconfig.json`). Detecta errores de tipo antes de ejecutar. Más rápido que mypy. |
| pre-commit | Hooks de calidad | Ejecuta ruff + pyright + venv-check antes de cada commit. Evita commits con errores de tipo o formato. |
| ruff | Linter + formato | Un solo tool que reemplaza flake8 + isort + black. Escrito en Rust, extremadamente rápido. |

### Decisión 0.5 — Entorno virtual limpio

**Qué:** se elimina el `.venv` heredado y se crea uno nuevo desde cero.

**Por qué:** el `.venv` anterior fue creado en la rama original y contenía paquetes
instalados que ya no están en `pyproject.toml` (FastAPI, Pydantic, Typeguard, etc.).
Un entorno limpio garantiza que solo existen las dependencias declaradas AHORA.

```bash
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
```

**¿Qué significa `pip install -e ".[dev]"`?**

```bash
pip install -e ".[dev]"
```

| Parte | Significado |
|---|---|
| `pip install` | Instala paquetes Python |
| `-e` | Modo **editable** (development mode). Instala un archivo `.pth` en `site-packages` que apunta a `src/`. Python lo lee al arrancar y añade esa ruta a `sys.path`. Los cambios en el código fuente se reflejan al instante al importar, sin reinstalar. **No es un symlink.** |
| `.` | Instala el paquete del directorio actual (library-api, definido en `pyproject.toml`) |
| `[dev]` | Instala también las dependencias opcionales del grupo `dev` (pytest, ruff, pre-commit) |

Sin `-e`, cada cambio en `src/` requeriría reinstalar el paquete para que los imports
funcionaran. Con `-e`, editas y los imports ven el cambio al instante.

### Decisión 0.6 — Instalar pre-commit hooks ahora, no después

**Qué:** se ejecuta `pre-commit install` antes de escribir cualquier línea de código.

**Por qué:** el config actual cubre ruff + ruff-format + venv-check + pyright.
Instalarlo ahora garantiza que el primer commit de código ya sale limpio. Si se deja
para después, el primer commit podría fallar por formato o tipo — y entonces tienes
dos problemas que resolver en lugar de uno. La disciplina de tooling se establece
antes del código, no como reacción a un commit fallido.

```bash
pre-commit install
```

---

## Sesión 1 — Refinamiento de la plantilla TDD

> Fecha: 19 junio 2026
> Fuente: conversación con Gemini (contenido sobre triangulación) + revisión crítica con Pi

En esta sesión no se escribió código de producción ni tests. Se refinó el documento
`00-plantilla-tdd.md` para que sirva como guía real de TDD, no solo como referencia
superficial. Cada cambio se documenta aquí con su porqué.

### Decisión 1.1 — Sección dedicada a triangulación

**Qué:** se añadió la sección «Triangulación: qué es y cuándo usarla» entre el
diagrama del ciclo RED-GREEN-REFACTOR y la tabla de orden de trabajo. Incluye la
metáfora del GPS, un ejemplo concreto (`calculate_shipping`) y una tabla de cuándo
conviene triangular y cuándo no.

**Por qué:** la plantilla mencionaba «triangula cuando dudes» en las reglas y tenía
notas dispersas, pero nunca definía el concepto. Sin definición, la regla es
inútil. La metáfora del GPS (1 satélite = radio enorme, 2+ satélites = coordenada
exacta) hace el concepto memorable. El ejemplo `calculate_shipping` muestra el
mecanismo: valor hardcodeado → segundo test con datos distintos fuerza el algoritmo
real. La tabla de «cuándo sí / cuándo no» evita que la triangulación se convierta
en ritual vacío.

**Fuente del contenido:** explicación proporcionada por Gemini, adaptada a
convenciones del proyecto (inglés para código, snake_case).

### Decisión 1.2 — Sección «Cuándo nacen las excepciones»

**Qué:** se añadió una sección que explica que las clases de excepción nacen de los
tests negativos, mostrando la secuencia real de RED encadenados
(`BookError` no existe → `Book` no existe → validación ausente). Incluye tabla
built-in vs custom, jerarquía del proyecto, y una subsección «¿Por qué un ancestro
común?».

**Por qué:** la plantilla original daba por sentado que las excepciones ya existían.
En TDD estricto, el test que hace `pytest.raises(MiError)` es el que fuerza a crear
`MiError`. La secuencia de RED encadenados no es obvia para quien empieza: el test
falla sobre el primer nombre no definido, así que la excepción se crea antes que la
entidad. Sin esta sección, quien siga la plantilla no sabrá en qué orden crear las
cosas.

**La subsección del ancestro común** se añadió tras una corrección del usuario:
originalmente decía «comparten ancestro para poder atraparlos con
except LibraryApiError» sin explicar por qué eso es útil. Ahora detalla 3 razones:
(1) separar errores de dominio de bugs, (2) no repetir listas de excepciones,
(3) evolucionar los errores sin tocar quien los atrapa.

### Decisión 1.3 — Corrección de secuencias RED en pasos 2.1 y 6.1

**Qué:** el paso 2.1 decía `RED esperado: NameError: name 'Book' is not defined`,
omitiendo que antes falla porque `BookError` no existe. El paso 6.1 no tenía RED
esperado. Ambos se corrigieron para mostrar los rojos encadenados.

**Por qué:** si la plantilla muestra una secuencia RED incorrecta, quien la siga
se confundirá cuando el error real no coincida con el esperado. Mostrar los rojos
reales genera confianza: el error que ves en pantalla es exactamente el que la
plantilla te dijo que verías.

### Decisión 1.4 — Reforzar el porqué en reglas 3 y 4

**Qué:** las reglas «RED primero» y «Código mínimo para GREEN» ahora incluyen su
porqué: ver el rojo confirma que el test prueba algo (un test sin assert siempre
está en verde); separar implementación de refactor evita perder el rastro de qué
cambio rompió qué.

**Por qué:** corrección del usuario: «siempre, cuando afirmes algo, explica el
porqué». Las reglas decían qué hacer pero no por qué. Sin el porqué, las reglas
se memorizan pero no se entienden, y cuando la situación no encaja exactamente,
no se sabe cómo adaptarse.

### Decisión 1.5 — Paso 7 con columna «Por qué»

**Qué:** el paso 7 (revisión de diseño) pasó de frases «está mal» a una tabla con
tres columnas: Pregunta, Si es SÍ…, Por qué. Cada «está mal» ahora tiene su razón
anclada en el Principio de Responsabilidad Única.

**Por qué:** misma corrección que 1.4. «La entidad no toca la DB» es una orden.
«La persistencia es responsabilidad del repositorio. Si la entidad sabe de tablas,
no puedes cambiar la DB sin tocar el dominio» es una lección de arquitectura.

### Decisión 1.6 — Nota sobre parámetros test vs función bajo test

**Qué:** se añadió una nota aclarando que un test no recibe en su signatura los
parámetros de la función que prueba. El test es el caller, la función es el callee.

**Por qué:** un usuario que empieza con TDD puede pensar que `def test_algo(param)`
debe reflejar los parámetros de la función bajo test. La nota evita esa confusión
antes de que ocurra. Se simplificó respecto a una versión inicial que mencionaba
fixtures y parametrize, porque esos conceptos no se necesitan en Stage 1.

### Decisión 1.7 — Posponer aprendizaje de fixtures y parametrize

**Qué:** se decidió no introducir `@pytest.fixture` ni `@pytest.mark.parametrize`
en la plantilla ni en el aprendizaje actual.

**Por qué:** en Stage 1 los tests son simples — cada test tiene sus propios datos
hardcodeados. Aprender fixtures o parametrize ahora añadiría complejidad sin
necesidad. La señal para aprenderlos será natural: fixtures cuando el mismo Arrange
aparezca copiado en 3+ tests, parametrize cuando haya 4+ tests que solo varíen en
datos de entrada/salida.

### Decisión 1.8 — Explicación de por qué Email es una clase (VO)

**Qué:** se añadió la subsección «¿Por qué esos criterios?» bajo la tabla «Cuándo
usar Value Objects vs strings simples», con 4 razones concretas.

**Por qué:** la tabla decía qué hacer pero no por qué. Las 4 razones (validación
centralizada, reutilización entre entidades, intención documentada en el tipo,
testabilidad aislada) convierten la tabla de referencia en una lección de diseño.

### Decisión 1.9 — Fusión de 00 y 01 en un solo documento

**Qué:** se elimina `00-plantilla-tdd.md` y todo su contenido se integra en este
documento. Las explicaciones profundas (triangulación, excepciones, VO) ya están
en las decisiones 1.1–1.8. La guía paso a paso con ejemplos de código se añade
como apéndice al final.

**Por qué:** mantener dos documentos generaba confusión sobre dónde poner cada
cosa y riesgo de inconsistencia. Un solo documento, en orden cronológico, permite
leer de principio a fin sin saltar entre archivos. El apéndice al final sirve
como referencia rápida sin interrumpir el flujo narrativo.

### Decisión 1.10 — Mantener `models.py` plano en Stage 1

**Qué:** se mantiene la organización plana (`models.py` con Book, User, Loan en un solo
archivo) en vez de dividir por dominio (`domain/book.py`, `domain/user.py`, etc.).
`models.py` contiene tanto **Value Objects** (`Email`) como **Entidades** (`Book`,
`User`, `Loan`).

**Por qué:** en TDD, la estructura emerge de los tests, no se diseña por adelantado.
Crear `domain/book.py` ahora sería una decisión arquitectónica sin un test que la
justifique. Además, Stage 1 tiene 3 entidades simples: la fricción de navegar entre
archivos supera el beneficio de separarlos. La señal para partir `models.py` será
natural: cuando el archivo crezca a ~200 líneas o duela encontrar una clase
concreta, el dolor justificará la división. En ese momento, los tests existentes
protegerán el movimiento.

**¿Por qué Value Objects y Entidades juntos?** Ambos son modelos de dominio. La
diferencia es conceptual, no de ubicación: un VO no tiene identidad (dos `Email`
con mismo valor son iguales), una Entidad sí (dos `Book` con mismo título pero
distinto `id` son distintos). Separarlos en archivos distintos (`vo/` vs
`entities/`) con solo 1 VO y 3 entidades sería sobre-ingeniería.

**Contexto:** el proyecto heredó de la rama original tanto el `models.py` plano
como directorios `domain/`, `db/`, `services/` con `.pyc` huérfanos. Se limpian
esos directorios.

---

## Sesión 2 — Primer test: Email Value Object

> Fecha: 19 junio 2026

Arranca la escritura de tests reales siguiendo el orden de trabajo del apéndice.

### Decisión 2.1 — Convenciones de estilo: PEP 8 + Ruff

**Qué:** el proyecto sigue PEP 8 con los ajustes de Ruff. Las reglas principales:

| Regla | PEP 8 | Este proyecto |
|---|---|---|
| Nombres de funciones | `snake_case` | `test_email_requires_at_sign` |
| Nombres de clases | `PascalCase` | `Email`, `Book`, `BookError` |
| Nombres de módulos | `snake_case` | `models.py`, `test_email.py` |
| Constantes | `UPPER_CASE` | (no hay aún) |
| Indentación | 4 espacios | Ruff lo fuerza |
| Largo de línea | 79 (PEP 8) / 88 (Ruff) | 88 — configurado en `pyproject.toml` |
| Comillas | Indistinto | **Dobles** — configurado en Ruff |
| Imports | 3 grupos: stdlib / terceros / locales | Ruff (`isort`) lo ordena |

**Por qué:** PEP 8 es el estándar de la industria. Ruff automatiza el
formateo y el orden de imports: no hay que memorizar reglas, el linter
corrige en pre-commit. La única decisión consciente es el largo de línea
(88 en vez de 79) porque facilita leer código con tipos anotados sin
partir líneas constantemente.

#### Convención de nombres de tests

Los tests se nombran por **la regla que el código debe cumplir**, no por
el input que reciben. La estructura:

```
test_<entidad>_<comportamiento_esperado>
```

| Ejemplo | Entidad | Comportamiento que prueba |
|---|---|---|
| `test_email_rejects_invalid_format` | Email | Rechaza un email sin formato válido (negativo) |
| `test_email_normalizes_to_lowercase` | Email | Convierte el email a minúsculas (positivo) |
| `test_book_requires_title` | Book | Necesita título — lo prueba con título vacío (negativo) |
| `test_cannot_loan_book_twice` | Book | Un libro prestado no se presta otra vez (negativo) |

**Por qué:** al leer el nombre del test sabes qué comportamiento del dominio
está probando sin abrir el código. Si el test falla, el nombre dice qué regla
se rompió.

**Regla para tests positivos:** un test positivo debe describir un
comportamiento que el código **hace** (`normalizes_to_lowercase`), no la
ausencia de error. Un nombre como `test_email_accepts_valid_format` es débil
porque describe lo que NO pasó (no hubo error), no lo que SÍ pasó (se
normalizó el valor).

### Decisión 2.2 — pytest `-v` como flag por defecto en TDD

**Qué:** se usa `pytest -v` (verbose) durante el ciclo TDD en vez de la salida
resumida.

**Por qué:** `-v` muestra el nombre completo de cada test y su resultado
(`PASSED`, `FAILED`, `ERROR`). En la fase RED, ver el nombre del test que falló
confirma que ejecutaste el que pensaste. En GREEN, ver todos los PASSED da
confianza de que no rompiste nada.

### Decisión 2.3 — VSCode en WSL: extensiones por contexto

**Qué:** las extensiones de VSCode no se comparten entre Windows y WSL. Las que
estaban instaladas en Windows desaparecen al abrir un proyecto en WSL. Hay que
instalarlas de nuevo dentro del contexto WSL remoto (`Install in WSL: Ubuntu`).

**Por qué:** VSCode trata WSL como un entorno remoto independiente. Las
extensiones que tocan el sistema de archivos o ejecutan procesos (Python,
linters, terminales) deben ejecutarse dentro de WSL, no en Windows. Es
consistente con la arquitectura cliente-servidor de VSCode: el servidor corre
en WSL con sus propias extensiones.

**Extensiones recomendadas para este proyecto:**

| Extensión | Para qué | Por qué |
|---|---|---|
| Python (`ms-python.python`) | Intérprete, test discovery, depuración | Núcleo del soporte Python en VSCode |
| Pylance (`ms-python.vscode-pylance`) | Type checking, autocompletado | Usa Pyright, el type checker del proyecto |
| Python Debugger (`ms-python.debugpy`) | Debugging paso a paso | Depurar tests que fallan sin `print()` |
| Python Environments (`ms-python.vscode-python-envs`) | Gestión de entornos | Cambiar entre `.venv` y otros sin comandos |
| Ruff (`charliermarsh.ruff`) | Linting + formateo | El mismo tool del proyecto, integrado en el editor |
| markdownlint (`davidanson.vscode-markdownlint`) | Linting de `.md` | Detecta errores en `project_docs/` (enlaces rotos, formato) |
| GitLens (`eamodio.gitlens`) | Blame, historial visual | Navegar decisiones pasadas en el código sin salir de VSCode |

**Mypy Type Checker se descarta** porque Pylance ya usa Pyright (mismo type
checker del proyecto, configurado en `pyrightconfig.json`). Tener dos
produciría diagnósticos duplicados. Pyright es más rápido.

**Cómo instalar:** con el proyecto abierto en WSL, `Ctrl+Shift+X` → buscar
cada ID → `Install in WSL: Ubuntu`. Las extensiones ya instaladas en Windows
local no aparecen en el contexto WSL; hay que reinstalarlas.

### Decisión 2.4 — Primer test: negativo de Email

**Qué:** se crea `src/app/tests/test_email.py`:

```python
import pytest


def test_email_rejects_invalid_format():
    with pytest.raises(ValueError):
        Email("without_sign")
```

**Por qué:** es el test negativo del VO Email. Usa `ValueError` (built-in)
porque Email es un VO simple. El test espera RED con `NameError: name 'Email'
is not defined`.

### Decisión 2.5 — Limpieza total de código pre-TDD

**Qué:** se eliminan todos los archivos de producción heredados de la rama
original (`exceptions.py`, `in_memory_database.py`, `library_service.py`,
`main.py`, `protocols.py`). `models.py` se vacía y solo contiene `Email`,
creado mediante TDD. Se conservan archivos de configuración (`pyproject.toml`,
`pyrightconfig.json`, `.pre-commit-config.yaml`).

**Por qué:** la Decisión 0.1 solo consideró eliminar los design notes
pre-TDD, pero el commit `90fbb83` también contenía código de producción
escrito sin tests. Mantenerlo viola la regla #1 de TDD (no escribir código
sin un test que falle). `Email` es ahora la primera clase del proyecto y
nació de un test. `Book`, `User`, `Loan` y el resto se recrearán cuando
lleguen sus tests.

### GREEN — Primer test superado

Se añade `from app.models import Email` al test y se crea `Email` en `models.py`
con validación por regex y `@dataclass(frozen=True)`. El test pasa a verde.

**Estado final de la estructura:**

```
src/
├── app/
│   ├── __init__.py
│   └── models.py      ← solo Email (TDD)
└── tests/
    └── test_email.py
```

### Decisión 2.6 — Email usa `@dataclass(frozen=True)`

**Qué:** la clase `Email` se implementa con `@dataclass(frozen=True)` en vez de
`__init__` manual.

**Por qué:**

- `frozen=True` hace el Value Object **inmutable** (no se puede modificar
  `email.value` tras la creación). Un VO debe ser inmutable por definición:
  dos `Email` con el mismo valor son intercambiables, y si alguien muta uno,
  esa garantía se rompe.
- `__eq__` automático: dos instancias con el mismo `value` son `==` sin
  escribir comparadores.
- `__repr__` automático: `Email(value='user@example.com')` en vez del
  opaco `<__main__.Email object at 0x...>`.
- Coherencia con el resto de entidades del proyecto (Book, User, Loan),
  que también usarán `@dataclass`.

### Decisión 2.7 — `tests/` fuera del paquete `app`

**Qué:** se mueve `tests/` de `src/app/tests/` a `src/tests/`. Se actualiza
`AGENTS.md`.

**Por qué:** tener `tests/` dentro de `src/app/` hace que Python lo trate como
un submódulo (`app.tests`). Esto tiene tres problemas:

1. **Contamina el espacio de nombres.** `tests` no es código de producción.
2. **Se despliega con el paquete.** Si el proyecto se publica, los tests viajan
   con el código del cliente.
3. **Rompe la convención.** El estándar Python es `tests/` fuera del paquete.

**Corrección de error previo:** el `AGENTS.md` original de `stage1-inmemory`
tenía `tests/` dentro de `app/`. Se heredó sin cuestionar y se indicó mal al
usuario durante esta sesión.

### Decisión 2.8 — Convención de imports: `import` vs `from`

**Qué:** se usa `import re` (módulo entero) para `re`, y `from dataclasses
import dataclass` (nombre único) para el decorador.

**Por qué:**

- `import re` trae el módulo y obliga a usar `re.compile(...)`. El prefijo
  `re.` deja claro que es una regex, no otra cosa. Además permite usar otras
  funciones de `re` (`re.IGNORECASE`, `re.search`) sin cambiar el import.
- `from dataclasses import dataclass` trae solo el decorador porque se usa
  exactamente una vez por clase. `import dataclasses` forzaría a escribir
  `@dataclasses.dataclass` con ruido innecesario.

**Regla general:**

| Situación | Forma |
|---|---|
| Usas una sola cosa del módulo | `from X import Y` |
| Usas varias cosas o el nombre solo es ambiguo | `import X` |

### Decisión 2.9 — `assert` vs `pytest.raises`

**Qué:** `assert` es una palabra reservada de Python, no de pytest. Funciona
en cualquier código, dentro o fuera de tests. `pytest.raises` es un context
manager propio de pytest.

**Por qué:**

| Mecanismo | Origen | Qué hace |
|---|---|---|
| `assert condicion` | Python built-in | Lanza `AssertionError` si la condición es falsa |
| `pytest.raises(Excepción)` | pytest | Verifica que el bloque dentro del `with` lance la excepción esperada |

Pytest no reemplaza `assert`: lo aprovecha. Cuando un `assert` falla dentro de
un test, pytest captura el `AssertionError`, muestra los valores comparados y
marca el test como `FAILED`. Pero `assert` sigue siendo Python puro.

**Cuándo usar cada uno:**

| Situación | Usar |
|---|---|
| Verificar un resultado (`==`, `is`, `in`) | `assert` |
| Verificar que se lanza una excepción | `pytest.raises` |
| Verificar que NO se lanza excepción | `assert` normal (el test falla solo si hay excepción) |

### Decisión 2.10 — Test positivo de Email agrupa formato y normalización

**Qué:** el test positivo de Email cubre dos comportamientos en un solo test:

```python
def test_email_normalizes_to_lowercase():
    email = Email("User@Example.com")
    assert email.value == "user@example.com"
```

**Por qué:** el assert prueba la normalización. El formato válido se prueba
**implícitamente**: si `Email("User@Example.com")` fuera rechazado por la
regex, lanzaría `ValueError` antes de llegar al `assert`, y el test fallaría
con ese error. Un tercer test que solo verificara «se guarda un email en
minúsculas» no probaría ningún camino de código nuevo. Dos tests (negativo

- positivo) cubren los tres comportamientos sin redundancia.

---

## Sesión 3 — Entidad Book: excepciones y atributos

> Fecha: 21 junio 2026

Arranca la entidad `Book`. Antes de escribir el primer test, hay que resolver
cuándo se crean las excepciones, con qué atributos nace `Book` y en qué orden
se escriben los tests de creación.

### Decisión 3.1 — `LibraryApiError` se crea ANTES del primer test de entidad

**Qué:** `LibraryApiError` no nace de un test concreto. Se crea como paso previo,
junto con `BookError` (su primera subclase), antes de ejecutar el test 2.1.

**Por qué:** `LibraryApiError` es infraestructura compartida. El test 2.1 solo
menciona `BookError`, pero `BookError(LibraryApiError)` no puede existir sin su
padre. Son un bloque atómico: se crean juntos.

La secuencia real del primer RED sería:

| # | Error | Qué crear |
|---|-------|------------|
| 1 | `NameError: name 'BookError' is not defined` | `class LibraryApiError(Exception): pass` + `class BookError(LibraryApiError): pass` |
| 2 | `NameError: name 'Book' is not defined` | `@dataclass class Book: ...` mínima |
| 3 | `BookError no fue lanzada` | Añadir validación en `__post_init__` |

Python busca `BookError` y, al no encontrarlo, falla en el paso 1. Pero al crear
`BookError`, el intérprete intenta resolver `LibraryApiError` en la herencia. Si
no existe, el error sería `NameError: name 'LibraryApiError' is not defined`.
Por eso se crean **las dos a la vez**, en un solo paso de RED.

> **Regla:** las excepciones de infraestructura (raíz de la jerarquía) se crean
> antes del test que las usa. Las excepciones específicas (`BookNotFoundError`)
> sí nacen de tests concretos (Paso 6.1).

### Decisión 3.2 — Atributos de `Book`: solo los que los tests piden

**Qué:** `Book` no nace con todos sus atributos definidos de antemano. Cada
atributo aparece cuando un test lo exige. El constructor evoluciona así:

```
Book(title, author)                              ← tests 2.1 y 2.2
Book(title, author, is_available=True)           ← test 3 (primer assert que nombra is_available)
Book(title, author, is_available=True, id=None)  ← tests de repositorio (cuando existan)
```

**Por qué:** en TDD estricto, la forma de la entidad la deciden los tests, no un
diseño previo. Cada campo se añade cuando hay un test que lo necesita:

| Campo | ¿Cuándo aparece? | Test que lo fuerza |
|---|---|---|
| `title: str` | Test 2.1 | `test_book_requires_title` — necesita un título para validar |
| `author: str` | Test 2.1 | El test usa `Book(title="", author="...")` — si `author` no existiera, el constructor fallaría |
| `is_available: bool = True` | Test 3 | `assert book.is_available is True` es el primer lugar donde se nombra el campo |
| `id: BookID \| None = None` | Tests de repositorio | El primer test que haga `assert book.id == 1` forzará a añadirlo |

Esto no significa que no sepamos el diseño final. Lo conocemos. Pero dejamos que
los tests **descubran** los atributos uno a uno, en vez de declararlos todos de
golpe. La diferencia es sutil pero importante: si declaras todo junto, estás
escribiendo código sin test. Si dejas que cada test añada lo que necesita, cada
línea de producción tiene un test que la justifica.

### Decisión 3.3 — Tests negativos antes que positivos (para entidades)

**Qué:** todos los tests negativos de creación de una entidad van **antes** que
el positivo. No se intercala negativo → positivo → negativo.

**Por qué:**

1. **Blindaje primero.** Los tests negativos son defensivos: protegen contra
   estados inválidos. Tiene sentido construir las murallas antes de celebrar
   que la casa se mantiene en pie.

2. **El positivo no forzaría nueva lógica.** Si intercalas un test positivo entre
   dos negativos, el positivo solo verifica comportamientos que ya existen — no
   obliga a escribir código nuevo. Es un test que nace verde, y un test que nace
   verde no aporta valor en TDD.

3. **El orden natural del dominio.** Cuando creas un libro, primero te asegurás
   de que no puede nacer roto (título vacío, autor vacío). Solo después confirmás
   que con datos válidos se crea correctamente.

```
Test 2.1 — negativo: título vacío
Test 2.2 — negativo: autor vacío
Test 3   — positivo: creación exitosa (prueba is_available, title, author)
```

> **Esto aplica a ENTIDADES, no a Value Objects.** En los VO (Email) el orden fue
> negativo → positivo porque solo hay un positivo. Con entidades, donde hay
> múltiples negativos, se agrupan todos antes del positivo.

### Decisión 3.4 — Type aliases solo para IDs, no para strings

**Qué:** se usan type aliases para distinguir IDs de distintas entidades
(`BookID = int`, `UserID = int`, `LoanID = int`). No se crean aliases para
atributos de tipo `str` (`BookTitle`, `BookAuthor`).

**Por qué:** un type alias en Python no crea un tipo nuevo — es un sinónimo.
Pyright no distingue `BookTitle` de `str`: son el mismo tipo. Por tanto, un
alias de string no previene errores:

```python
BookTitle = str
BookAuthor = str

book = Book(title=author_value, author=title_value)  # Pyright no se queja
```

Con IDs la situación es distinta. `int` se usa para muchas cosas (ids,
contadores, edades, cantidades). Un alias documenta la intención:

```python
BookID = int
UserID = int

def get_book(book_id: BookID) -> Book: ...      # Sé que es un ID de libro
def get_user(user_id: UserID) -> User: ...      # Sé que es un ID de usuario
```

`Email` no es un alias, es una **clase real** (`class Email`). Ahí sí hay
distinción de tipos para Pyright, y por eso se justifica.

**Regla:** alias solo cuando el mismo tipo base (`int`) tiene significados
distintos en el dominio. Para `str`, el nombre del campo en el dataclass
(`title: str`, `author: str`) ya documenta la intención.

### Decisión 3.5 — Validación hardcodeada, no automática con `vars()` o `fields()`

**Qué:** la validación de campos obligatorios en `__post_init__` se escribe
explícitamente, campo por campo. No se usan bucles sobre `vars(self)` ni
`fields(self)` para validar automáticamente todos los atributos.

**Por qué:**

1. **Un campo nuevo no debe validarse mágicamente.** Si añades `publisher: str`
   mañana, con validación automática se validaría sin que ningún test lo pida.
   Eso es código de producción sin test — viola TDD.

2. **Los campos opcionales rompen la validación automática.**
   `subtitle: str | None = None` o `notes: str = ""` dispararían `BookError`
   porque `not None` es `True` y `not ""` es `True`. Necesitarías una lista de
   excepciones, y eso ya es más complejo que la lista explícita.

3. **Trazabilidad TDD.** Cada campo obligatorio tiene su test negativo:

   ```
   test_book_requires_title  → if not self.title
   test_book_requires_author → if not self.author
   ```

   Con validación automática, un solo test cubriría varios campos. Si falla,
   no sabes cuál se rompió. Si alguien borra la validación por accidente,
   ningún test lo detecta porque nunca escribiste un test dedicado a ese campo.

4. **Código aburrido > código elegante.** Dos `if not` son más fáciles de leer
   y depurar que un bucle con `isinstance` y `getattr`. En TDD la prioridad es
   la seguridad, no la brevedad.

**Qué NO hacer:**

```python
# ❌ Validación automática — mágica, frágil con opcionales, sin trazabilidad
def __post_init__(self):
    for name, value in vars(self).items():
        if isinstance(value, str) and (not value or not value.strip()):
            raise BookError(f"Book must have {name}")
```

**Qué SÍ hacer:**

```python
# ✅ Validación explícita — aburrida, segura, trazable
def __post_init__(self):
    if not self.title or not self.title.strip():
        raise BookError("Book must have a title")
    if not self.author or not self.author.strip():
        raise BookError("Book must have an author")
```

> **Señal de refactor:** cuando los `if not` repetidos duelan (5+ campos),
> extraer a una lista `_REQUIRED = ["title", "author", ...]` con un bucle.
> Pero solo cuando duela, no antes. Los tests existentes protegen el cambio.

### Decisión 3.6 — Un assert por atributo en el test positivo

**Qué:** el test positivo de creación (`test_book_created_with_valid_data`)
tiene un `assert` independiente por cada atributo de la entidad. No se agrupan
en un solo assert genérico.

**Por qué:**

1. **Cada assert es un satélite de triangulación.** Si `assert book.title`
   falla, sabes exactamente qué campo no se asignó. Si usas un solo assert
   masivo y falla, no sabes cuál de los 4 campos es el culpable.

2. **Fuerza la existencia de cada campo.** El test positivo es el primer lugar
   donde `is_available` aparece nombrado. El assert `book.is_available is True`
   es lo que fuerza a añadir ese campo al dataclass — no aparece en los tests
   negativos.

3. **Documenta la forma completa de la entidad.** Leyendo el test positivo,
   sabes todos los atributos que tiene `Book` sin abrir `models.py`.

**El test completo:**

```python
def test_book_created_with_valid_data():
    book = Book(title="The Odyssey", author="Homer")
    assert book.title == "The Odyssey"
    assert book.author == "Homer"
    assert book.is_available is True
```

> **Importante:** `is_available` no existe aún en `Book`. Este test, en su
> fase RED, fallará con `AttributeError: 'Book' object has no attribute
> 'is_available'`. Ese rojo es el que fuerza a añadir el campo con default
> `True` al dataclass.

### Decisión 3.7 — Fases de aprendizaje TDD: de la creación al comportamiento

**Qué:** las entidades se construyen en fases progresivas. Cada fase responde
a una categoría distinta de preguntas sobre el dominio y enseña un patrón
de test diferente.

| Fase | Qué aprendés | Pregunta del dominio |
|------|-------------|---------------------|
| VO | Validar un dato aislado | ¿Este dato es correcto por sí mismo? |
| Creación | La entidad no puede nacer rota | ¿Qué campos son obligatorios? |
| Comportamiento | Métodos que consultan estado | ¿Qué me puede decir el objeto sobre sí mismo? |
| Transiciones | Métodos que cambian estado | ¿Qué acciones cambian el objeto? |
| Límites | Operaciones ilegales | ¿Qué no debería permitirse nunca? |
| Persistencia | Guardar y recuperar | ¿Cómo sobrevive el objeto entre ejecuciones? |
| Orquestación | Coordinar entidades | ¿Cómo interactúan varias entidades entre sí? |

> **Momento actual:** Creación de Book y User completada. En curso: Sesión 4
> — diseño de `Loan` (entidad asociativa) previo a la escritura de tests.

---

## Sesión 4 — Diseño de Loan (entidad asociativa)

> Fecha: 24 junio 2026

Antes de escribir el primer test, se resuelve el diseño completo de `Loan`:
atributos, validaciones, y la decisión sobre si referenciar por objeto o por ID.

### Decisión 4.1 — Loan referencia por ID, no por objeto

**Qué:** `Loan` usa `book_id: BookID` y `user_id: UserID`, no referencias directas
a `Book` y `User`.

**Por qué:** Stage 1 es en memoria, pero Stage 2 introduce base de datos.
Referenciar por ID desde el principio evita un refactor completo de `Loan` al
llegar a SQLAlchemy. Los type aliases `BookID` y `UserID` ya están definidos
(Decisión 3.4).

**Efecto en Book y User:** necesitan un campo `id: int | None = None`. Este
campo no requiere tests dedicados (ver apéndice, tabla de detección temprana):
su existencia se verifica **por uso** cuando el primer test de `Loan` falle con
`TypeError` al pasar `book_id=1` si `Book` no tiene `id`.

### Decisión 4.2 — Atributos de Loan

**Qué:** `Loan` nace con cinco atributos:

| Atributo | Tipo | Default | Significado |
|----------|------|---------|-------------|
| `book_id` | `BookID` (`int`) | — | Qué libro se prestó |
| `user_id` | `UserID` (`int`) | — | Quién lo pidió |
| `loan_date` | `date` | `date.today()` | Fecha del préstamo |
| `due_date` | `date` | `field(init=False)` → `loan_date + timedelta(days=30)` | Fecha límite de devolución |

> ⚠️ **Actualizado en 4.4:** `due_date` pasó de ser parámetro explícito a
> `field(init=False)` calculado automáticamente. Ver Decisión 4.4 para el
> razonamiento completo.
| `return_date` | `date \| None` | `None` | `None` = aún no devuelto |

> **Nota sobre `loan_date` y `default_factory`:**
>
> El default de `loan_date` se escribe `field(default_factory=date.today)`, no
> `= date.today()`. La diferencia:
>
> ```python
> # ❌ = date.today() — se evalúa UNA vez, al definir la clase
> loan_date: date = date.today()
> # Todas las instancias comparten la misma fecha (cuando se importó models.py)
>
> # ✅ default_factory=date.today — se evalúa al crear CADA instancia
> loan_date: date = field(default_factory=date.today)
> # Cada préstamo tiene la fecha del día en que realmente se creó
> ```
>
> Sin `default_factory`, la fecha queda congelada al momento de importar el
> módulo — todos los préstamos tendrían la misma fecha. Con `default_factory`,
> Python llama a `date.today()` cada vez que se instancia `Loan`.

**Por qué cada atributo:**

- `book_id` y `user_id` son la conexión mínima para una entidad asociativa.
- `loan_date` con default `date.today()` refleja que un préstamo siempre
  empieza «ahora». El servicio puede sobrescribirlo si necesita otra fecha.
- `due_date` **→ modificado en 4.4:** ahora se calcula automáticamente como
  `loan_date + timedelta(days=30)` mediante `field(init=False)`. El razonamiento
  original de 4.2 (política de negocio en el servicio, hecho del dominio,
  distintas duraciones por categoría) se reconsideró: en Stage 1 la duración
  es fija (30 días) y hacer imposible el estado inválido por construcción
  elimina la necesidad de un test negativo.
- `return_date` es opcional: `None` mientras el libro está prestado, toma
  valor cuando se ejecuta `return_book()`.

**Distinción `due_date` vs `return_date`:**

| | `due_date` | `return_date` |
|---|---|---|
| Naturaleza | Promesa | Hecho consumado |
| Responde a | ¿Para cuándo lo tengo que devolver? | ¿Cuándo lo devolvió? |
| Se fija en | Creación del préstamo | `return_book()` |
| Cambia | No | Solo una vez (de `None` a fecha) |
| Juntos permiten | — | `was_returned_late()`: ¿hubo retraso? |

**Atributos descartados:**

- `days: int` — redundante. `due_date - loan_date` lo calcula si alguna vez
  se necesita. No es un atributo del dominio, es un detalle de construcción.

**Progresión de `id` en las entidades:**

| Entidad | ¿Tiene `id` ahora? | ¿Quién lo fuerza? |
|---------|:-------------------:|--------------------|
| `Book` | ✅ Sí | `Loan.book_id` (el test de `Loan` falla con `TypeError` si `Book` no tiene `id`) |
| `User` | ✅ Sí | `Loan.user_id` (ídem) |
| `Loan` | ❌ No aún | El repositorio (`InMemoryDatabase`), más adelante |

`Loan` no recibe su `id` propio ahora porque nadie lo necesita todavía. Misma
regla de siempre: cada `id` nace cuando otra entidad o componente lo exige por
uso, no por anticipación.

### Decisión 4.3 — Validación única: `due_date > loan_date`

**Qué:** la única validación de dominio en `__post_init__` es que la fecha de
devolución sea posterior a la fecha de préstamo.

**Por qué:**

- `book_id` y `user_id` son `int` — sin validación de dominio. El tipo los
  protege. Su existencia se verifica por uso.
- `loan_date` tiene default sensato (`date.today()`). Validar que no sea
  futura añadiría complejidad sin un caso de uso real en Stage 1.
- `due_date` es el único campo cuya invariante puede romperse: `due_date`
  anterior o igual a `loan_date` es un sinsentido de dominio.
- `return_date` es opcional por definición — no hay invariante que proteger.

**Tests resultantes (fase 2 y 3):**

| # | Test | Fase |
|---|------|------|
| 1 | `test_loan_requires_due_date_after_loan_date` | 2 (−) |
| 2 | `test_loan_created_with_valid_data` | 3 (+) |

**Cadena de RED del test 1:** un solo test de `Loan` fuerza 4 cambios antes
de llegar al assert real. Es el mismo patrón que usamos con `Book` (Decisión
3.1): el test falla sobre el primer nombre no definido. La diferencia es que
aquí los primeros errores son `TypeError`, no `NameError`, porque `book_id` y
`user_id` fuerzan a que `Book` y `User` ganen un campo `id`.

```python
def test_loan_requires_due_date_after_loan_date():
    with pytest.raises(LoanError):
        Loan(book_id=1, user_id=1, loan_date=date.today(), due_date=date.today())
```

| # | Error real | Causa | Qué crear |
|---|-----------|-------|-----------|
| 1 | `TypeError: Book.__init__() got unexpected keyword argument 'id'` | `Loan` necesita `book_id=1` pero `Book` no tiene `id` | Añadir `id: BookID \| None = None` a `Book` |
| 2 | `TypeError: User.__init__() got unexpected keyword argument 'id'` | Ídem para `User` | Añadir `id: UserID \| None = None` a `User` |
| 3 | `NameError: name 'LoanError' is not defined` | No existe la excepción | Crear `class LoanError(LibraryApiError): pass` |
| 4 | `NameError: name 'Loan' is not defined` | No existe la clase | Crear `@dataclass class Loan: ...` mínima |
| 5 | `Failed: DID NOT RAISE LoanError` | `Loan` no tiene validación aún | Añadir `__post_init__` con validación `due_date` |
| 6 | ✅ GREEN | — | — |

> Los pasos 1 y 2 **no son tests de `id`** — no escribimos `test_book_has_id`
> ni `test_user_has_id`. Es el test de `Loan` forzando a que `Book` y `User`
> crezcan. Verificación por uso (ver apéndice, tabla de detección temprana).

**Lectura del nombre del test:**

```
test_loan_requires_due_date_after_loan_date
│          │         │
│          │         └── due_date > loan_date (la invariante)
│          └── "el préstamo exige que…"
└── entidad bajo test
```

El nombre no dice «debe existir el atributo `due_date`» — eso se verifica por
uso en el test positivo. El nombre describe la invariante de dominio: la fecha
límite de devolución (`due_date`) debe ser posterior a la fecha de préstamo
(`loan_date`).

**¿Por qué `due_date` y no `return_date` en el test negativo?**

| | `due_date` | `return_date` |
|---|---|---|
| Naturaleza | Promesa (fecha límite) | Hecho consumado (fecha real) |
| Se fija en | Creación del préstamo | `return_book()` (transición) |
| Invariante en creación | `> loan_date` | Ninguna — es `None` por definición |

`return_date` en creación siempre es `None` — no hay nada que validar. Su
invariante (`> loan_date`) se verifica en un test de transición, cuando se
ejecuta `return_book()`, no en uno de creación. Por eso el test negativo de
creación protege `due_date`, no `return_date`.

### Decisión 4.4 — `due_date` con `field(init=False)`: de validación runtime a invariante estructural

**Punto de partida — el test incompleto:**

El primer test de Loan se escribió con la intención de validar que
`due_date` debe ser posterior a `loan_date`. Quedó incompleto porque
faltaba cerrar la llamada a `Loan()` dentro del `with pytest.raises`:

```python
# Versión original incompleta
def test_loan_date_requires_due_date_after_loan_date():
    with pytest.raises(LoanError):
        loan = Loan(1, 1, )
        loan_date >= return_date
```

La lógica era correcta: crear un `Loan` con `due_date` igual o anterior a
`loan_date` debía lanzar `LoanError`. El test debía ser:

```python
# Versión que se pretendía escribir
def test_loan_requires_due_date_after_loan_date():
    with pytest.raises(LoanError):
        Loan(book_id=1, user_id=1, due_date=date.today(), loan_date=date.today())
```

**La pregunta que cambió el rumbo:** al revisar cómo crear `loan_date` y
`due_date`, surgió la cuestión: ¿`due_date` se pasa desde fuera o se calcula
automáticamente como `loan_date + 30 días`?

Se evaluaron dos opciones:

| Opción | `due_date` | Constructor | Flexibilidad |
|--------|-----------|-------------|-------------|
| A | `field(init=False)` — calculado siempre +30 | `Loan(book_id, user_id)` | Ninguna — 30 días fijos |
| B | Parámetro con default `None` → +30 si no se pasa | `Loan(book_id, user_id, due_date=...)` | El caller puede pasar otra duración |

Se eligió la **Opción A** para Stage 1: más simple, elimina la ambigüedad de
«¿quién decide la duración del préstamo?», y hace imposible el estado inválido
por construcción.

**La clase `Loan` resultante:**

```python
from datetime import date, timedelta
from dataclasses import dataclass, field

@dataclass
class Loan:
    book_id: BookID
    user_id: UserID
    loan_date: date = field(default_factory=date.today)
    return_date: date | None = None
    loan_id: LoanID | None = None
    due_date: date = field(init=False)          # ← no es parámetro, va al final

    def __post_init__(self):
        self.due_date = self.loan_date + timedelta(days=30)
```

**Por qué `init=False` y no `default_factory`:**

Podrías pensar en usar `default_factory` con una lambda para calcular
`due_date` automáticamente:

```python
# ❌ NO funciona
due_date: date = field(default_factory=lambda: loan_date + timedelta(days=30))
```

El problema es simple: `loan_date` no existe en ese scope. La lambda se
ejecuta sola, sin contexto, sin `self`. Es literalmente como escribir
`loan_date + timedelta(days=30)` en una línea suelta de Python — da
`NameError`. No es que «no vea otros campos» como concepto abstracto:
es que la variable no está definida ahí.

Con `init=False` + `__post_init__`, para cuando `__post_init__` se ejecuta,
`self.loan_date` ya tiene valor (lo asignó el `__init__` automático). Por
eso funciona.

> ⚠️ **Orden de campos:** `due_date` va al final de la clase, después de todos
> los campos con default. Aunque `init=False` lo excluye del constructor,
> Python lo cuenta como «campo sin default» para la validación de orden.
> Ponerlo entre `loan_date` (con default) y `return_date` (con default)
> produce `TypeError: non-default argument 'due_date' follows default argument`.

**Consecuencia en los tests — del negativo al positivo:**

El test negativo original (`test_loan_requires_due_date_after_loan_date`)
ya no tiene razón de ser. Con `init=False`, `due_date` siempre se calcula
como `loan_date + 30`. No existe forma de pasar un `due_date` inválido porque
**no existe forma de pasar `due_date` en absoluto**. La validación pasó de ser
runtime (`if due_date <= loan_date: raise LoanError`) a ser estructural:
está garantizada por cómo se construye el objeto.

En su lugar nace un test positivo:

```python
from datetime import timedelta

from app.models import Loan


def test_loan_due_date_is_loan_date_plus_30_days():
    loan = Loan(book_id=1, user_id=1)
    assert loan.due_date == loan.loan_date + timedelta(days=30)
```

**Qué verifica el test:** un único assert que comprueba la relación
`due_date == loan_date + 30`. No necesita fecha hardcodeada porque en Stage 1
no existe ningún camino donde `loan_date` sea distinto de `date.today()`.
Ver la Decisión 4.5 para el razonamiento completo.

**`LoanError` tras este cambio:**

Con la Opción A, `Loan` no tiene ninguna validación runtime. `LoanError`
queda definida como clase pero ningún código la lanza. En TDD puro, si
ningún test espera una excepción, esa excepción no debe existir. Se elimina.
Volverá a nacer cuando el primer test negativo de `Loan` (devoluciones,
préstamo duplicado) la exija.

**Qué enseña esta decisión sobre diseño de entidades:**

Cuando una invariante «X debe ser mayor que Y» se cumple siempre porque X
se calcula a partir de Y, has encontrado una **invariante estructural**, no
de negocio. Las invariantes estructurales no se testean con negativos — se
testean con positivos que verifican el cálculo. Las invariantes de negocio
(«un libro prestado no puede prestarse otra vez») sí necesitan test negativo
porque dependen de decisiones externas (alguien llamó a `loan()` dos veces).

> **Regla:** si puedes hacer imposible un estado inválido por construcción,
> hacelo. Es más barato que vigilarlo con tests.

### Decisión 4.5 — Un solo test: eliminación del test con fecha hardcodeada

El test con fecha explícita (`loan_date=date(2026, 1, 1)`) se escribió por
inercia de triangulación: «dos puntos de datos fuerzan la solución general,
pongamos uno con fecha explícita y otro con default». Pero la triangulación
solo tiene sentido cuando cada punto de datos por separado admite una solución
hardcodeada distinta. Aquí no: en Stage 1, `loan_date` siempre es
`date.today()`. No existe ningún flujo donde `loan_date` tome otro valor.

**El error:** se aplicó el patrón de triangulación sin verificar si el
segundo punto de datos realmente fuerza algo que el primero no pueda forzar.
El test con fecha hardcodeada protegía contra una implementación tramposa
(`self.due_date = date.today() + 30` en vez de `self.loan_date + 30`) que,
como `loan_date` siempre coincide con `date.today()` en la práctica del
Stage 1, nunca se manifestaría como bug. Es triangulación vacía: el segundo
punto de datos no añade cobertura real.

**El test final:**

```python
from datetime import timedelta

from app.models import Loan


def test_loan_due_date_is_loan_date_plus_30_days():
    loan = Loan(book_id=1, user_id=1)
    assert loan.due_date == loan.loan_date + timedelta(days=30)
```

Un solo test que verifica la relación que importa: `due_date` depende de
`loan_date`, sea cual sea. Si alguien rompe esa relación, el test falla.
No necesita fecha hardcodeada porque no hay ningún camino por el que
`loan_date` tome otro valor.

> **Principio:** si no hay caso de uso para `loan_date != date.today()`,
> el test con fecha hardcodeada es ruido. La triangulación no se aplica
> mecánicamente: requiere que existan al menos dos caminos de ejecución
> distintos que ejerciten la misma invariante.

### Decisión 4.6 — Test de creación completa: consistencia con Book y User

Tanto `Book` como `User` tienen un test de creación completa que documenta
el contrato público de la entidad:

```python
# Book
def test_book_created_with_valid_data():
    book = Book(title="The Odyssey", author="Homer")
    assert book.title == "The Odyssey"
    assert book.author == "Homer"
    assert book.is_available is True

# User
def test_user_created_with_valid_data():
    user = User("hector", Email("hector@gmail.com"))
    assert user.username == "hector"
    assert user.email.value == "hector@gmail.com"
```

`Loan` no tenía el suyo. El test existente solo verificaba `due_date`.
Se añade:

```python
from datetime import date, timedelta

from app.models import Loan


def test_loan_created_with_valid_data():
    loan = Loan(book_id=1, user_id=1)
    assert loan.book_id == 1
    assert loan.user_id == 1
    assert loan.loan_date == date.today()
    assert loan.return_date is None
    assert loan.loan_id is None
```

**Qué verifica cada assert:**

| Atributo | Assert | Qué garantiza |
|----------|--------|---------------|
| `book_id` | `== 1` | El ID pasado se conserva |
| `user_id` | `== 1` | Ídem |
| `loan_date` | `== date.today()` | El default `date.today()` se aplica correctamente |
| `return_date` | `is None` | El préstamo nace sin devolución |
| `loan_id` | `is None` | El préstamo no tiene ID hasta que el repositorio se lo asigne |

**Por qué `loan_date == date.today()` y no un valor hardcodeado:**

Igual que `test_book_created_with_valid_data` no pasa `is_available=True`
explícitamente —usa el default y lo verifica—, este test no pasa `loan_date`
explícitamente. Hardcodear `loan_date=date(2026, 1, 1)` repetiría el error de
la Decisión 4.5: añadir un valor explícito sin un caso de uso real que lo
ejerza. El default `date.today()` es parte del contrato público de `Loan`,
exactamente igual que `is_available=True` lo es de `Book`.

> **Regla de consistencia:** el test de creación completa de una entidad
> debe pasar solo los parámetros obligatorios (sin repetir los defaults)
> y verificar todos los atributos visibles, incluyendo los que tienen
> default. Si el default cambia, el test lo detecta.

### Guía de diseño de entidades — las 5 preguntas

El diseño de `Loan` expuso un patrón de razonamiento que aplica a cualquier
entidad nueva. Son 5 preguntas en orden:

**1. ¿Qué conecta y cómo?**

Si es una entidad asociativa, conecta dos o más entidades existentes. La
decisión es: ¿referencia por objeto o por ID? Por ID si Stage 2 está cerca;
por objeto si la API es puramente en memoria y no habrá persistencia.

**2. ¿Qué atributos le pertenecen solo a ella?**

Atributos que ninguna de las entidades conectadas tiene. Son los *hechos del
dominio* de esta entidad. Si un atributo pertenece a otra entidad (`title` es
de `Book`, `email` es de `User`), no va aquí.

**3. ¿Qué invariante de dominio protege?**

¿Qué combinación de valores es un sinsentido en el negocio? Toda entidad
protege al menos una invariante. Si no encontrás ninguna, es sospechoso.

**4. ¿Qué atributos parecen necesarios pero no lo son?**

Aplicá la navaja: si puedes derivarlo de otros atributos, no lo almacenás.
Pero cuidado: no todo lo derivable es falso. Preguntate si es un *hecho del
dominio* (se almacena) o un *detalle de construcción* (se descarta).

**5. ¿Qué tests nacen de esto?**

De las preguntas 2 y 3 salen los tests: un negativo por cada invariante + un
positivo que verifica todos los atributos con asserts. Si la entidad tiene 1
invariante → 2 tests. Si tuviera 3 invariantes → 4 tests (3 negativos + 1
positivo).

**Ficha resumen:**

| Pregunta | Ejemplo con Loan |
|----------|-----------------|
| ¿Qué conecta y cómo? | `Book` + `User`, por ID (`book_id`, `user_id`) |
| ¿Atributos propios? | `loan_date`, `due_date`, `return_date` |
| ¿Invariante? | Estructural: `due_date = loan_date + 30` (garantizada por construcción, no necesita test negativo) |
| ¿Atributos falsos? | `days` (derivable de `due_date - loan_date`) |
| ¿Tests? | 2 positivos (ver 4.4, 4.5 y 4.6) |

---

## Patrones y principios descubiertos

> Los patrones no se estudian de antemano. Emergen de los tests y se
> documentan cuando se reconocen. Esta sección crece con el proyecto.

| Patrón / Principio | Fuente | Dónde aparece | Qué resuelve |
|---|---|---|---|
| **Value Object** | DDD (Eric Evans) | `Email` | Objeto sin identidad, inmutable, igualdad por valor |
| **Entity** | DDD (Eric Evans) | `Book` | Objeto con identidad (ID futuro), muta estado |
| **CQS** | Bertrand Meyer | `can_be_loaned()` vs `loan()` | Las preguntas nunca fallan; las acciones sí pueden |
| **Encapsulación** | OOP | `can_be_loaned()` oculta `is_available` | El campo es interno, el método es contrato público |
| **Guard Clause** | Refactoring (Fowler) | `if not self.title: raise BookError(...)` | Rechazar estados inválidos al entrar, no al final |
| **Exception Hierarchy** | Decisión de diseño | `LibraryApiError → BookError → BookAlreadyLoanedError` | Atrapar por nivel de especificidad sin enumerar excepciones |

> **Distinción importante:** OOP da la sintaxis (clases, herencia). DDD da el
> significado (¿esto se identifica por valor o por ID?). Value Object y Entity
> no son conceptos de OOP — nacen del diseño guiado por el dominio.

> Esta sección es la referencia práctica. Leela cuando vayas a escribir código.
> Las decisiones de arriba explican el porqué de cada regla; aquí está el cómo.

---

## Decisión de infraestructura — Hook pre-push `check-tests`

### Contexto

El TDD tiene reglas que requieren criterio humano (triangulación, refactor,
orden RED→GREEN) y una regla que es puramente mecánica: **si cambias código de
producción, deben cambiar tests.**

Las skills de Gentle-Pi (`work-unit-commits`, `gentle-ai`) son pasivas:
dependen de que el agente recuerde aplicarlas. En sesiones largas, las
instrucciones del system prompt se diluyen y el agente puede commitear código
de producción sin tests. El análisis completo de este problema está en
`project_docs/config-map.md`, sección "Por qué falla la aplicación de reglas".

### Decisión

**Crear un hook de pre-push (`check-tests`) que bloquee el push cuando hay
cambios en `src/app/` sin cambios correspondientes en `src/tests/`.**

El hook se ejecuta en `pre-push`, no en `pre-commit`, para no mezclar capas
de enforcement: tipado y formato son corrección inmediata (no deberías ni
committear sin ellos); la presencia de tests es disciplina de entrega (se
verifica al empujar). Si el hook da un falso positivo (cambio cosmético),
`--no-verify` en push no sacrifica `pyright` ni `ruff`.

### Las tres preguntas que llevaron a esta decisión

| Pregunta | Respuesta |
|---|---|
| ¿Hooks en vez de extensiones para Python? | **Sí.** Las extensiones de Pi son TypeScript. Un proyecto Python no debería depender de una pila TS para enforcement de git. |
| ¿Un hook para work-unit-commits? | **Sí.** Es la única regla del TDD que se puede codificar sin criterio humano. Las demás (triangulación, refactor, orden RED→GREEN) requieren juicio — para eso está el Gentleman. |
| ¿En pre-commit o pre-push? | **Pre-push.** Tipado y formato (pyright, ruff) deben bloquear el commit. La disciplina de tests se verifica al empujar. Separar capas evita que un falso positivo del hook de tests te obligue a saltarte también pyright. |

### Qué se creó

| Archivo | Rol |
|---|---|
| `scripts/check_tests.py` | Script Python que implementa la regla binaria: cambios en `src/app/` → cambios en `src/tests/` requeridos. |
| `.pre-commit-config.yaml` | Nuevo hook `check-tests` con `stages: [pre-push]`. |

### Comportamiento verificado

| Escenario | Resultado |
|---|---|
| Sin cambios en producción | ✅ Pass (skip) |
| Producción sin tests | ❌ Bloquea — mensaje claro con los archivos ofensores |
| Producción + tests | ✅ Pass |

### Lo que el hook NO verifica — y por qué es deliberado

El hook es binario y opera a nivel de **archivos**, no de métodos o líneas.
No casa `models.py` con `test_book.py` — solo comprueba que haya al menos
un archivo en `src/tests/` si hay al menos uno en `src/app/`.

**No verifica:**

| No verifica… | Porque… |
|---|---|
| Que el test corresponde al método cambiado | Requiere entender el código — criterio humano |
| Que hay un test por cada función o clase nueva | Ídem |
| Cobertura de líneas o ramas | Herramienta aparte: `pytest --cov` |
| Que el test realmente prueba el cambio | Podrías stagiir un test vacío y pasaría — el Gentleman debe revisarlo |
| Que los tests pasan | Eso lo garantizan `pyright` + `pytest`, hooks independientes |

**Ejemplo concreto** que aclara la granularidad:

```
Cambias models.py para añadir User entity.
Stageas src/app/models.py + src/tests/test_user.py

✅ El hook pasa. No le importa que test_book.py no esté staged.
   Solo mira: ¿hay algo en src/app/? ¿Hay algo en src/tests/? → Sí a ambas.
```

El hook es deliberadamente tonto. Un hook más fino (parsear el diff para
detectar qué cambió, mantener un mapa de archivos, distinguir cambios
cosméticos de cambios de comportamiento) sería frágil y se rompería con
cada refactor. La granularidad fina la da el criterio del Gentleman durante
la sesión.

### El flag `--no-verify` — válvula de escape, no atajo

`git push --no-verify` **bypassea el hook `check-tests`**, pero no afecta
a los hooks de `pre-commit` (pyright, ruff, check-language) porque se
ejecutan en stages distintos.

**Casos legítimos:**

| Escenario | ¿Legítimo? | Por qué |
|---|---|---|
| Cambiaste un docstring/typo en `models.py`, sin tests necesarios | ✅ Sí | Falso positivo del hook — no hay comportamiento que testear |
| Arreglaste un comentario, Pyright y Ruff ya pasaron en el commit | ✅ Sí | La corrección ya está verificada |
| Te saltas `check-tests` porque no escribiste tests | ❌ No | Estás violando TDD — el hook está funcionando exactamente como debe |

> **Regla:** `--no-verify` existe para cuando el **hook se equivoca**, no para
> cuando **tú te equivocas**. Separar `check-tests` en `pre-push` hace que
> este bypass no sacrifique `pyright` ni `ruff` — solo afecta al hook de tests.

### La foto completa de los hooks, sin ambigüedad

| Componente | Ubicación | Qué es |
|---|---|---|
| Configuración de hooks | `library-api/.pre-commit-config.yaml` | **Un solo archivo.** Define 7 hooks, algunos en `pre-commit`, uno en `pre-push` |
| Script `pre-commit` | `.git/hooks/pre-commit` | Generado por `pre-commit install`. Delega al framework |
| Script `pre-push` | `.git/hooks/pre-push` | Generado por `pre-commit install --hook-type pre-push`. Ídem |
| `check-language` | `/home/heks/.local/bin/check-language` | Script Python independiente, en el PATH del sistema, llamado por el hook |
| `check-tests` | `scripts/check_tests.py` | Script Python del proyecto, llamado por el hook |

**Flujo real:**

```
git commit
  └─→ .git/hooks/pre-commit
       └─→ pre-commit framework
            └─→ lee .pre-commit-config.yaml
                 └─→ ejecuta hooks con stages: [pre-commit]
                      ├── check-venv
                      ├── pyright
                      ├── check-language  → /home/heks/.local/bin/check-language
                      ├── ruff
                      └── ruff-format

git push
  └─→ .git/hooks/pre-push
       └─→ pre-commit framework
            └─→ ejecuta hooks commit-stage + push-stage:
                 ├── pyright          (pre-commit, re-verifica)
                 ├── ruff             (pre-commit, re-verifica)
                 ├── ruff-format      (pre-commit, re-verifica)
                 └── check-tests      (pre-push)  → scripts/check_tests.py
```

> **Comportamiento de pre-commit:** `pre-push` ejecuta tanto los hooks de
> `pre-commit` como los de `pre-push`. No es un bug — es una ventaja:
> el push re-verifica tipado y linting por si algo se coló entre commit y push.

### Por qué un hook y no una extensión de Pi

- **Extensión de Pi:** código TypeScript que intercepta tool calls del agente.
  Para un proyecto Python, añadir una pila TS solo para validar commits es
  atacar el problema en la capa equivocada.
- **Hook de pre-commit:** código que se ejecuta en git, independiente del
  agente. Es inmune a la dilución de prompt y a la amnesia post-compaction.
  No depende de que el Gentleman "recuerde" nada — git lo ejecuta siempre.

> **Regla general:** si la validación es sobre un `git commit`, el enforcement
> vive en git hooks. Si la validación es sobre el comportamiento del agente
> (qué herramientas usa, qué lee antes de actuar), ahí sí es extensión de Pi.
> No mezclar capas.

---

## Apéndice

Guía TDD paso a paso — referencia práctica.

### Reglas antes de empezar

1. **Test primero, siempre.** No escribas ni una línea de producción sin un test que falle.
2. **AAA en cada test.** Arrange (preparas) → Act (ejecutas) → Assert (verificas). Separa los bloques con línea en blanco.
3. **RED primero, sin excepción.** Ejecuta el test y mira cómo falla antes de implementar. Si no ves el rojo, no sabes si el test realmente prueba algo: un test sin `assert` siempre está en verde y no prueba nada.
4. **Código mínimo para GREEN.** Sin adornos, sin anticipar necesidades futuras, sin refactorizar antes de tiempo. El refactor tiene su propia fase después del verde, con los tests como red de seguridad. Si mezclas implementación y refactor, pierdes el rastro de qué cambio rompió qué.
5. **Triangula cuando dudes.** Si no estás seguro de que tu implementación es genérica, escribe un segundo test con datos distintos.
6. **Las excepciones nacen del test.** Si un test negativo espera una excepción custom, el primer RED será `NameError` sobre esa excepción. Créala antes que la entidad.

> **Nota sobre parámetros:** un test no recibe en su signatura los parámetros de
> la función que prueba. El test es quien **llama** a la función y le **pasa** los
> valores desde dentro del cuerpo. La función los recibe; el test los proporciona.
> No intentes copiar la signatura de la función al test — no funciona así.

### Ciclo RED → GREEN → TRIANGULATE → REFACTOR

```
Pregunta del dominio
        │
        ▼
┌──────────────────┐
│ 1. RED           │  Escribes el test. Lo ejecutas: FALLA.
│    ↓              │  El error te dice exactamente qué falta.
│ 2. GREEN         │  Escribes el MÍNIMO código para que pase.
│    ↓              │  Lo ejecutas: PASA.
│ 3. TRIANGULATE   │  ¿Funciona con otros datos? Si no estás seguro,
│    ↓              │  escribes otro test con valores distintos.
│ 4. REFACTOR      │  Ahora sí: limpias, renombras, extraes,
└──────────────────┘  eliminas duplicación. Los tests siguen en verde.
        │
        ▼
Siguiente pregunta del dominio
```

### Triangulación: qué es y cuándo usarla

#### El problema que resuelve

En la fase GREEN escribimos el **código mínimo** para que el test pase. A veces eso
significa hacer trampa: devolver un valor fijo (hardcodeado) en vez del algoritmo real.

```python
def test_shipping_one_book():
    assert calculate_shipping(quantity=1) == 5
```

GREEN con trampa:

```python
def calculate_shipping(quantity):
    return 5  # Funciona para quantity=1, pero no es el algoritmo real
```

El test pasa, pero sabes que el código está mal. Aquí entra la triangulación.

#### Cómo funciona

El nombre viene de la navegación por GPS: con un solo satélite sabes que estás en
algún lugar de un radio enorme, pero necesitas **dos o tres satélites que se crucen**
para obtener tus coordenadas exactas.

En TDD funciona igual:

1. **Primer satélite (Test 1):** escribes un test con un caso concreto.
2. **Segundo satélite (Triangular):** escribes un **segundo test** para el mismo
   comportamiento pero con datos de entrada distintos. Este nuevo test **falla** (RED)
   porque el código tramposo no puede satisfacer ambos a la vez.
3. **Coordenada exacta (Algoritmo real):** la única forma de poner ambos tests en
   verde es escribir la lógica general.

```python
# Test 2 — fuerzas que el código deje de hacer trampa
def test_shipping_two_books():
    assert calculate_shipping(quantity=2) == 10

# GREEN — ahora sí, algoritmo real
def calculate_shipping(quantity):
    return quantity * 5
```

#### Cuándo triangular (y cuándo no)

| Triangula cuando… | No hace falta triangular cuando… |
|---|---|
| El algoritmo es complejo y no ves el patrón de inmediato | Desde el primer test sabes exactamente la fórmula |
| Quieres blindar una regla de negocio con casos límite | El código mínimo ya es obviamente genérico |
| Dudas de si tu implementación es realmente general | El comportamiento es trivial (getter, asignación) |
| Escribiste el constructor a mano (`def __init__`) | El constructor lo genera `@dataclass` — Python lo hace genérico por ti |

#### Por qué `@dataclass` no necesita triangulación

La triangulación existe para cazar **código escrito a mano que hace trampa**.
El constructor de `@dataclass` no está escrito a mano — lo genera Python.

```python
# Constructor escrito a mano — PUEDES hacer trampa
class BookManual:
    def __init__(self, title, author):
        self.title = "The Odyssey"    # hardcodeado, ignora el parámetro
        self.author = author
```

El test con `BookManual("Dune", "Herbert")` pasa en GREEN aunque `title`
se haya hardcodeado. Necesitas un segundo test con `"Foundation"` para
exponer la trampa.

```python
# @dataclass — constructor GENERADO por Python
@dataclass
class Book:
    title: str
    author: str

# Python genera esto automáticamente:
# def __init__(self, title: str, author: str):
#     self.title = title      # ← no hay espacio para hardcodear
#     self.author = author
```

El código generado es **genérico por construcción**. No hay un `if` donde
esconder un valor fijo. No hay un programador humano que pueda decidir
"devuelvo `\"The Odyssey\"` siempre". Python pone `self.title = title` — punto.

> **Regla:** triangulas código que escribes. No triangulas código que genera
> Python. Es como testear `1 + 1 == 2` y luego "triangular" con `2 + 2 == 4` —
> no estás probando tu código, estás probando el intérprete.

> **Caso concreto de este proyecto:** `test_book_created_with_other_valid_data`
> y `test_user_created_with_other_valid_data` se eliminaron porque triangulaban
> constructores de `@dataclass`. El decorador genera `__init__` genérico — no hay
> código tramposo que cazar. La triangulación con dataclass no triangula nada.

No es necesario triangular absolutamente todo. Es una **herramienta para cuando dudas**,
no un ritual obligatorio.

### Cuándo nacen las excepciones

En TDD, las clases de excepción **nacen de los tests negativos**. Cada
`pytest.raises(MiError)` te fuerza a crear `MiError` antes de crear lo que sea
que lanza el error.

Cuando escribes un test:

```python
def test_book_requires_title():
    with pytest.raises(BookError):
        Book(title="", author="Herbert")
```

El ciclo RED → GREEN se descompone en **varios rojos encadenados**:

| # | Acción | Error obtenido | Qué crear |
|---|--------|---------------|------------|
| 1 | Ejecutas el test | `NameError: name 'BookError' is not defined` | `class BookError(LibraryApiError): pass` |
| 2 | Vuelves a ejecutar | `NameError: name 'Book' is not defined` | `@dataclass class Book: ...` mínima |
| 3 | Vuelves a ejecutar | `BookError no fue lanzada` | Añades validación en `__post_init__` |
| 4 | Vuelves a ejecutar | ✅ GREEN | — |

**Regla:** el test falla sobre el **primer nombre no definido** que encuentra.
Si la excepción no existe, ni siquiera llega a evaluar si la entidad existe.
Por eso la excepción se crea **antes** que la entidad.

#### Built-in vs custom

| Usa excepción built-in cuando… | Crea excepción custom cuando… |
|---|---|
| El error es genérico, no pertenece a tu dominio | El error es específico de las reglas de tu dominio |
| `ValueError`, `TypeError` bastan | Necesitas atrapar ESE error concreto más arriba |
| Estás en un Value Object simple (Email) | Estás en lógica de negocio (`BookAlreadyLoanedError`) |

Jerarquía del proyecto:

```
LibraryApiError          ← raíz (se crea antes del primer test de entidad)
├── BookError            ← tests negativos de creación de Book
│   ├── BookNotFoundError      ← búsqueda por ID
│   └── BookAlreadyLoanedError ← caso límite "no prestar dos veces"
├── UserError            ← tests negativos de creación de User
└── LoanError            ← tests de lógica de préstamo
```

`LibraryApiError` es la única excepción que no nace de un test concreto: nace
de una decisión de diseño. Se crea antes del primer test de entidad.

#### ¿Por qué un ancestro común?

1. **Separa errores de dominio de errores inesperados.**
   `except LibraryApiError` atrapa todos los errores conocidos y permite
   traducirlos a respuestas HTTP controladas (404, 409, 422…). Si algo que
   **no** es `LibraryApiError` escapa, es un bug (500).

2. **No te obliga a repetir listas de excepciones.**
   Sin ancestro, cada `except` tendría que enumerar todas las excepciones.
   Con `LibraryApiError`, un solo `except` cubre las presentes y las futuras.

3. **Permite evolucionar los errores sin tocar quien los atrapa.**
   Si añades `status_code` a `LibraryApiError`, todas las subclases lo heredan.

### Orden de trabajo

> **Regla:** completa cada fase para **todas** las entidades antes de pasar a la
> siguiente. No avances de Creación a Comportamiento hasta que todas las entidades
> (Book, User, Loan) sepan nacer correctamente.
>
> **Por qué:** las fases avanzadas dependen de entidades que aún no existen.
> No puedes testear `loan()` (Estados) sin User. No puedes testear casos límite
> de Loan sin Book y User. La creación completa del dominio es el prerequisito
> de todo lo demás.

| Orden | Fase | Qué construyes | Tipo de tests | Patrón |
|---|---|---|---|---|
| 1º | VO | Value Objects (Email) | Negativos + Positivos | `pytest.raises` + `assert vo.atributo == valor` |
| 2º | Creación (−) | **Todas las entidades** — no pueden nacer rotas | Negativos | `pytest.raises(EntidadError)` |
| 3º | Creación (+) | **Todas las entidades** — creación exitosa | Positivos | `assert entidad.atributo == valor` |
| 4º | Comportamiento | **Todas las entidades** — métodos que consultan estado | Positivos | `assert entidad.metodo() == esperado` |
| 5º | Estados | Entidad — transiciones que mutan estado | Positivos | `assert entidad.estado is True/False` |
| 6º | Casos límite | Entidad — blindaje contra operaciones ilegales | Negativos | `pytest.raises(EntidadError)` |
| 7º | Revisión de diseño | Manual, sin test | — | ¿El código toca la BD? ¿Sabe de fechas? |

### Paso 1 — Value Objects (datos pequeños)

**Objetivo:** asegurar que los datos que componen la entidad son válidos por sí mismos.

#### 1.1 — Test negativo del VO

```python
# ARRANGE: nada
# ACT + ASSERT
def test_email_requires_at_sign():
    with pytest.raises(ValueError):
        Email("sin_arroba.com")
```

**RED esperado:** `NameError: name 'Email' is not defined`. `ValueError` es built-in
de Python, así que no necesitas crearlo.

**GREEN — código mínimo:**

```python
class Email:
    def __init__(self, value: str):
        if "@" not in value:
            raise ValueError("Email must contain @")
        self.value = value
```

#### 1.2 — Test positivo del VO

```python
def test_email_stores_valid_value():
    # ARRANGE + ACT
    email = Email("user@example.com")
    # ASSERT
    assert email.value == "user@example.com"
```

> **Sin triangulación:** el constructor de `@dataclass(frozen=True)` es
> genérico por construcción. No hay código tramposo que cazar.

### Paso 2 — Entidad: tests negativos (la entidad no puede nacer rota)

**Objetivo:** la entidad rechaza su creación si faltan piezas fundamentales.

> **Orden:** todos los tests negativos de creación van **antes** del positivo.
> Primero blindas la entidad contra estados inválidos (2.1 título, 2.2 autor).
> Luego confirmas que con datos válidos se crea correctamente (Paso 3). Si
> intercalas positivo entre negativos, estás escribiendo un test que no fuerza
> nueva lógica — el positivo solo prueba comportamientos que ya existen.

#### ¿Cuándo escribir un test negativo dedicado?

No todo atributo necesita test negativo. La regla la da el sistema de
**detección temprana** — quién atrapa el error primero:

| Atributo | Tipo | Valor inválido | ¿Instancia del tipo? | ¿Quién lo atrapa? | ¿Test negativo? |
|---|---|---|---|---|---|
| `Book.title` | `str` | `""` | ✅ Sí — `""` es `str` | **Runtime** (`__post_init__`) | ✅ Necesario |
| `User.username` | `str` | `""` | ✅ Sí — `""` es `str` | **Runtime** (`__post_init__`) | ✅ Necesario |
| `User.email` | `Email` | `"no soy email"` | ❌ No — `str` no es `Email` | **Pyright** (type checker) | ❌ No necesario |
| `Book.author` | `str` | `""` | ✅ Sí — `""` es `str` | **Runtime** (`__post_init__`) | ✅ Necesario |
| `Book.id` | `int \| None` | — | No hay valor inválido posible | **Por uso** (otra entidad lo exige) | ❌ No necesario |
| `User.id` | `int \| None` | — | No hay valor inválido posible | **Por uso** (otra entidad lo exige) | ❌ No necesario |

> **Regla:** si el valor inválido **engaña al type checker** (ej: `""` es un
> `str` válido para Python pero inválido para el dominio), necesitas un test
> negativo. Si el type checker lo rechaza en tiempo de análisis (ej: pasar
> `str` donde se espera `Email`), el tipo ya es tu test.
>
> **Ejemplo concreto:** `User` no tiene test negativo de email. Si alguien
> intenta `User(username="john", email="bad")`, Pyright marca error antes de
> que pytest corra. Si alguien borra el campo `email` del modelo, el test
> positivo `test_user_created_with_valid_data` truena con `AttributeError`
> al hacer `user.email`. El campo se verifica **por uso**, no por test dedicado.
>
> **Ejemplo concreto:** `Book` y `User` no tienen test de `id`. El campo `id` es
> `int | None` con default `None`. No hay regla de dominio que validar (no hay
> «id debe ser positivo»). Su existencia se verifica **por uso**: cuando `Loan`
> pida `book_id` y `user_id`, si `Book` o `User` no tienen `id`, el test de
> `Loan` falla con `TypeError`. Ese fallo es el que fuerza a añadir el campo —
> sin un test dedicado para `book.id` o `user.id`.

#### ¿Cuándo normalizar un campo en `__post_init__`?

No todo `str` debe bajarse a lowercase. La decisión depende de si existe
un **estándar externo** que defina la equivalencia:

| Campo | ¿Normalizar? | ¿Por qué? |
|---|---|---|
| `Email.value` | ✅ Sí | RFC 5321: `User@Example.com` y `user@example.com` son la misma dirección. No normalizar es incorrecto. |
| `User.username` | ❌ No | No hay estándar. `JohnDoe` y `johndoe` pueden ser el mismo usuario o dos distintos — es decisión de producto, no técnica. |

La case-sensitivity se resuelve en la **capa correcta**, no en el modelo:

| Capa | ¿Dónde? | ¿Cuándo? |
|---|---|---|
| Dominio | `User.username` guarda lo que el usuario escribió | Ahora (Stage 1) |
| Persistencia | `UNIQUE COLLATE NOCASE` en SQLite | Stage 2 |
| Búsqueda | `repo.find_by_username()` compara case-insensitive | Stage 1 (Repository) |

> **Regla:** el modelo preserva lo que el usuario escribió. La comparación y
> unicidad se delegan a la capa que sabe del storage. No mezclar capas en
> `__post_init__` solo porque "algún día habrá base de datos".

#### 2.1 — Test negativo: título vacío

```python
def test_book_requires_title():
    with pytest.raises(BookError):
        Book(title="", author="Herbert")
```

**RED esperado (secuencia):**

1. `NameError: name 'BookError' is not defined` → creas `class BookError(LibraryApiError): pass`
2. `NameError: name 'Book' is not defined` → creas la clase `Book` mínima
3. `BookError no fue lanzada` → añades la validación

**GREEN — código mínimo (tras los 3 rojos):**

```python
# exceptions.py
class BookError(LibraryApiError):
    """Raised for general book-related failures."""
    pass

# models.py
@dataclass
class Book:
    title: str
    author: str

    def __post_init__(self):
        if not self.title or not self.title.strip():
            raise BookError("Book must have a title")
```

#### 2.2 — Test negativo: autor vacío

```python
def test_book_requires_author():
    with pytest.raises(BookError):
        Book(title="Dune", author="")
```

**GREEN:** añadir validación de autor en `__post_init__`:

```python
def __post_init__(self):
    if not self.title or not self.title.strip():
        raise BookError("Book must have a title")
    if not self.author or not self.author.strip():
        raise BookError("Book must have an author")
```

### Paso 3 — Entidad: test positivo (creación exitosa)

```python
def test_book_created_with_valid_data():
    book = Book("Dune", "Herbert")
    assert book.title == "Dune"
    assert book.author == "Herbert"
    assert book.is_available is True
```

> **Sin triangulación:** el constructor de `@dataclass` es genérico por
> construcción. No hay código tramposo que cazar.

### Paso 4 — Entidad: comportamiento (métodos)

**Cómo descubrir métodos:** hazte preguntas de sentido común sobre el dominio.
Para esta fase, solo preguntas que **consultan** estado (no lo cambian):

| Pregunta | Respuesta | Método |
|----------|-----------|--------|
| ¿Este libro está disponible? | Sí, si no está prestado | `can_be_loaned() → bool` |

> ⚠️ **No hagas tests que solo verifican «se ejecuta sin errores».**
> Todo test necesita un `assert` o un `pytest.raises`.

```python
def test_available_book_can_be_loaned():
    book = Book("Dune", "Herbert")
    result = book.can_be_loaned()
    assert result is True
```

**RED esperado:** `AttributeError: 'Book' object has no attribute 'can_be_loaned'`

**GREEN:**

```python
def can_be_loaned(self) -> bool:
    return self.is_available
```

#### ¿Por qué un método y no usar el campo directamente?

`can_be_loaned()` es la interfaz pública. Nadie debería hacer
`if book.is_available` — debería preguntar `if book.can_be_loaned()`.
Es **encapsulación**: el campo es implementación interna, el método es
el contrato público.

| Test | Qué prueba | Nivel |
|------|-----------|-------|
| Test 3 | `assert book.is_available is True` | **Estado interno** — el campo |
| Test 4 | `assert book.can_be_loaned() is True` | **API pública** — el método |

Hoy `can_be_loaned()` solo devuelve `self.is_available`, pero mañana
podría incluir más reglas: «está disponible si no está prestado Y tiene
ISBN válido Y no está en restauración».

**Caso concreto — añadir ISBN como requisito:**

```python
# Sin método — la regla vive en cada consumidor
if book.is_available:                     # ❌ no sabe nada del ISBN

# Con método — la regla vive en UN lugar
def can_be_loaned(self) -> bool:
    return self.is_available and self.isbn is not None  # ← único cambio
```

Si el código externo usa `is_available` a pelo, al añadir ISBN tienes que
cambiarlo en cada sitio. Si usa `can_be_loaned()`, cambias un método y
todo sigue funcionando.

Es la misma razón por la que no accedes a `email._value` sino a
`email.value`: el método expone el contrato público, el campo es detalle
interno.

#### ¿Por qué `can_be_loaned()` no lleva `pytest.raises`?

`can_be_loaned()` es una **pregunta** (query), no una **acción** (command).
Preguntar «¿está disponible?» siempre tiene respuesta válida: `True` o
`False`. No hay caso donde la pregunta misma sea ilegal.

```python
# Pregunta — nunca falla
assert book.can_be_loaned() is True   # ✅ respuesta válida
assert book.can_be_loaned() is False  # ✅ también respuesta válida
```

La excepción va en la **acción**, que es `loan()` (Paso 5). Intentar
prestar un libro ya prestado sí es ilegal:

```python
# Acción — puede fallar
with pytest.raises(BookAlreadyLoanedError):   # ✅ excepción aquí
    book.loan()
```

| Método | Tipo | ¿Excepción? |
|--------|------|-------------|
| `can_be_loaned()` | Pregunta (query) | Nunca |
| `loan()` | Acción (command) | `BookAlreadyLoanedError` si ya está prestado |

Esto es el principio **Command-Query Separation**: quien pregunta no
falla; quien actúa, sí puede fallar.

### Paso 5 — Entidad: estados (transiciones)

**Cómo descubrir métodos:** ahora preguntas que **cambian** el estado del objeto:

| Pregunta | Respuesta | Método |
|----------|-----------|--------|
| ¿Qué pasa cuando se presta? | Deja de estar disponible | `loan()` → `is_available = False` |
| ¿Se puede devolver? | Sí, vuelve a estar disponible | `return_book()` → `is_available = True` |

```python
def test_loaning_book_marks_it_unavailable():
    book = Book("Dune", "Herbert")
    book.loan()
    assert book.is_available is False
```

**GREEN:**

```python
def loan(self):
    self.is_available = False
```

💡 **Triangulación:** prueba `loan()` con otro libro para confirmar que no está hardcodeado.

### Paso 6 — Entidad: casos límite (blindaje)

> Cada «¿qué debería pasar si…?» es un test.

#### 6.1 — Un libro prestado no puede volver a prestarse

```python
def test_cannot_loan_book_twice():
    book = Book("Dune", "Herbert", is_available=False)
    with pytest.raises(BookAlreadyLoanedError):
        book.loan()
```

**RED esperado:** `NameError: name 'BookAlreadyLoanedError' is not defined`.

**GREEN:**

```python
# exceptions.py
class BookAlreadyLoanedError(BookError):
    """Raised when attempting to loan a book that is already out."""
    pass

# models.py
def loan(self):
    if not self.is_available:
        raise BookAlreadyLoanedError("Book is already loaned")
    self.is_available = False
```

#### 6.2 — Un libro disponible no puede devolverse

```python
def test_cannot_return_book_that_is_available():
    book = Book("Dune", "Herbert", is_available=True)
    with pytest.raises(BookError):
        book.return_book()
```

### Paso 7 — Revisión de diseño (manual, sin test)

**Objetivo:** verificar que la entidad no asume responsabilidades que no le corresponden.

Todas las preguntas aplican el mismo principio: **la entidad solo debe conocer su propio
estado** (Principio de Responsabilidad Única).

| Pregunta | Si es SÍ… | Por qué |
|---|---|---|
| ¿El código consulta una base de datos? | Mal — la entidad no toca la DB | La persistencia es responsabilidad del repositorio. Si la entidad sabe de tablas o queries, no puedes cambiar la DB sin tocar el dominio. |
| ¿El código sabe de fechas de devolución? | Mal — eso es del préstamo | `Loan` gestiona el ciclo de vida del préstamo. Si `Book` conoce fechas, cada vez que añadas una regla de préstamo tendrás que modificar `Book`. |
| ¿El código sabe quién lo prestó? | Mal — eso es del servicio | La relación usuario-libro la orquesta `LibraryService`. Si `Book` guarda una referencia al usuario, estás forzando a la entidad a conocer todo el modelo de usuarios. |

### Checklist post-entidad

| Verificación | ¿Pasa? |
|---|---|
| `pytest src/app/tests/ -v` — todo verde | ☐ |
| Cada test tiene AAA explícito | ☐ |
| Cada test negativo usa `pytest.raises` | ☐ |
| Cada test positivo tiene `assert` concreto | ☐ |
| Triangulé donde tuve dudas | ☐ |
| Cada excepción custom nació de un test negativo | ☐ |
| La entidad no toca BD, fechas ni usuarios | ☐ |

### Notas del proyecto

**Decisión tomada:** Email usa clase propia (VO). El resto usa strings con validación
en `__post_init__`.

| Entidad | Atributo | ¿Es VO? | Validación en |
|---|---|---|---|
| Book | `title` | No (str) | `Book.__post_init__` |
| Book | `author` | No (str) | `Book.__post_init__` |
| User | `email` | **Sí (Email)** | Clase `Email` |
| User | `username` | No (str) | `User.__post_init__` |

- **Loan** relaciona `User` con `Book`. Sus tests vendrán después.
- El orden completo: `Email (VO) → Book → User → Loan → InMemoryDatabase → LibraryService → DbProtocol`

#### Cuándo usar Value Objects vs strings simples

| Usa VO cuando… | Usa string simple cuando… |
|---|---|
| El dato tiene reglas de formato (email, DNI, ISBN) | El dato es libre (título de libro) |
| El dato se repite en varias entidades | El dato solo existe en una entidad |
| Quieres que el tipo documente la intención (`Email` vs `str`) | La simplicidad pesa más que el tipado |

#### ¿Por qué esos criterios?

1. **Reglas de formato → VO.** Si el dato tiene que cumplir condiciones para
   ser válido, la validación tiene que vivir en algún sitio. Con una clase, el
   constructor es el único punto de validación. El que recibe un `Email` sabe que
   ya es válido.

2. **Se repite en varias entidades → VO.** Si `Email` aparece en notificaciones,
   recibos o login, cada nuevo contexto duplicaría la validación. Una clase
   independiente evita ese problema.

3. **El tipo documenta la intención → VO.** `def register(email: Email)` dice
   más que `def register(email: str)`. El type checker detecta si pasas un string
   crudo sin validar.

4. **Testabilidad aislada.** Probar `Email` requiere 2 tests y cero dependencias.
   Si la validación estuviera dentro de `User`, cada test del email necesitaría
   crear un `User`.
