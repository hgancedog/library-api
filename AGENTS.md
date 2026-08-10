# library-api — Project Context for Pi

> Inicia Pi desde `/home/heks/PROJECTS/library-api` para que los comandos y paths resuelvan correctamente.

## Project identity

- **Name**: library-api — Library Management System
- **Author**: Hector Gancedo Grade
- **Language**: Python 3.14
- **Current stage**: Stage 2 · Persistence (`stage2-persistence`)
- **Goal**: Add SQLite persistence via SQLAlchemy + Alembic, separate service from repository
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
    models.py             # dataclass domain models + type aliases (TDD-driven)
    repository.py         # LibraryRepository protocol (CRUD only in Stage 2)
    library_service.py    # NUEVO Stage 2 — orquestación, sin dependencia de DB
    orm_models.py         # NUEVO Stage 2 — SQLAlchemy declarative models
    sqlite_repository.py  # NUEVO Stage 2 — implementación CRUD con SQLAlchemy
  tests/
    test_book.py          # Book model tests (intactos desde Stage 1)
    test_user.py          # User model tests (intactos)
    test_loan.py          # Loan model tests (intactos)
    test_email.py         # Email VO tests (intactos)
    test_library_service.py    # NUEVO — unit tests con repo doble
    test_sqlite_repository.py  # NUEVO — integration tests con SQLite :memory:
openspec/
  config.yaml           # SDD project config — source of truth for Pi phases
project_docs/
  design-notes/
    01-tdd-desde-cero.md    # decision journal Stage 1
    02-persistencia.md       # decision journal Stage 2
  ROADMAP_FINAL_2026.md
pyproject.toml
pyrightconfig.json      # typeCheckingMode: strict, includes: [src]
.pre-commit-config.yaml # ruff + ruff-format + venv-check
alembic.ini             # NUEVO Stage 2
alembic/                # NUEVO Stage 2 — migrations
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

## config.yaml integrity check

`openspec/config.yaml` is ground truth for SDD agents and subagents. A stale
config derails entire phases. Verify it at three checkpoints:

### When closing a session that modified `src/`

If the session touched production code or tests, run before ending:

```bash
git rev-parse --short HEAD          # should be == or descendant of project.git_head
pytest src/tests/ -q --tb=no        # vs test_status.total_tests
python --version                    # vs project.python_runtime
git branch --show-current           # vs project.current_branch
ls src/app/*.py                     # vs structure.source_files
```

`project.git_head` records the LAST commit where config.yaml was fully verified.
It does NOT need to match current HEAD — only that current HEAD is a descendant.
Update `git_head` only when running the full integrity check, not on every commit.

Also update `test_status.coverage_percent`, `test_status.last_verified`,
`domain.entities[*].behavior` and `domain.exceptions.hierarchy` if they changed.

### Before any git commit

When a commit is about to be created, run the same verification. This catches
stale config before it gets sealed into a commit — the most dangerous form of
drift, since future agents will read it as ground truth.

### Before any SDD phase or subagent

The orchestrator or any SDD subagent runs the same verification before reading
`config.yaml`. This is the safety net in case the previous session closure
or pre-commit check didn't do it.

Read-only sessions, doc reviews, or conversations do **not** need this check.

## Productivity guard — anti-pattern detection

**If you detect any of these patterns, warn me immediately and suggest a course correction:**

1. **Docs > code ratio**: when project documentation (`.md` files in `project_docs/`) exceeds production code + tests by more than 3:1, flag it. The project is a library API, not a wiki.

2. **Meta-documentation creep**: writing docs about tools (Pi, git, seguridad, python-theory, etc.) that do not advance the current stage. These belong in a personal knowledge base, not in the project repo.

3. **Planning as procrastination**: spending more than one session on a design note, roadmap refinement, or decision journal entry without producing code. Stop writing ABOUT the code and write THE code.

4. **Tool configuration without implementation**: adding hooks, scripts, linters, or CI config for features that don't exist yet. Stage 1 doesn't need Docker, K8s, or CI pipelines — it needs a working in-memory API.

5. **Session without a passing test**: if a full session ends without at least one new passing test that advances Stage 1 completion criteria, flag it.

6. **Stale SDD artifact**: `openspec/config.yaml` must reflect the current state of the project — not aspirational architecture. If it lists source files that don't exist on disk, describes a stack that isn't installed, or references a different branch than `git branch --show-current`, flag it. A stale config wastes entire SDD phases because agents treat it as ground truth. Verify with: `ls src/app/*.py` vs `structure.source_files`, `python --version` vs `project.python_runtime`, `git branch --show-current` vs `project.current_branch`. Note: `project.git_head` is a historical record of last verification, not current HEAD — it's stale by design and only updated during full integrity checks.

7. **Long session without delegation**: when the session reaches ~20 tool calls or ~2 non-trivial commits without delegating a single task to a subagent, pause and warn. Long sessions cause context dilution — rules in this file, the commit flow, and `config.yaml` integrity checks are progressively forgotten. Suggest: (a) close and reopen the session to reload context fresh, or (b) delegate the next task.

**When I warn you**: stop writing docs/config immediately. Open the task that moves Stage 1 forward. If in doubt, the answer is always: write the next failing test.

## TDD rule — strict

**TDD rule — strict:** RED → GREEN → TRIANGULATE → REFACTOR

No production code before a failing test. This is not negotiable in Stage 1.

## Commit flow

Every commit goes through the review lens before committing.

**Fast path (solo-dev):** `scripts/commit "message"` — ejecuta pre-flight checks,
start, finalize, validate y commit en un solo paso.

**Full path:** `project_docs/commit-flow.md` — procedimiento paso a paso para
control fino, PRs multi-área, o docs-only commits.

## Known tech debt

- **Branch rename post-Stage 1**: ✅ DONE (2026-08-10). Deleted stale `stage1-inmemory`, renamed `stage1-tdd-from-scratch` → `stage1-inmemory`.
- **Pending docstrings**: ✅ DONE (2026-08-10). All entities, public methods, properties, protocol, and implementation documented.

## Context loading policy

This file is your complete context for **current stage work**. Do not load additional docs for routine tasks.

| Situation | Load |
| ----------- | ------ |
| Routine Stage 1 work (tests, lint, refactors, TD fixes) | Nothing — this file is enough |
| Committing code | `project_docs/commit-flow.md` |
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
