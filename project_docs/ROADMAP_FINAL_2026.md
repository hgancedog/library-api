# ROADMAP: De Fundamentos a AI-Native Architecture (2026)

### Backend Engineering con Python · Edición definitiva

> Documento elaborado por el Gentleman — arquitecto senior + harness Pi  
> Fuentes: roadmap original de Hector, opiniones de Gemini, GPT-4, Claude Opus, análisis propio  
> Fecha: junio 2026

---

## Filosofía del roadmap

Tres principios que atraviesan todas las stages:

**1. Fundamentos antes que herramientas**  
Una herramienta nueva tarda días en aprenderse. Un concepto sólido dura toda la carrera. No avances a la siguiente stage hasta entender el *por qué*, no solo el *cómo*.

**2. Tests como ciudadanos de primera clase**  
En 2026 la IA genera código más rápido que nunca. Tu única garantía de que ese código funciona son los tests. Sin tests, no hay stage completada.

**3. La IA es un componente, no el objetivo**  
No aprendas a usar IA para escribir código. Aprende a construir sistemas donde la IA sea un servicio más, tan reemplazable y monitoreable como una base de datos.

---

## Mapa general

| Stage | Nombre | Branch | Versión | Stack principal |
|-------|--------|--------|---------|-----------------|
| 1 | Foundations | `stage1-inmemory` | Stage 1 | Python 3.13, Pyright, Ruff, Pytest |
| 2 | Persistence | `stage2-persistence` | Stage 2 | SQLite, SQLAlchemy, Alembic |
| 3 | Security Base | `stage3-security` | Stage 3 | OWASP, Pydantic, secrets |
| 4 | Pro Databases | `stage4-databases` | Stage 4 | PostgreSQL, MongoDB |
| 5 | Docker | `stage5-docker` | Stage 5 | Docker, Docker Compose |
| 6 | Cloud Basics | `stage6-cloud` | Stage 6 | Railway / Render |
| 7 | Microservices | `stage7-microservices` | Stage 7 | FastAPI, Redis, RabbitMQ |
| 8 | AI Service | `stage8-ai` | Stage 8 | LLMs, RAG, pgvector |
| 9 | Kubernetes | `stage9-k8s` | Stage 9 | K8s, AWS EKS / GKE |
| 10 | Infrastructure | `stage10-infra` | Stage 10 | Terraform, Kafka |
| 11 | Production | `stage11-production` | Stage 11 | JWT, Prometheus, Grafana, LLMOps |
| 12 | Agents | `stage12-agents` | Stage 12 | LangGraph, Semantic Kernel |

---

## Stage 1 · Foundations

### `stage1-inmemory` · Stage 1

**Objetivo:** Escribir código Python correcto, tipado, testeable y auditable por una IA.

### Stack

| Herramienta | Rol |
|-------------|-----|
| Python 3.13 | Lenguaje base |
| Pyright | Type checker estático |
| Ruff | Linter + formateador |
| Pytest | Framework de tests |
| Git | Control de versiones |

### Conceptos clave a dominar

**Tipos estrictos**  
El tipado estático no es opcional en 2026. Cuando le das tipos claros a una IA, sus sugerencias mejoran 10x. Cuando no los das, genera código ambiguo que parece correcto y no lo es.

```python
# ❌ Sin tipos — la IA no puede ayudarte bien
def create_loan(user, book, days):
    ...

# ✅ Con tipos — contrato explícito, auditable
def create_loan(user: User, book: Book, days: int) -> Loan:
    ...
```

**Separación de responsabilidades**  
La lógica de negocio debe vivir en servicios puros, sin dependencias externas. La base de datos es un detalle de implementación. Esta decisión tomada en Stage 1 te ahorra semanas en Stage 2.

```python
# LibraryService no sabe nada de bases de datos
class LibraryService:
    def __init__(self, repository: LibraryRepository) -> None:
        self._repo = repository

    def create_loan(self, user_id: int, book_id: int) -> Loan:
        book = self._repo.get_book(book_id)
        if not book.available:
            raise BookNotAvailableError(book_id)
        return self._repo.save_loan(Loan(user_id=user_id, book_id=book_id))
```

**TDD desde el primer día**  
No escribas producción antes de escribir el test. Este hábito formado en Stage 1 se vuelve natural en Stage 7.

```python
# RED: el test primero, el código no existe aún
def test_create_loan_fails_when_book_unavailable():
    book = Book(id=1, available=False)
    repo = InMemoryRepository(books=[book])
    service = LibraryService(repo)

    with pytest.raises(BookNotAvailableError):
        service.create_loan(user_id=1, book_id=1)
```

### Criterios de compleción

- [ ] API de biblioteca completa en memoria (sin base de datos)
- [ ] Suite de tests con cobertura > 90% de la lógica de negocio
- [ ] Pyright en modo estricto sin errores
- [ ] Ruff sin warnings

### Cómo usar IA en esta stage

- Cuando sugiera código, preguntá: *¿por qué este patrón y no otro?*
- Usa la IA para revisar si tus tipos son consistentes
- **No delegues el diseño de interfaces — eso es tuyo**

### Señal de que estás listo para Stage 2

Puedes cambiar la implementación de `LibraryRepository` completamente y tus tests siguen pasando sin modificarlos.

---

## Stage 2 · Persistence

### `stage2-persistence` · Stage 2

**Objetivo:** Añadir persistencia a tu sistema sin que la lógica de negocio sepa que existe una base de datos.

### Stack

| Herramienta | Rol |
|-------------|-----|
| SQLite | Base de datos de desarrollo |
| SQLAlchemy | ORM + abstracción de datos |
| Alembic | Migraciones de esquema |
| Pytest + fixtures | Tests de integración |

### Conceptos clave a dominar

**El repositorio como frontera**  
La única pieza que cambia al pasar de memoria a SQLite es el repositorio. Si tu `LibraryService` necesita cambios, Stage 1 fue incorrecto.

```python
# Stage 1: repositorio en memoria
class InMemoryRepository(LibraryRepository):
    def get_book(self, book_id: int) -> Book: ...

# Stage 2: mismo contrato, diferente implementación
class SQLiteRepository(LibraryRepository):
    def get_book(self, book_id: int) -> Book: ...

# LibraryService no cambia ni una línea
```

**Migraciones como contrato**  
Alembic registra la historia de tu esquema. Una migración mal hecha en producción puede destruir datos. Tratá cada migración como código de producción: revisada, testeada, irreversible con cuidado.

**Tests de integración vs tests unitarios**  
En Stage 1 todos tus tests eran unitarios (en memoria, sin I/O). En Stage 2 añades tests de integración que hablan con SQLite real. Mantenlos separados.

```python
# conftest.py
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        session.rollback()
```

### Criterios de compleción

- [ ] Misma API de Stage 1, ahora persistida en SQLite
- [ ] Migraciones con Alembic para todos los modelos
- [ ] Tests unitarios (lógica de negocio) separados de tests de integración (repositorio)
- [ ] Los tests de Stage 1 siguen pasando sin modificaciones

### Cómo usar IA en esta stage

- Pedile que genere las migraciones de Alembic, revisalas antes de aplicar
- Usala para explorar trade-offs entre diferentes esquemas relacionales
- Preguntá: *¿qué índices necesita esta consulta?*

### Señal de que estás listo para Stage 3

Cambias de SQLite a PostgreSQL cambiando una línea de configuración y tus tests siguen pasando.

---

## Stage 3 · Security Base

### `stage3-security` · Stage 3

**Objetivo:** Que la seguridad sea un hábito, no una feature de última hora.

> Esta stage es nueva respecto al roadmap original. Ningún modelo la incluyó aquí.  
> En 2026 con IA generando código más rápido que nunca, las vulnerabilidades escalan igual de rápido.

### Stack

| Herramienta | Rol |
|-------------|-----|
| Pydantic v2 | Validación estricta de inputs |
| python-dotenv / Secrets | Gestión de variables de entorno |
| OWASP API Security Top 10 | Marco de referencia |
| Bandit | Análisis estático de seguridad |

### Conceptos clave a dominar

**OWASP API Security Top 10**  
Los 10 riesgos más comunes en APIs. No memorices la lista — entendé cada uno con un ejemplo concreto en tu proyecto.

Los más relevantes para esta stage:

- **API1**: Broken Object Level Authorization — ¿puede el usuario 2 acceder a los datos del usuario 1?
- **API3**: Broken Object Property Level Authorization — ¿devolvés más campos de los necesarios?
- **API8**: Security Misconfiguration — variables de entorno en el código, CORS abierto, debug en producción

**Validación en la frontera**  
Todo input externo es malicioso hasta demostrar lo contrario. Pydantic v2 es tu primera línea de defensa.

```python
class LoanRequest(BaseModel):
    book_id: int = Field(gt=0, description="ID must be positive")
    days: int = Field(ge=1, le=30, description="Between 1 and 30 days")

    @field_validator("book_id")
    @classmethod
    def book_id_must_exist(cls, v: int) -> int:
        # Validación de negocio en el modelo
        return v
```

**Secretos nunca en el código**  
Una API key commiteada en git es una vulnerabilidad permanente aunque la borres después. Git recuerda todo.

```bash
# .env (nunca en git)
DATABASE_URL=postgresql://user:pass@localhost/mydb
SECRET_KEY=supersecret123

# .gitignore
.env
*.env
```

### Criterios de compleción

- [ ] Revisión de toda la API contra OWASP API Top 10
- [ ] Cero secretos en el código ni en el historial de git
- [ ] Validación estricta con Pydantic en todos los endpoints
- [ ] Bandit sin warnings de severidad alta

### Cómo usar IA en esta stage

- Pedile que revise tu código buscando vulnerabilidades OWASP
- Usala para generar casos de prueba maliciosos (inputs inválidos, SQLi, etc.)
- Preguntá: *¿qué información de esta respuesta no debería exponer?*

### Señal de que estás listo para Stage 4

Puedes recibir cualquier input de un usuario y demostrar por qué no puede romper ni acceder a datos ajenos.

---

## Stage 4 · Pro Databases

### `stage4-databases` · Stage 4

**Objetivo:** Entender cuándo usar qué base de datos y por qué.

### Stack

| Herramienta | Rol |
|-------------|-----|
| PostgreSQL | Base de datos relacional de producción |
| MongoDB | Base de datos documental |
| SQLAlchemy | ORM (ahora con PostgreSQL) |
| Redis (introducción) | Cache en memoria |

### Conceptos clave a dominar

**PostgreSQL vs MongoDB — la decisión correcta**  
No es una guerra. Son herramientas para problemas diferentes.

```
Usa PostgreSQL cuando:
  - Los datos tienen relaciones claras y estables
  - Necesitás transacciones ACID
  - Las queries son complejas (JOINs, agregaciones)
  - Ejemplo: préstamos, usuarios, libros con inventario

Usa MongoDB cuando:
  - La estructura del documento varía entre registros
  - Necesitás flexibilidad de esquema
  - Escribes más de lo que leés
  - Ejemplo: logs de actividad, perfiles con campos variables
```

**Índices — el conocimiento que separa junior de senior**  
Una query sin índice en 100 registros es rápida. En 10 millones, es inaceptable. Aprendé a leer `EXPLAIN ANALYZE` en PostgreSQL.

```sql
-- Antes de añadir índice
EXPLAIN ANALYZE SELECT * FROM loans WHERE user_id = 42;
-- Seq Scan on loans (cost=0.00..2847.00 rows=1 width=64)

-- Después
CREATE INDEX idx_loans_user_id ON loans(user_id);
-- Index Scan (cost=0.00..8.28 rows=1 width=64) ← 300x más rápido
```

**Transacciones y consistencia**  
Dos operaciones que deben ocurrir juntas o no ocurrir ninguna. El ejemplo clásico: crear un préstamo Y decrementar el stock del libro en la misma transacción.

### Criterios de compleción

- [ ] API migrada de SQLite a PostgreSQL sin cambios en la lógica de negocio
- [ ] Implementación de al menos un caso de uso con MongoDB
- [ ] Análisis de queries con EXPLAIN ANALYZE y optimización con índices
- [ ] Tests de integración que validan comportamiento transaccional

### Cómo usar IA en esta stage

- Pedile que genere queries SQL y explique el plan de ejecución
- Usala para comparar trade-offs de diseño de esquema
- Preguntá: *¿qué pasa si esta operación falla a mitad de camino?*

### Señal de que estás listo para Stage 5

Puedes justificar por qué elegiste PostgreSQL o MongoDB para cada entidad de tu sistema.

---

## Stage 5 · Docker

### `stage5-docker` · Stage 5

**Objetivo:** Que tu aplicación corra igual en tu máquina, en la de tu colega, y en producción.

### Stack

| Herramienta | Rol |
|-------------|-----|
| Docker | Contenedorización |
| Docker Compose | Orquestación local |
| .dockerignore | Optimización de imágenes |
| Multi-stage builds | Imágenes ligeras de producción |

### Conceptos clave a dominar

**La imagen como unidad de despliegue**  
Una imagen Docker es inmutable. Lo que funciona en tu máquina es exactamente lo que va a producción. Eso elimina el "en mi máquina funciona".

**Multi-stage builds — imágenes de producción limpias**  

```dockerfile
# Stage de build
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage de producción — sin herramientas de build
FROM python:3.13-slim AS production
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose para el entorno completo**  

```yaml
# docker-compose.yml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      DATABASE_URL: postgresql://user:pass@db/library
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: library
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 5s
```

### Criterios de compleción

- [ ] API completa containerizada con multi-stage build
- [ ] Docker Compose con API + PostgreSQL + Redis
- [ ] Variables de entorno externalizadas (sin secretos en el Dockerfile)
- [ ] Imagen de producción < 200MB

### Cómo usar IA en esta stage

- Pedile que optimice tu Dockerfile y explique cada decisión
- Usala para diagnosticar problemas de red entre contenedores
- Preguntá: *¿qué capas de esta imagen se cachean y por qué importa?*

### Señal de que estás listo para Stage 6

`docker compose up` levanta toda tu aplicación desde cero en menos de 2 minutos, en cualquier máquina.

---

## Stage 6 · Cloud Basics

### `stage6-cloud` · Stage 6

**Objetivo:** Ver tu API funcionando en producción real, aprender conceptos de nube sin la complejidad de Kubernetes.

> Stage nueva respecto al roadmap original. Incorporada a partir del análisis de las imágenes del documento.  
> Railway y Render actúan como campo de entrenamiento antes de K8s.

### Stack

| Herramienta | Rol |
|-------------|-----|
| Railway o Render | Plataforma de despliegue |
| GitHub Actions | CI/CD básico |
| Variables de entorno en nube | Gestión de secretos en producción |

### Por qué esta stage existe

El salto de "Docker en local" a "Kubernetes" es brutal si no hay nada en el medio. Railway y Render ocultan la complejidad de la infraestructura pero te exponen a los problemas reales de producción:

```
Si tu app corre en Docker local pero falla en Render:
  → Aprendés sobre redes reales
  → Aprendés sobre permisos de Linux en producción
  → Aprendés sobre variables de entorno que olvidaste
  → Aprendés sobre health checks que nunca configuraste

Todo eso, sin administrar un cluster.
```

### Railway vs Render

| Característica | Render | Railway |
|----------------|--------|---------|
| Facilidad | Muy alta | Altísima (DX excelente) |
| Bases de datos | Postgres, Redis | Postgres, MySQL, MongoDB, Redis |
| Plan gratuito | Sí (app se suspende si inactiva) | Sí (basado en créditos) |
| Ideal para | APIs estables | Microservicios, despliegues rápidos |

**Recomendación:** Railway para este roadmap. Mejor experiencia de desarrollo y más cercano a lo que necesitarás en Stage 7 con microservicios.

### Conceptos clave a dominar

**Variables de entorno en producción**  
Lo que en local es un archivo `.env`, en producción son variables configuradas en el dashboard. Nunca hardcodées valores en la imagen.

**Health checks**  

```python
@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
```

Railway necesita saber si tu app está viva. Sin health check, no puede reiniciarla automáticamente si falla.

**Logs remotos**  
En local haces `print()`. En producción, los logs son tu único ojo dentro del sistema. Aprendé a leerlos en el dashboard de Railway.

**CI/CD básico**  

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: railway up
```

### Criterios de compleción

- [ ] API de Stage 5 desplegada en Railway con base de datos real
- [ ] Health check endpoint funcionando
- [ ] CI/CD: push a main despliega automáticamente
- [ ] URL pública que un reclutador pueda visitar

### Cómo usar IA en esta stage

- Pedile que diagnostique errores de despliegue de los logs de Railway
- Usala para configurar el pipeline de CI/CD
- Preguntá: *¿qué debería monitorear en esta aplicación?*

### Señal de que estás listo para Stage 7

Tienes una URL pública funcionando, con CI/CD automático, y entiendes qué ocurre cuando algo falla en producción.

---

## Stage 7 · Microservices

### `stage7-microservices` · Stage 7

**Objetivo:** Dividir un sistema en servicios independientes que se comunican de forma asíncrona.

### Stack

| Herramienta | Rol |
|-------------|-----|
| FastAPI | Framework de APIs |
| Redis | Cache + pub/sub |
| RabbitMQ | Message broker |
| Pact | Contract testing entre servicios |
| Docker Compose | Orquestación local multi-servicio |

### Conceptos clave a dominar

**Cuándo dividir en microservicios**  
Los microservicios no son la solución por defecto. Son la solución cuando un monolito tiene problemas reales de escala, despliegue independiente, o equipos separados.

```
Señales de que necesitás microservicios:
  - Un cambio en préstamos requiere desplegar toda la app
  - El módulo de notificaciones consume recursos que afectan al de búsqueda
  - Dos equipos trabajan en la misma base de código y se bloquean
```

**Comunicación asíncrona con RabbitMQ**  

```python
# Servicio de préstamos publica un evento
async def create_loan(loan: Loan) -> None:
    await repository.save(loan)
    await queue.publish("loans.created", {
        "loan_id": loan.id,
        "user_id": loan.user_id,
        "book_id": loan.book_id
    })

# Servicio de notificaciones consume el evento
async def on_loan_created(event: dict) -> None:
    user = await users_service.get(event["user_id"])
    await email_service.send_confirmation(user.email, event["loan_id"])
```

**Contract testing con Pact**  
Cuando tienes 6 microservicios comunicándose, los tests de integración clásicos no escalan. Contract testing define el contrato entre consumidor y proveedor de forma independiente.

```python
# El servicio de notificaciones define qué espera del servicio de usuarios
@consumer("notifications-service")
@provider("users-service")
def test_get_user_contract(pact):
    pact.given("user 42 exists").upon_receiving(
        "a request for user 42"
    ).with_request(
        method="GET", path="/users/42"
    ).will_respond_with(200, body={"id": 42, "email": "user@example.com"})
```

### Criterios de compleción

- [ ] Sistema dividido en al menos 3 servicios: loans, users, notifications
- [ ] Comunicación asíncrona via RabbitMQ para eventos de dominio
- [ ] Redis como cache de queries frecuentes
- [ ] Contract tests entre todos los servicios que se comunican
- [ ] Docker Compose que levanta el sistema completo

### Cómo usar IA en esta stage

- Pedile que identifique los límites de cada servicio (bounded contexts)
- Usala para diseñar los contratos de mensajes entre servicios
- Preguntá: *¿qué pasa si el servicio de notificaciones está caído cuando se crea un préstamo?*

### Señal de que estás listo para Stage 8

Puedes apagar un servicio y el resto del sistema sigue funcionando de forma degradada pero sin fallar completamente.

---

## Stage 8 · AI Service

### `stage8-ai` · Stage 8

**Objetivo:** Integrar IA como un microservicio más, con las mismas garantías de calidad que cualquier otro componente.

> Basado en la recomendación de Gemini: IA como servicio separado, introducido después de microservicios.  
> La IA no es el core del sistema — es un componente que puede fallar, ser reemplazado, y debe monitorearse.

### Stack

| Herramienta | Rol |
|-------------|-----|
| OpenAI API / Anthropic | LLM como servicio externo |
| pgvector | Búsqueda semántica en PostgreSQL |
| ChromaDB o Qdrant | Base de datos vectorial dedicada |
| LangSmith | Tracing de llamadas a LLM |
| Pydantic | Structured outputs del LLM |

### Conceptos clave a dominar

**RAG — Retrieval Augmented Generation**  
Conectar tu base de datos con un LLM sin reentrenarlo. El modelo no "sabe" de tu biblioteca — tu sistema le da el contexto relevante en cada consulta.

```
Usuario: "Busco algo triste para leer en un día de lluvia"
    ↓
1. Convertir la query en un embedding (vector numérico)
2. Buscar en pgvector los libros más similares semánticamente
3. Pasar esos libros como contexto al LLM
4. El LLM responde con una recomendación fundamentada en tus datos
```

**pgvector — búsqueda semántica en PostgreSQL**  

```sql
-- Extensión de PostgreSQL, no hace falta una DB nueva
CREATE EXTENSION vector;

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT,
    description TEXT,
    embedding vector(1536)  -- dimensiones del modelo de embeddings
);

-- Búsqueda por similitud coseno
SELECT title, description
FROM books
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;
```

**Structured Outputs — la IA habla con tu código**  

```python
class BookRecommendation(BaseModel):
    book_id: int
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)

# Forzamos al LLM a responder en JSON válido con esquema Pydantic
response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[...],
    response_format=BookRecommendation,
)
recommendation = response.choices[0].message.parsed
```

**LLMOps — tratar la IA como producción**  

```python
# Cada llamada al LLM debe tener:
# - Timeout
# - Retry con backoff
# - Logging de tokens, latencia y costo
# - Fallback si el servicio falla

async def call_llm_with_observability(prompt: str) -> str:
    with langsmith.trace("book-recommendation") as trace:
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                timeout=10.0
            )
            trace.log({"tokens": response.usage.total_tokens})
            return response.choices[0].message.content
        except TimeoutError:
            return await fallback_recommendation()
```

### Criterios de compleción

- [ ] Servicio de búsqueda semántica con pgvector
- [ ] Endpoint de recomendación que usa RAG
- [ ] Structured outputs para todas las respuestas del LLM
- [ ] Tracing con LangSmith: latencia, tokens, costo por request
- [ ] Fallback si el LLM no responde en menos de 10 segundos

### Cómo usar IA en esta stage

- La IA te ayuda a diseñar los prompts — iterá con ella
- Pedile que genere casos de prueba para el LLM-as-a-judge
- Preguntá: *¿cómo detecto si el LLM está alucinando en esta respuesta?*

### Señal de que estás listo para Stage 9

Tu AI Service puede caerse completamente y el resto del sistema sigue funcionando con funcionalidad reducida.

---

## Stage 9 · Kubernetes

### `stage9-k8s` · Stage 9

**Objetivo:** Entender cómo se gestiona un sistema distribuido a escala, con alta disponibilidad y despliegues sin downtime.

### Stack

| Herramienta | Rol |
|-------------|-----|
| Kubernetes | Orquestador de contenedores |
| AWS EKS o Google GKE | Kubernetes gestionado en la nube |
| kubectl | CLI de K8s |
| Helm | Gestor de paquetes para K8s |

### Por qué después de Railway

Railway te enseñó los conceptos (env vars, health checks, logs, CI/CD). Kubernetes los formaliza y los lleva a escala industrial. Sin ese puente, el golpe es duro.

```
Railway/Render te enseñó:
  - Health checks → ahora son liveness/readiness probes
  - Variables de entorno → ahora son ConfigMaps y Secrets
  - Despliegue automático → ahora son Rolling Updates
  - Logs → ahora son agregados por Fluentd/Loki
```

### Conceptos clave a dominar

**Los tres objetos fundamentales**  

```yaml
# Deployment — define cuántas réplicas corren
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: api
          image: myregistry/library-api:v1.0
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000

# Service — expone el deployment internamente
# Ingress — expone el service al exterior
```

**Rolling Updates — cero downtime**  
Kubernetes reemplaza pods uno a uno. Si el nuevo pod falla el health check, el rollout se detiene y el sistema sigue funcionando con la versión anterior.

**Horizontal Pod Autoscaler**  

```yaml
# Escala automáticamente según CPU
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Criterios de compleción

- [ ] Sistema de Stage 7 desplegado en EKS o GKE
- [ ] Rolling update sin downtime demostrado
- [ ] HPA configurado para al menos un servicio
- [ ] Secrets de K8s para todas las credenciales

### Cómo usar IA en esta stage

- Pedile que genere manifiestos YAML y explique cada campo
- Usala para diagnosticar pods en estado `CrashLoopBackOff`
- Preguntá: *¿qué pasa con las requests en vuelo durante un rolling update?*

### Señal de que estás listo para Stage 10

Puedes desplegar una nueva versión de un servicio sin que ningún usuario perciba downtime.

---

## Stage 10 · Infrastructure as Code

### `stage10-infra` · Stage 10

**Objetivo:** Que toda la infraestructura sea código versionado, reproducible y auditado.

### Stack

| Herramienta | Rol |
|-------------|-----|
| Terraform | Infraestructura como código |
| Kafka | Streaming de eventos a escala |
| AWS / GCP | Cloud provider |

### Conceptos clave a dominar

**Terraform — la infraestructura tiene historia**  

```hcl
# El cluster de K8s como código
resource "aws_eks_cluster" "library" {
  name     = "library-production"
  version  = "1.29"
  role_arn = aws_iam_role.eks.arn

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
  }
}
```

Un `terraform apply` crea la infraestructura. Un `terraform destroy` la elimina. El estado del sistema está en el repositorio, no en la cabeza de un administrador.

**Kafka — cuando RabbitMQ no escala**  
RabbitMQ (Stage 7) es excelente para colas de trabajo. Kafka es para cuando necesitás:

- Millones de eventos por segundo
- Replay de eventos históricos
- Múltiples consumidores del mismo evento
- Retención de eventos por días o semanas

### Criterios de compleción

- [ ] Cluster de K8s creado y destruido completamente con Terraform
- [ ] Al menos un caso de uso migrado de RabbitMQ a Kafka
- [ ] Estado de Terraform en S3 con locking (no en local)

### Señal de que estás listo para Stage 11

Puedes recrear todo tu entorno de producción desde cero con un solo comando.

---

## Stage 11 · Production

### `stage11-production` · Stage 11

**Objetivo:** Un sistema que sobrevive a fallos, es observable, y seguro en producción real.

### Stack

| Herramienta | Rol |
|-------------|-----|
| JWT + OAuth2 | Autenticación y autorización |
| Prometheus | Métricas |
| Grafana | Dashboards |
| OpenTelemetry | Tracing distribuido |
| LangSmith / Arize Phoenix | Observabilidad de LLMs |

### Conceptos clave a dominar

**Autenticación completa con JWT**  
JWT en Stage 11 no es solo generar un token. Es:

- Rotación de refresh tokens
- Revocación de tokens comprometidos
- Scopes y permisos por recurso
- Rate limiting por usuario autenticado

**Los cuatro pilares de observabilidad**  

```
Logs    → qué ocurrió (texto estructurado, no prints)
Metrics → cuánto ocurrió (contadores, gauges, histogramas)
Traces  → cómo ocurrió (el camino de una request por los servicios)
Alerts  → cuándo actuar (umbrales automáticos que te despiertan)
```

**LLMOps en producción**  

```python
# Métricas específicas de LLM que deberías monitorear
METRICS = {
    "llm_latency_p99": "El 99% de las llamadas responden en < N ms",
    "llm_token_cost_daily": "Costo diario de tokens en USD",
    "llm_hallucination_rate": "% de respuestas marcadas como incorrectas",
    "llm_fallback_rate": "% de veces que el fallback fue necesario"
}
```

### Criterios de compleción

- [ ] Autenticación JWT completa con refresh tokens y revocación
- [ ] Dashboard de Grafana con métricas de todos los servicios
- [ ] Tracing distribuido con OpenTelemetry (ver el camino de cada request)
- [ ] Dashboard de LLMOps con latencia, costo y tasa de alucinaciones
- [ ] Alertas configuradas para los KPIs críticos

### Señal de que estás listo para Stage 12

Cuando algo falla en producción, sabes exactamente dónde falló, por qué, y cuántos usuarios fueron afectados — antes de que te lo reporten.

---

## Stage 12 · Agents

### `stage12-agents` · Stage 12

**Objetivo:** Construir flujos donde la IA razona, toma decisiones y coordina herramientas de forma autónoma.

> Esta stage llega al final porque para diseñar agentes útiles necesitás entender qué herramientas van a usar. Sin stages 1-11, diseñarás agentes sobre arena.

### Stack

| Herramienta | Rol |
|-------------|-----|
| LangGraph | Agentes con estado y ciclos |
| Semantic Kernel | Integración empresarial de agentes |
| LLM-as-a-Judge | Evaluación automática de respuestas |

### Conceptos clave a dominar

**Qué es un agente**  
Un agente no es un prompt más largo. Es un loop: el modelo recibe una tarea, decide qué herramienta usar, ejecuta la herramienta, observa el resultado, y decide si terminó o necesita más pasos.

```python
# Un agente que gestiona préstamos
graph = StateGraph(LibraryState)

graph.add_node("understand_request", parse_user_intent)
graph.add_node("check_availability", check_book_availability)
graph.add_node("create_loan", process_loan)
graph.add_node("suggest_alternative", find_similar_books)

# El agente decide el camino según el estado
graph.add_conditional_edges(
    "check_availability",
    lambda state: "create_loan" if state.book_available else "suggest_alternative"
)
```

**Herramientas como tu API**  
Las herramientas del agente son los servicios que construiste en stages anteriores. El agente no tiene magia — llama a tus endpoints.

```python
@tool
def search_books(query: str, max_results: int = 5) -> list[Book]:
    """Search the library catalog semantically."""
    return library_service.semantic_search(query, max_results)

@tool
def check_loan_eligibility(user_id: int, book_id: int) -> EligibilityResult:
    """Check if a user can borrow a specific book."""
    return loans_service.check_eligibility(user_id, book_id)
```

**LLM-as-a-Judge**  
Cuando el agente responde, ¿cómo sabes si la respuesta es correcta? Usas un modelo más potente para evaluar las respuestas del modelo más pequeño.

### Criterios de compleción

- [ ] Agente que resuelve al menos 3 tipos de requests en lenguaje natural
- [ ] Las herramientas del agente son los servicios de stages anteriores
- [ ] LLM-as-a-Judge automático evaluando el 100% de las respuestas
- [ ] Dashboard en Grafana con métricas específicas del agente

---

## Resumen de señales de progreso

```
Stage 1  ✓  Tests pasan sin importar la implementación interna
Stage 2  ✓  Cambiar de SQLite a PostgreSQL = una línea de configuración
Stage 3  ✓  Ningún input externo puede romper ni acceder a datos ajenos
Stage 4  ✓  Puedes justificar la elección de base de datos para cada entidad
Stage 5  ✓  docker compose up levanta todo en < 2 minutos en cualquier máquina
Stage 6  ✓  URL pública con CI/CD automático y entiendes qué falla en producción
Stage 7  ✓  Un servicio caído no tumba el sistema completo
Stage 8  ✓  El AI Service caído no afecta las funcionalidades core
Stage 9  ✓  Despliegue de nueva versión sin downtime demostrado
Stage 10 ✓  Toda la infraestructura recreable desde cero con un comando
Stage 11 ✓  Sabrías dónde falló algo antes de que te lo reporten
Stage 12 ✓  Agentes que resuelven tareas reales usando tu infraestructura
```

---

## Hilo de seguridad transversal

La seguridad no es una stage — es un hábito que aplica en todas:

| Stage | Acción de seguridad |
|-------|---------------------|
| 1 | Tipos estrictos — sin datos ambiguos |
| 2 | Migraciones revisadas — sin destrucción accidental de datos |
| 3 | OWASP, validación, secretos fuera del código |
| 4 | Permisos de base de datos por principio de mínimo privilegio |
| 5 | Imágenes Docker sin root, sin secretos en capas |
| 6 | Variables de entorno en el dashboard, nunca en el repo |
| 7 | Autenticación entre microservicios (mTLS o tokens internos) |
| 8 | Rate limiting en el AI Service — los LLMs son caros |
| 9 | Network policies en K8s — servicios solo hablan con quien deben |
| 10 | IAM con mínimo privilegio en Terraform |
| 11 | JWT completo, rotación, revocación, rate limiting |
| 12 | Sandboxing de herramientas del agente — no puede llamar a lo que no debe |

---

*Documento generado con el Gentleman · Pi Agent Harness · junio 2026*
