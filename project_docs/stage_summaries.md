# Stage Summaries — library-api

> Derived from `ROADMAP_FINAL_2026.md`. Always update both together.
> Source of truth: `ROADMAP_FINAL_2026.md` · This file: compact agent reference.

## Purpose

Middle layer between `AGENTS.md` (always loaded) and the full roadmap (rarely loaded).

| Load when… | File |
|------------|------|
| Routine Stage 1 work | `AGENTS.md` — already in context |
| Stage transition planning, "am I ready?", multi-stage questions | **This file** |
| Full concept explanations, code examples, deep design | `ROADMAP_FINAL_2026.md` |

## Maintenance

When a stage is **added, removed, or modified**:

1. Update `ROADMAP_FINAL_2026.md` (source of truth — full detail)
2. Update this file (derived compact view — status, stack, exit criteria)
3. Update `AGENTS.md` if current stage identity, branch, or goal changed

Never update only one of the three files.

---

## Stage map

| # | Name | Branch | Status | Stack highlights |
|---|------|--------|--------|-----------------|
| 1 | Foundations | `stage1-tdd-from-scratch` | **in_progress** | Python 3.14, Pyright strict, Ruff, Pytest |
| 2 | Persistence | `stage2-persistence` | pending | SQLite → PostgreSQL, SQLAlchemy, Alembic |
| 3 | Security Base | `stage3-security` | pending | Pydantic v2, OWASP, Bandit, secrets |
| 4 | Pro Databases | `stage4-databases` | pending | PostgreSQL, MongoDB, Redis (intro) |
| 5 | Docker | `stage5-docker` | pending | Docker, Compose, multi-stage builds |
| 6 | Cloud Basics | `stage6-cloud` | pending | Railway, GitHub Actions CI/CD |
| 7 | Microservices | `stage7-microservices` | pending | FastAPI, Redis, RabbitMQ, Pact |
| 8 | AI Service | `stage8-ai` | pending | OpenAI/Anthropic, pgvector, LangSmith |
| 9 | Kubernetes | `stage9-k8s` | pending | K8s, AWS EKS/GKE, Helm, HPA |
| 10 | Infrastructure | `stage10-infra` | pending | Terraform, Kafka, AWS/GCP |
| 11 | Production | `stage11-production` | pending | JWT/OAuth2, Prometheus, Grafana, OTel |
| 12 | Agents | `stage12-agents` | pending | LangGraph, Semantic Kernel, LLM-as-a-Judge |

---

## Stage 1 · Foundations — `stage1-tdd-from-scratch`

**Status**: in_progress  
**Objective**: In-memory API — fully typed, tested, lint-clean. No database.

**Stack**: Python 3.14 · Pyright (strict) · Ruff · Pytest · Git

**Core concepts**:

- Strict types with Pyright — no ambiguity for human or AI reviewer
- SRP: `LibraryService` holds business logic; `LibraryRepository` (Protocol) holds the contract
- `InMemoryDatabase` is the implementation — swappable without touching service or tests
- TDD: RED → GREEN → TRIANGULATE → REFACTOR, no exceptions

**Exit criteria**:

- Swap `LibraryRepository` implementation without modifying a single test
- Pyright strict — zero errors
- Ruff — zero warnings
- Test coverage > 90% on business logic

**Known debt**: TD-001 `Optional[date]`, TD-002 pytest dev-dep, TD-003 email regex location

---

## Stage 2 · Persistence — `stage2-persistence`

**Status**: pending  
**Objective**: Add persistence without leaking the database into business logic.

**Stack**: SQLite (dev) · SQLAlchemy · Alembic · Pytest fixtures (integration tests)

**Core concepts**:

- Only the repository implementation changes — `LibraryService` must be untouched
- SQLite for dev/tests; switching to PostgreSQL = one config line
- Alembic migrations are production code: reviewed, tested, irreversible with care
- Unit tests (in-memory, no I/O) stay separate from integration tests (SQLite)

**Exit criteria**:

- Switch SQLite → PostgreSQL by changing one line; all tests pass
- Stage 1 unit tests require zero modification
- Integration tests use `Session(engine)` fixtures with rollback

---

## Stage 3 · Security Base — `stage3-security`

**Status**: pending  
**Objective**: Security as a habit, not a last-minute feature.

**Stack**: Pydantic v2 · python-dotenv · Bandit · OWASP API Security Top 10

**Core concepts**:

- OWASP API Top 10 understood with concrete examples in this project (API1, API3, API8 first)
- All external input validated at the boundary with Pydantic v2 `Field` constraints
- Zero secrets in code or git history — `.env` for local, platform env vars for production
- Bandit for static security analysis in CI

**Exit criteria**:

- Any user input — malicious or malformed — cannot break or access other users' data
- Bandit: zero high-severity warnings
- Pydantic v2 validation on all external entry points
- No secrets in code, history, or Docker layers

---

## Stage 4 · Pro Databases — `stage4-databases`

**Status**: pending  
**Objective**: Know when to use which database and why — and prove it.

**Stack**: PostgreSQL · MongoDB · SQLAlchemy (PostgreSQL) · Redis (intro)

**Core concepts**:

- PostgreSQL: relational, ACID, complex queries — loans, users, inventory
- MongoDB: flexible schema, high write volume — logs, variable-field profiles
- `EXPLAIN ANALYZE` on every critical query; index before it becomes a problem
- Transactions: two operations that must succeed together or not at all

**Exit criteria**:

- Justified database choice for every entity in the system
- All critical queries analyzed with `EXPLAIN ANALYZE` and indexed where needed
- Integration tests validate transactional behavior (partial failure scenarios)

---

## Stage 5 · Docker — `stage5-docker`

**Status**: pending  
**Objective**: Same behavior in dev, colleague's machine, and production.

**Stack**: Docker · Docker Compose · multi-stage builds · .dockerignore

**Core concepts**:

- Image as deployment unit — immutable, reproducible
- Multi-stage build: builder stage installs deps; production stage is lean (no build tools)
- Docker Compose orchestrates the full stack locally (API + DB + any broker)
- Zero secrets in Dockerfile or image layers — all via environment variables

**Exit criteria**:

- `docker compose up` boots full stack from scratch in < 2 minutes on any machine
- Production image < 200 MB
- No secrets in Dockerfile, image layers, or `docker-compose.yml`

---

## Stage 6 · Cloud Basics — `stage6-cloud`

**Status**: pending  
**Objective**: Real production URL. Understand what breaks in the cloud before K8s complexity.

**Stack**: Railway (recommended) · GitHub Actions · cloud env vars

**Core concepts**:

- Railway as training ground: same concepts as K8s (health checks, env vars, logs, CI/CD) without the cluster overhead
- Health endpoint (`GET /health`) required — platform needs it to auto-restart on failure
- Push to `main` → automatic deploy via GitHub Actions
- Logs are your only window into production — learn to read them in the dashboard

**Exit criteria**:

- Public URL live; push to `main` deploys automatically
- Health check responding; Railway auto-restart validated
- Zero hardcoded credentials anywhere in the pipeline

**Why Railway over Render**: better DX, closer to Stage 7 microservices patterns.

---

## Stage 7 · Microservices — `stage7-microservices`

**Status**: pending  
**Objective**: Independent services that communicate asynchronously and degrade gracefully.

**Stack**: FastAPI · Redis (cache + pub/sub) · RabbitMQ · Pact · Docker Compose multi-service

**Core concepts**:

- Split by bounded context only when there's a real reason (independent deploy, team isolation, scale)
- Async communication: loans service publishes `loans.created`; notifications service consumes it
- If notifications is down, loan creation still succeeds — the event stays in the queue
- Contract testing with Pact: consumer defines what it expects from the provider, independently

**Exit criteria**:

- Take down one service; the rest continue operating (degraded but not failed)
- Minimum 3 independent services: loans, users, notifications
- Pact contract tests between all communicating service pairs
- `docker compose up` boots the full multi-service system

---

## Stage 8 · AI Service — `stage8-ai`

**Status**: pending  
**Objective**: AI as a microservice with the same quality guarantees as any other component.

**Stack**: OpenAI/Anthropic API · pgvector · ChromaDB or Qdrant · LangSmith · Pydantic structured outputs

**Core concepts**:

- RAG: embed query → vector similarity search in pgvector → pass context to LLM → structured response
- Structured outputs via Pydantic: LLM returns typed, validated objects — not raw strings
- Every LLM call needs: timeout, retry with backoff, token/cost logging, fallback
- LangSmith for tracing: latency, tokens, and cost per request

**Exit criteria**:

- AI Service can go down completely; core system continues with reduced functionality
- Automatic fallback if LLM doesn't respond in < 10 seconds
- LangSmith tracing active: latency, tokens, cost visible per request

---

## Stage 9 · Kubernetes — `stage9-k8s`

**Status**: pending  
**Objective**: Manage a distributed system at scale with zero-downtime deployments.

**Stack**: Kubernetes · AWS EKS or GKE · kubectl · Helm

**Core concepts**:

- Railway concepts formalized: health checks → liveness/readiness probes; env vars → ConfigMaps/Secrets; auto-deploy → Rolling Updates
- Rolling Updates: pods replaced one by one; if new pod fails health check, rollout stops automatically
- HorizontalPodAutoscaler: scale replicas based on CPU/memory automatically
- Zero credentials in YAML manifests — everything via K8s Secrets

**Exit criteria**:

- Deploy new service version with zero user-perceived downtime (demonstrated)
- HPA configured on at least one service
- Zero credentials in any manifest; all managed via K8s Secrets

---

## Stage 10 · Infrastructure as Code — `stage10-infra`

**Status**: pending  
**Objective**: All infrastructure is versioned code — reproducible and auditable.

**Stack**: Terraform · Kafka · AWS or GCP

**Core concepts**:

- `terraform apply` creates infrastructure; `terraform destroy` removes it — state in the repo, not in someone's head
- Terraform state in S3 with locking — never local, never shared via filesystem
- Kafka over RabbitMQ when: millions of events/sec, event replay, multi-consumer, days of retention
- IAM with least privilege — Terraform manages permissions, not console clicks

**Exit criteria**:

- Recreate entire production environment from scratch with one command
- Terraform state in S3 with remote locking
- At least one Kafka use case replacing a RabbitMQ queue from Stage 7

---

## Stage 11 · Production — `stage11-production`

**Status**: pending  
**Objective**: A system that survives failure, is observable, and is secure in real production.

**Stack**: JWT + OAuth2 · Prometheus · Grafana · OpenTelemetry · LangSmith / Arize Phoenix

**Core concepts**:

- JWT at production level: refresh token rotation, revocation, scopes per resource, rate limiting per authenticated user
- Four pillars of observability: logs (what), metrics (how much), traces (how), alerts (when to act)
- LLM-specific metrics: p99 latency, daily token cost, hallucination rate, fallback rate
- Alerts configured before incidents, not after

**Exit criteria**:

- When something fails in production: know exactly where, why, and how many users affected — before they report it
- JWT with refresh tokens and revocation implemented; rate limiting active
- Grafana alerts configured for critical KPIs

---

## Stage 12 · Agents — `stage12-agents`

**Status**: pending  
**Objective**: AI that reasons, decides, and coordinates tools autonomously over the infrastructure built in stages 1–11.

**Stack**: LangGraph · Semantic Kernel · LLM-as-a-Judge

**Core concepts**:

- An agent is a loop: receive task → choose tool → execute → observe result → decide if done
- Agent tools ARE your existing services from previous stages — no magic, just API calls
- LangGraph manages state and conditional branching (book available? → create loan : suggest alternative)
- LLM-as-a-Judge: a more powerful model evaluates every response of the task model

**Exit criteria**:

- Agent resolves at least 3 natural-language request types using services from previous stages
- LLM-as-a-Judge evaluates 100% of agent responses automatically
- Grafana dashboard: agent success rate, reasoning latency, cost per resolution

---

## Cross-cutting security thread

| Stage | Security action |
|-------|----------------|
| 1 | Strict types — no ambiguous data |
| 2 | Migrations reviewed — no accidental data destruction |
| 3 | OWASP, input validation, secrets out of code |
| 4 | DB permissions by least-privilege principle |
| 5 | Docker images without root; no secrets in layers |
| 6 | Env vars in platform dashboard, never in repo |
| 7 | Service-to-service auth (mTLS or internal tokens) |
| 8 | Rate limiting on AI Service — LLM calls are expensive |
| 9 | K8s NetworkPolicies — services talk only to whom they must |
| 10 | IAM least privilege in Terraform |
| 11 | Full JWT: rotation, revocation, rate limiting |
| 12 | Agent tool sandboxing — can only call what it should |
