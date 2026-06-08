# Library Management System API

This project is an evolutionary backend development journey. It starts from basic Object-Oriented Programming (OOP) fundamentals and scales up to a distributed microservices architecture deployed in the cloud.

The main objective is to demonstrate professional growth, architectural patterns, and the adoption of industry-standard technologies like **SQLAlchemy, PostgreSQL, MongoDB, Redis, Docker, FastAPI, RabbitMQ, Kubernetes, Kafka, JWT, Prometheus, Grafana, OpenTelemetry, and LLMs/RAG**.

---

## 🚀 Project Roadmap & Evolution

The project is organized into sequential stages. Each stage is hosted in its own dedicated branch to showcase the transition between different architectural levels.

| Stage                     | Branch                 | Key Technologies                    |
| :------------------------ | :--------------------- | :---------------------------------- |
| **1. Foundations**        | `stage1-inmemory`      | Python 3.13, Pyright, Ruff, Pytest  |
| **2. Persistence**        | `stage2-sqlite`        | SQLite, SQLAlchemy, Alembic         |
| **3. Security Base**      | `stage3-postgres`      | OWASP, Pydantic v2, Bandit          |
| **4. Pro Databases**      | `stage4-docker`        | PostgreSQL, MongoDB, Redis          |
| **5. Docker**             | `stage4-docker`        | Docker, Docker Compose              |
| **6. Cloud Basics**       | `stage5-microservices` | Railway/Render, GitHub Actions      |
| **7. Microservices**      | `stage5-microservices` | FastAPI, Redis, RabbitMQ, Pact      |
| **8. AI Service**         | `stage6-kubernetes`    | LLMs, RAG, pgvector, LangSmith      |
| **9. Kubernetes**         | `stage6-kubernetes`    | K8s, AWS EKS/GKE, Helm              |
| **10. Infrastructure**    | `stage7-extras`        | Terraform, Kafka                    |
| **11. Production**        | `stage7-extras`        | JWT, Prometheus, Grafana, OpenTelemetry |
| **12. Agents**            | `stage7-extras`        | LangGraph, Semantic Kernel, LLM Judge |

> Full roadmap: [`project_docs/ROADMAP_FINAL_2026.md`](project_docs/ROADMAP_FINAL_2026.md)
> Current stage configuration: [`openspec/config.yaml`](openspec/config.yaml)

---

## 🛠️ Global Tech Stack

**Language:** Python 3.13
**Framework:** FastAPI
**Databases:** PostgreSQL, MongoDB, SQLite, Redis
**Type Checking:** Pyright (strict mode)
**Linting & Formatting:** Ruff
**Testing:** Pytest
**Infrastructure:** Docker, Kubernetes
**DevOps:** GitHub Actions, Prometheus, Grafana
**AI:** LLMs/RAG, pgvector, LangGraph
**Methodology:** Strict TDD, SDD/OpenSpec phases

---

## 📖 How to navigate this project

1.  **Main Branch:** This README serves as the project index and roadmap.
2.  **Specific Stages:** Switch to a specific branch to see the implementation:
    ```bash
    git checkout stage1-inmemory
    ```
3.  **Documentation:** Detailed stage specifications live in [`project_docs/ROADMAP_FINAL_2026.md`](project_docs/ROADMAP_FINAL_2026.md) and [`openspec/config.yaml`](openspec/config.yaml).

---

## 👤 Author

**Hector Gancedo Grade**

- _Backend/API Developer_
- Focus: Python, Microservices, and Cloud-native Architectures.
