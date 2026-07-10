# Library Management System API

This project is an evolutionary backend development journey. It starts from basic Object-Oriented Programming (OOP) fundamentals and scales up to a distributed microservices architecture deployed in the cloud.

The main objective is to demonstrate professional growth, architectural patterns, and the adoption of industry-standard technologies like **SQLAlchemy, PostgreSQL, MongoDB, Redis, Docker, FastAPI, RabbitMQ, Kubernetes, Kafka, JWT, Prometheus, Grafana, OpenTelemetry, and LLMs/RAG**.

---

## 🚀 Project Roadmap & Evolution

The project is organized into sequential stages. Each stage is hosted in its own dedicated branch to showcase the transition between different architectural levels.

| Stage | Branch | Key Technologies |
| --- | --- | --- |
| **1. Foundations** | `stage1-tdd-from-scratch` | Python 3.14, Pyright, Ruff, Pytest |
| **2. Persistence** | `stage2-persistence` | SQLite, SQLAlchemy, Alembic |
| **3. Security Base** | `stage3-security` | OWASP, Pydantic v2, Bandit |
| **4. Pro Databases** | `stage4-databases` | PostgreSQL, MongoDB, Redis |
| **5. Docker** | `stage5-docker` | Docker, Docker Compose |
| **6. Cloud Basics** | `stage6-cloud` | Railway, GitHub Actions |
| **7. Microservices** | `stage7-microservices` | FastAPI, Redis, RabbitMQ, Pact |
| **8. AI Service** | `stage8-ai` | LLMs, RAG, pgvector, LangSmith |
| **9. Kubernetes** | `stage9-k8s` | K8s, AWS EKS/GKE, Helm |
| **10. Infrastructure** | `stage10-infra` | Terraform, Kafka |
| **11. Production** | `stage11-production` | JWT, Prometheus, Grafana, OpenTelemetry |
| **12. Agents** | `stage12-agents` | LangGraph, Semantic Kernel, LLM Judge |

> Full roadmap: [`project_docs/ROADMAP_FINAL_2026.md`](project_docs/ROADMAP_FINAL_2026.md)
> Current stage configuration: [`openspec/config.yaml`](openspec/config.yaml)

---

## 🧠 Development methodology

This project follows **Specification-Driven Development (SDD)** with strict TDD. Every significant change is documented through auditable phases before a single line of production code is written:

- **RED → GREEN → TRIANGULATE → REFACTOR** — no production code without a failing test first
- **SDD artifact pipeline** — `explore → proposal → spec → design → tasks → apply → verify`
- **OpenSpec** — phase-gated development; each change leaves a trail of auditable artifacts in `openspec/changes/`
- **Multi-lens review** — every change is audited across security, reliability, resilience, and readability gates

**Agent-assisted, human-directed.** This project uses [Pi](https://github.com/earendil-works/pi-coding-agent) as an agent orchestration harness and [Gentle AI](https://github.com/pi-coding-agent/gentle-pi) for SDD workflow discipline. AI is a tool in the engineering process — it explores, drafts, and reviews. The human owns every architectural decision, every interface design, and every commit.

---

## 🛠️ Global Tech Stack

| Category | Tools |
| ---------- | ------ |
| **Language** | Python 3.14 |
| **Framework** | FastAPI |
| **Databases** | PostgreSQL, MongoDB, SQLite, Redis |
| **Type Checking** | Pyright (strict mode) |
| **Linting & Formatting** | Ruff |
| **Testing** | Pytest |
| **Infrastructure** | Docker, Kubernetes |
| **DevOps** | GitHub Actions, Prometheus, Grafana |
| **AI** | LLMs/RAG, pgvector, LangGraph |
| **Methodology** | Strict TDD, SDD/OpenSpec, multi-lens automated review |

---

## 📖 How to navigate this project

1. **Main Branch:** This README serves as the project index and roadmap.
2. **Specific Stages:** Switch to a specific branch to see the implementation:

    ```bash
    git checkout stage1-tdd-from-scratch
    ```

3. **Documentation:** Detailed stage specifications live in [`project_docs/ROADMAP_FINAL_2026.md`](project_docs/ROADMAP_FINAL_2026.md) and [`openspec/config.yaml`](openspec/config.yaml).

---

## 👤 Author

### Hector Gancedo Grade

- _Backend/API Developer_
- Focus: Python, Microservices, and Cloud-native Architectures.
