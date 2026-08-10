# Business Request Triage

A lightweight internal request-intake and reviewer-triage prototype built for a
Bain & Company software-engineer take-home assessment.

Requestors submit an unstructured business need. The backend creates a structured
brief, persists both records, and places the request in a reviewer queue. Reviewers
can assess the brief and update status, priority, and notes with an auditable
history.

## Stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic, SQLite
- Frontend: React with JavaScript and Vite
- Tests: pytest
- Brief generation: deterministic local mock by default; optional Gemini API

## Features

- Signup and login with requestor and reviewer roles.
- Request submission with a generated structured brief.
- Reviewer queue with cursor pagination.
- Reviewer triage updates for status, priority, and notes.
- Persisted triage-update history.
- Optimistic locking prevents concurrent reviewer updates from silently
  overwriting each other.
- Exact duplicate prevention using normalized SHA-256 fingerprints.
- Local, deterministic near-duplicate warning with an explicit “Submit anyway”
  choice.

## Project layout

```text
backend/
  app/
    models/       SQLAlchemy persistence models
    routes/       FastAPI HTTP endpoints
    schemas/      Pydantic request and response contracts
    services/     Brief generation, authentication, triage, duplicate detection
    migrations/   One-off SQLite upgrades for existing prototype databases
  tests/          pytest API and model tests
frontend/
  src/
    api/          HTTP client functions
    components/   Reusable React UI
    pages/        Route-level React pages
docs/
  ai-usage-log.md
  written-answers.md
```

## Setup

Prerequisites:

- Python 3.11 or later
- Node.js 20 or later with npm

### 1. Set up the backend

From the repository root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The app uses `sqlite:///./request_triage.db` by default. It creates a new SQLite
database and its tables on first startup.

### 2. Configure optional AI generation

Mock generation is the default and requires no configuration. To enable the
optional AI selection in the intake form:

```bash
cd backend
cp .env.example .env
```

Set `GEMINI_API_KEY` in `backend/.env`; do not commit that file. The unpaid
Gemini API path must only receive sanitized, non-confidential demo text. See the
known gaps below for the production constraint.

### 3. Upgrade an existing local database

If `backend/request_triage.db` was created before optimistic locking and duplicate
detection were added, stop Uvicorn and run:

```bash
cd backend
source .venv/bin/activate
python -m app.migrations.add_business_request_version
python -m app.migrations.add_request_fingerprint
```

Both commands are idempotent. The fingerprint migration preserves historical
duplicates instead of deleting records; the earliest copy becomes the canonical
match for future exact-duplicate checks.

### 4. Run the backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

The API is available at <http://127.0.0.1:8000> and interactive API docs are at
<http://127.0.0.1:8000/docs>.

### 5. Run the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Create an account and select a role, or use the
locally seeded demo accounts:

```text
requestor@demo.local / requestor-demo
reviewer@demo.local / reviewer-demo
```

## Running tests and checks

Backend tests:

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

Frontend lint and production build:

```bash
cd frontend
npm run lint
npm run build
```

## Workflow and API overview

1. A requestor signs up or logs in, then submits a request through `POST /requests`.
2. FastAPI validates the request, checks exact and near duplicates, generates a
   brief, and saves the request plus brief in one transaction.
3. A reviewer loads the paginated `GET /requests` queue and opens `GET /requests/{id}`.
4. The reviewer sends a versioned `PATCH /requests/{id}/triage` update.
5. The backend updates the current state and creates a `triage_updates` audit row
   in one transaction.

The main API endpoints are:

| Endpoint | Role | Purpose |
| --- | --- | --- |
| `POST /auth/signup` | Public | Create an account and session |
| `POST /auth/login` | Public | Create a session for an existing account |
| `POST /requests` | Requestor | Submit a request and generate a brief |
| `GET /requests` | Reviewer | Load one cursor-paginated queue page |
| `GET /requests/{id}` | Reviewer | Load the request, brief, and recent history |
| `PATCH /requests/{id}/triage` | Reviewer | Version-locked status, priority, and notes update |
| `GET /requests/{id}/triage-history` | Reviewer | Load complete triage history |

## Design decisions and assumptions

- A structured brief has one parent request. Its lists of likely users, risks,
  and clarifying questions are JSON arrays because they are generated and
  displayed as whole lists. Normalize them into child tables when individual
  items need ownership, resolution state, comments, filtering, or audit history.
- A request's `version` is optimistic locking. A stale reviewer update returns
  `409 Conflict` rather than silently overwriting a newer decision.
- Exact duplicate detection normalizes Unicode, case, spacing, and punctuation,
  then enforces a unique SHA-256 fingerprint at the database level.
- Near duplicate detection is advisory: it uses Jaccard token-set similarity,
  requires at least three shared words and 70% overlap, and compares the 200
  newest requests. It does not expose another requestor's text.
- Duplicate checks are global because requests are not yet associated with a
  submitting user. In a multi-tenant product, scope this rule by organization
  and/or submitter once ownership is modeled.
- The deterministic mock generator is the default, keeping the core workflow
  free, repeatable, and testable.

## Known gaps and production considerations

- The SQLite upgrade modules are intentionally lightweight for this prototype.
  Use versioned Alembic migrations for production deployments.
- The app is not yet multi-tenant, and `BusinessRequest` does not record the
  submitting `User`. Add organization and submitter foreign keys before sharing
  request data across real users.
- Self-service signup can select the reviewer role. Production reviewer access
  should be provisioned or approved by an administrator.
- Browser sessions use opaque bearer tokens in `localStorage` for simplicity.
  Use secure HTTP-only cookies, CSRF protection, rotation/expiry handling, and
  revocation controls in production.
- The local similarity heuristic is intentionally simple. It can miss semantic
  matches that use different vocabulary and may warn on overlapping work. Use
  full-text search for scalable candidate selection and consider approved
  embeddings only after privacy, security, and cost review.
- The optional unpaid Gemini API integration must not receive personal, sensitive,
  confidential, or client data. A production AI integration needs data
  minimization/redaction, legal and security approval, and a provider agreement
  suitable for the data classification.
- The prototype does not include email verification, password reset, rate
  limiting, centralized observability, background jobs, or deployment
  configuration.

## Documentation

- [AI usage log](docs/ai-usage-log.md)
