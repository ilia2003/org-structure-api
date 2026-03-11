# Organizational Structure API

![CI](https://github.com/ilia2003/org-structure-api/actions/workflows/build.yml/badge.svg)

REST API for managing a company's organizational structure.

The system supports hierarchical departments and employees, including:

- nested department tree
- employees within departments
- department relocation
- recursive department retrieval
- cascade deletion
- employee reassignment
- PostgreSQL persistence

This project was implemented as a **technical assignment**.

---

# Tech Stack

- **FastAPI**
- **SQLAlchemy 2.0**
- **PostgreSQL**
- **Alembic**
- **Docker & Docker Compose**
- **pytest**
- **factory-boy**
- **ruff**
- **poethepoet**
- **loguru**

Python version


Python >= 3.13


---

# Project Structure


app
├── db
│ ├── crud
│ ├── migrations
│ └── models
│
├── managers
│ ├── departments.py
│ └── employees.py
│
├── routers
│ └── api
│
├── schemas
│
├── services
│ └── postgresql.py
│
├── dependencies
│
└── main.py

dev
├── factories
└── tests
├── integrations
└── managers


---

# Database Model

## ER Diagram


Department
──────────────
id
name
parent_id
created_at

Employee
──────────────
id
department_id
full_name
position
hired_at
created_at


Relations


Department 1 ─── N Employee
Department 1 ─── N Department (self reference)


---

# Example Department Tree


Company
│
├── Backend
│ ├── API
│ └── Infrastructure
│
├── Frontend
│
└── HR


---

# API Endpoints

## Create department


POST /api/v1/departments


Body

```json
{
  "name": "Backend",
  "parent_id": null
}
Create employee
POST /api/v1/departments/{department_id}/employees

Body

{
  "full_name": "John Smith",
  "position": "Backend Developer",
  "hired_at": "2026-03-11"
}
Get department with nested tree
GET /api/v1/departments/{department_id}

Query parameters

depth=1..5
include_employees=true|false

Response includes

department
employees
children
Update department
PATCH /api/v1/departments/{department_id}

Body

name
parent_id
Delete department
DELETE /api/v1/departments/{department_id}

Query

mode=cascade | reassign
reassign_to_department_id=<id>
Business Rules

department names must be unique within the same parent

department name length: 1..200

employee full_name length: 1..200

employee position length: 1..200

cannot create circular department hierarchy

cannot assign department as its own parent

employee cannot be created in non-existing department

Healthcheck
GET /api/v1/shared/healthcheck

Response

{
  "msg": "OK",
  "release": "0.1.0"
}
Installation

Clone repository

git clone https://github.com/ilia2003/org-structure-api.git
cd org-structure-api

Install dependencies

uv sync
Database

Create database

poe db-create

Drop database

poe db-drop
Migrations

Create migration

poe create-migration -m "create tables"

Apply migrations

poe apply-migrations

Rollback migration

poe revert-migration
Run Application

Development

poe start-dev

or

poe dev

Server

http://localhost:8000

Swagger

http://localhost:8000/api/docs
Production
poe start-prod
Tests

Run all tests

poe test

Managers tests

poe test-managers

Integration tests

poe test-integrations

db tests

poe test-db

Example output

50 passed in 0.36s
Linting & Formatting

Run linter

poe ruff-lint

Format code

poe ruff-format

Run both

poe format
Docker

Build and run

docker compose up --build

API

http://localhost:8000
OpenAPI

Swagger UI

/api/docs

OpenAPI schema

/api/openapi.json
Code Quality

The project follows best practices:

✔ modular architecture
✔ separated business logic and persistence layer
✔ typed codebase
✔ Pydantic schemas
✔ migrations
✔ Docker support
✔ automated tests

Author

Ilia Fedorenko

fedorenkoilia@gmail.com
