# library-api — Project Context for Pi

> Abrí Pi desde `/home/heks/PROJECTS/library-api` para que los comandos y paths resuelvan correctamente.

## Project identity

- **Name**: library-api — Library Management System
- **Author**: Hector Gancedo Grade
- **Language**: Python 3.13
- **Current stage**: Stage 1 · Foundations (`stage1-inmemory`)
- **Goal**: In-memory API, fully typed, tested, and lint-clean — no database yet
- **Full roadmap**: `project_docs/ROADMAP_FINAL_2026.md`
- **SDD config**: `openspec/config.yaml`

## Commands

```bash
# Tests
pytest src/app/tests/ -v
pytest src/app/tests/ -v --cov=src/app --cov-report=term-missing

# Lint + format
ruff check src/
ruff format src/

# Type check
pyright

# All checks in one pass
ruff check src/ && ruff format src/ && pyright
```

> ⚠️ `pytest` is not yet in dev deps — must be added to `pyproject.toml` before running tests.

## File structure

```
src/
  app/
    models.py           # dataclass domain models + type aliases
    exceptions.py       # exception hierarchy
    protocols.py        # DbProtocol (typing.Protocol)
    in_memory_database.py  # InMemoryDatabase — implements DbProtocol
    library_service.py  # LibraryService — pure business logic, no DB import
    main.py             # manual smoke runner (temporary)
    tests/              # ← must be created; empty for now
openspec/
  config.yaml         # SDD project config — source of truth for Pi phases
project_docs/
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
- **Casing**: `snake_case` for identifiers, `PascalCase` for classes
- **Line length**: 88 (Ruff)
- **Quote style**: double quotes

## Exception hierarchy

```
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

## TDD rule — strict

**RED → GREEN → TRIANGULATE → REFACTOR**

No production code before a failing test. This is not negotiable in Stage 1.

## Known tech debt

- **TD-001** `Optional[date]` in `Loan.return_date` — should be `date | None`
- **TD-002** `pytest` + `pytest-cov` missing from dev deps — blocking
- **TD-003** Email regex lives in `LibraryService.register_user` — should be in model/validator layer

## Context loading policy

This file is your complete context for **current stage work**. Do not load additional docs for routine tasks.

| Situation | Load |
|-----------|------|
| Routine Stage 1 work (tests, lint, refactors, TD fixes) | Nothing — this file is enough |
| Stage transition planning, "am I ready?", multi-stage questions | `project_docs/stage_summaries.md` |
| Full concept explanations, code examples, deep design dive | `project_docs/ROADMAP_FINAL_2026.md` |
| Adding, removing, or modifying a stage | Both files above (ROADMAP is source of truth) |

### When stages change

If a stage is **added, removed, or modified**, update all three files — never just one:
1. `project_docs/ROADMAP_FINAL_2026.md` — full detail, source of truth
2. `project_docs/stage_summaries.md` — compact map and per-stage card
3. `AGENTS.md` — this file, if current stage identity, branch, or goal changed

## SDD preferences

- **Mode**: interactive (Pi pauses between phases for confirmation)
- **Artifact store**: OpenSpec + Engram
- **PR strategy**: auto-forecast (Pi estimates diff size)
- **Review budget**: ~200 lines per PR
