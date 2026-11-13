# SQL Lab: FastAPI + PostgreSQL + Temporal + OpenTelemetry + Next.js

Run it: `cp .env.example .env && docker compose up --build`

| What | URL |
|---|---|
| Frontend (UI with every SQL scenario) | http://localhost:3000 |
| REST API + Swagger | http://localhost:8000/docs |
| Jaeger (traces, one span per SQL step) | http://localhost:16686 |
| Temporal UI (see which scenarios failed) | http://localhost:8080 |
| Prometheus (metrics `sql_scenarios_total`, `sql_scenario_duration_ms`) | http://localhost:9090 |
| Logs (OTLP -> collector) | `docker compose logs -f otel-collector` |

Register with the email in `ADMIN_EMAIL` to get the admin role (can commit changes and delete records).

## Structure (backend/app)
- `router/`      HTTP endpoints (`/api/v1/auth`, `/departments`, `/employees`, `/projects`, `/assignments`, `/sql-lab`)
- `schemas/`     Pydantic request/response models
- `models/`      SQLAlchemy ORM tables (users, departments, employees, projects, assignments)
- `services/`    business logic (auth, CRUD, SQL lab runner) and `sql_catalog.py` with 63 scenarios
- `repository/`  database access (generic CRUD and the raw-SQL scenario runner)
- `workflows/`   Temporal workflow and activity; `worker.py` runs them
- `core/`        config, DB engine, bcrypt + JWT security, OpenTelemetry setup

## How the SQL scenarios run
Each scenario is a list of SQL statements run in one transaction on the sandbox schema `lab`
(seeded automatically), then rolled back, so it can be run again and again. Only catalog scenarios
run; the API never executes arbitrary SQL from the client. A failed step raises a non-retryable
Temporal activity error, so it shows as FAILED in the Temporal UI and as a red span in Jaeger.
`demo-failure` fails on purpose to show this.

## Security
bcrypt hashing (`passlib[bcrypt]`), short-lived JWT access tokens plus refresh tokens, roles, CORS allow-list.
Before production: set a strong `JWT_SECRET`, serve over HTTPS, add Alembic migrations, and consider httpOnly cookies instead of localStorage.
