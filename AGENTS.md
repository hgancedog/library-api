# library-api — Project Context for Pi

> Inicia Pi desde `/home/heks/PROJECTS/library-api` para que los comandos y paths resuelvan correctamente.

## Project identity

- **Name**: library-api — Library Management System
- **Author**: Hector Gancedo Grade
- **Language**: Python 3.13
- **Current stage**: Stage 1 · Foundations (`stage1-tdd-from-scratch`)
- **Goal**: In-memory API, fully typed, tested, and lint-clean — no database yet
- **Full roadmap**: `project_docs/ROADMAP_FINAL_2026.md`
- **SDD config**: `openspec/config.yaml`

## Commands

```bash
# Tests
pytest src/tests/ -v
pytest src/tests/ -v --cov=src/app --cov-report=term-missing

# Lint + format
ruff check src/
ruff format src/

# Type check
pyright

# All checks in one pass
ruff check src/ && ruff format src/ && pyright
```

## File structure

```text
src/
  app/
    models.py           # dataclass domain models + type aliases (TDD-driven)
  tests/
    test_email.py       # Email VO tests
openspec/
  config.yaml         # SDD project config — source of truth for Pi phases
project_docs/
  design-notes/
    01-tdd-desde-cero.md  # decision journal + TDD guide
  ROADMAP_FINAL_2026.md
pyproject.toml
pyrightconfig.json    # typeCheckingMode: strict, includes: [src]
.pre-commit-config.yaml  # ruff + ruff-format + venv-check
```

## Established conventions

- **Models**: `@dataclass`, not Pydantic (Stage 1)
- **ID types**: type aliases — `BookID = int`, `UserID = int`, `LoanID = int`
- **Repository interface**: `typing.Protocol` — never ABC
- **Union syntax**: `X | None` — not `Optional[X]` (one legacy instance in `Loan.return_date` to fix)
- **Private attributes**: `_` prefix in implementation classes
- **Duck typing guard**: `_: DbProtocol = InMemoryDatabase()` at module level
- **Code and docstrings**: English
- **Docs language**: neutral Spanish (castellano estándar). **ZERO voseo** — no usar conjugaciones del voseo (-ás, -és, -ís). Usa solo formas del castellano estándar: tienes, puedes, sabes, creas, usas.
- **Casing**: `snake_case` for identifiers, `PascalCase` for classes
- **Line length**: 88 (Ruff)
- **Quote style**: double quotes

## Exception hierarchy

```text
LibraryApiError
├── BookError
│   ├── BookNotFoundError
│   └── BookAlreadyLoanedError
├── UserError
└── LoanError
```

## Stage 1 completion criteria (from roadmap)

- `LibraryRepository` implementation swappable without touching tests
- Pyright strict — zero errors
- Ruff — zero warnings
- Test coverage > 90% on business logic

## Session startup — config.yaml integrity check

**At the start of every session, before any work begins**, verify that
`openspec/config.yaml` matches the actual state on disk. If any field is
stale, update it before proceeding — a stale config wastes entire SDD
phases because agents and subagents treat it as ground truth.

```bash
# Run these 5 checks in one pass:
git rev-parse --short HEAD          # vs project.git_head
pytest src/tests/ -q --tb=no        # vs test_status.total_tests
python --version                    # vs project.python_runtime
git branch --show-current           # vs project.current_branch
ls src/app/*.py                     # vs structure.source_files
```

Also verify:

- `test_status.coverage_percent` — run `pytest --cov=src/app --cov-report=term-missing`
- `test_status.last_verified` — update to today's date
- `domain.entities[*].behavior` — check for new methods added since last sync
- `domain.exceptions.hierarchy` — check for new exception classes

This is NOT optional. The cost of a stale config is the cost of an entire
SDD session built on false assumptions.

## Productivity guard — anti-pattern detection

**If you detect any of these patterns, warn me immediately and suggest a course correction:**

1. **Docs > code ratio**: when project documentation (`.md` files in `project_docs/`) exceeds production code + tests by more than 3:1, flag it. The project is a library API, not a wiki.

2. **Meta-documentation creep**: writing docs about tools (Pi, git, seguridad, python-theory, etc.) that do not advance the current stage. These belong in a personal knowledge base, not in the project repo.

3. **Planning as procrastination**: spending more than one session on a design note, roadmap refinement, or decision journal entry without producing code. Stop writing ABOUT the code and write THE code.

4. **Tool configuration without implementation**: adding hooks, scripts, linters, or CI config for features that don't exist yet. Stage 1 doesn't need Docker, K8s, or CI pipelines — it needs a working in-memory API.

5. **Session without a passing test**: if a full session ends without at least one new passing test that advances Stage 1 completion criteria, flag it.

6. **Stale SDD artifact**: `openspec/config.yaml` must reflect the current state of the project — not aspirational architecture. If it lists source files that don't exist on disk, describes a stack that isn't installed, or references a different branch than `git branch --show-current`, flag it. A stale config wastes entire SDD phases because agents treat it as ground truth. Verify with: `ls src/app/*.py` vs `structure.source_files`, `python --version` vs `project.python_runtime`, `git branch --show-current` vs `project.current_branch`.

**When I warn you**: stop writing docs/config immediately. Open the task that moves Stage 1 forward. If in doubt, the answer is always: write the next failing test.

## TDD rule — strict

**TDD rule — strict:** RED → GREEN → TRIANGULATE → REFACTOR

No production code before a failing test. This is not negotiable in Stage 1.

## Known tech debt

- **Branch rename post-Stage 1**: al finalizar Stage 1, eliminar `stage1-inmemory` (local + remoto, 17 commits obsoleta) y renombrar `stage1-tdd-from-scratch` → `stage1-inmemory`. Actualizar referencias en `AGENTS.md`, `openspec/config.yaml`, `stage_summaries.md` y `ROADMAP_FINAL_2026.md`.
- **Docstrings pendientes**: `models.py` tiene docstrings en las excepciones pero no en entidades (`Book`, `User`, `Loan`, `Email`), métodos públicos (`can_be_loaned`, `mark_as_loaned`, `due_date`), ni type aliases (`BookID`, `UserID`, `LoanID`). Añadir al finalizar Stage 1 para que el código sea auditable por IA y profesional para portfolio.

## Context loading policy

This file is your complete context for **current stage work**. Do not load additional docs for routine tasks.

| Situation | Load |
| ----------- | ------ |
| Routine Stage 1 work (tests, lint, refactors, TD fixes) | Nothing — this file is enough |
| Stage transition planning, "am I ready?", multi-stage questions | `project_docs/stage_summaries.md` |
| Full concept explanations, code examples, deep design dive | `project_docs/ROADMAP_FINAL_2026.md` |
| Adding, removing, or modifying a stage | Both files above (ROADMAP is source of truth) |

### When stages change

If a stage is **added, removed, or modified**, update all four files — never just one:

1. `project_docs/ROADMAP_FINAL_2026.md` — full detail, source of truth
2. `project_docs/stage_summaries.md` — compact map and per-stage card
3. `AGENTS.md` — this file, if current stage identity, branch, or goal changed
4. `openspec/config.yaml` — SDD ground truth: branch, stack, structure, domain

## SDD preferences

- **Mode**: interactive (Pi pauses between phases for confirmation)
- **Artifact store**: OpenSpec + Engram
- **PR strategy**: auto-forecast (Pi estimates diff size)
- **Review budget**: ~200 lines per PR
