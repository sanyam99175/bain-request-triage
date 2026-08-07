# AI Usage Log

## Tooling
- Tool: Codex in VS Code
- Purpose: AI-assisted development, explanation, review, and test generation
- Model/API usage in product: Deterministic mock brief generator; no paid model API

---

## 2026-08-07 - Project planning

### Prompt1
```text
Help me plan a FastAPI and React JavaScript MVP for a request intake and triage tool.
The required workflow is: submit a messy request, generate a structured brief,
save it, show a reviewer queue, and support triage updates.
```

### Prompt
```text
Lets start with setup on vscode first
```

#### AI output / outcome
AI proposed a small FastAPI + React + SQLite architecture with a pluggable
BriefGenerator interface. AI also helped with setting up Python fastAPI and react environment
#### My review and action
I chose SQLite and a deterministic mock generator to keep the prototype free,
reliable, and testable. I intentionally excluded authentication and live model
integration from the MVP. I did setup by creating python environment and separating project layers in terms of frontend, backend and docs.

### Prompt2
```text
Shouldn't we crearte **init**.py
```

#### AI output / outcome
Yes—we should.
`backend/app/__init__.py` makes `app` an explicit Python package. In Rails terms,
it is roughly like establishing a namespaced module, so imports can reliably use
paths such as `from app.main import app`.

#### My review and action
I created `backend/app/__init__.py` and `backend/tests/__init__.py`. The app
package marker is required for the project's explicit import structure; the test
package marker is optional but keeps the directory structure consistent.

---

## 2026-08-07 - API entrypoint

### Prompt3
```text
Moving forward, whatever i am sending you as the prompt, i want you to add
relavant prompts in ai-usage-log.md fie in the format it is already in. Lets
start with entrypoints
```

#### AI output / outcome
AI proposed a minimal FastAPI entrypoint: create the application instance,
provide a `GET /health` route, and add one pytest test using FastAPI's
`TestClient`.

#### My review and action
I accepted this as the first vertical slice because it verifies application
startup and HTTP routing before adding database or business-request behavior.

---

## 2026-08-07 - Backend package structure

### Prompt4
```text
I started uvicorn server and it worked on /docs endpoint. Also, I have created
structure for app folders like routes, schemas etc. Please check if they look
correct. Add/remove folders as per required structure
```

#### AI output / outcome
AI confirmed the `routes`, `schemas`, `models`, and `services` folders match
the required separation. It recommended adding package markers and keeping the
layout lean until a feature needs additional structure.

#### My review and action
I kept the four required layer folders and added explicit Python package markers
to them. I did not add unused abstractions such as repositories or a separate
database folder.

---

## 2026-08-07 - SQLite configuration

### Prompt5
```text
Great. lets start with SQLite database configuration.
```

#### AI output / outcome
AI added shared SQLAlchemy configuration with a SQLite default URL, an explicit
model base class, and a request-scoped database-session dependency.

#### My review and action
I chose a file-backed SQLite database for persistence without external services.
The database URL can be replaced using the `DATABASE_URL` environment variable
when a different database is needed.
