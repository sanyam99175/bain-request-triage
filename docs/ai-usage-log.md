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

---

## 2026-08-07 - Backend implementation

### Prompt6
```text
I have added a feature branch from main for backend work. Lets start with
implementing backend like tables, models, endpoints etc.
```

#### AI output / outcome
AI proposed implementing the backend in small vertical slices, beginning with
the core persisted request model and its database-table test.

#### My review and action
I started with the `business_requests` table so later structured-brief and
triage records have a clear parent record. I used SQLAlchemy metadata creation
at application startup for the prototype; production applications should use
versioned migrations instead.

---

## 2026-08-07 - Complete persistence model

### Prompt7
```text
Lets add all tables, models that are required for responses & other features etc.
```

#### AI output / outcome
AI added models for the structured brief and triage-update history, and extended
the business request model with its current triage state and relationships.

#### My review and action
I used a one-to-one relationship for the generated brief and a one-to-many
relationship for triage history. List-like brief fields are stored as SQLite JSON
values to preserve them as arrays without adding tables that the MVP does not need.

---

## 2026-08-07 - Request submission workflow

### Prompt8
```text
Let's build the first business logic: submit a request
Add an endpoint to accept unstructured request text, generate the brief through
a BriefGenerator, and save both.
```

### Prompt9
```text
Yes, implement it
```

#### AI output / outcome
AI added a validated `POST /requests` endpoint, a deterministic implementation
of the swappable `BriefGenerator` interface, and a service that saves the
request and generated brief together.

#### My review and action
I kept the mock generator deterministic so tests are stable and no paid or live
model API is needed. The generator is provided through a FastAPI dependency, so
a real implementation can replace it later without changing the route.

---

## 2026-08-07 - Brief-generator interface

### Prompt10
```text
Lets build UI for brief generator so we can test it out.
```

### Prompt11
```text
i want to use react jsx
```

#### AI output / outcome
AI replaced the Vite starter screen with a React JSX form that submits text to
the FastAPI API and renders the resulting structured brief, loading state, and
errors. It also configured local development CORS for the Vite origin.

#### My review and action
I chose React JSX and local component state to keep the first UI small and easy
to follow. The API base URL is configurable with `VITE_API_URL`; it otherwise
uses the local FastAPI server.

---

## 2026-08-07 - Request-submission debugging

### Prompt12
```text
I am getting 500 error when clicking generate brief but i am not able to trace
it. Maybe we need to handle exception/errors better to be able to trace them.
```

#### AI output / outcome
AI inspected the local SQLite schema and identified an outdated
`business_requests` table created before later model fields were added.

#### My review and action
The local generated database contains no requests, so it can be safely reset
after stopping the server. The longer-term production solution is versioned
database migrations rather than relying on table creation at startup.

---

## 2026-08-07 - Triage ownership design

### Prompt13
```text
Great. How are we going to set owner of particular business request
```

#### AI output / outcome
AI explained that owner assignment belongs in a reviewer triage update endpoint,
which updates the request's current owner and writes a triage-history record.

#### My review and action
I will keep initial request submission unassigned, then set ownership during
review alongside status, priority, and notes so the current state and audit
history remain consistent.

---

## 2026-08-07 - Reviewer request detail

### Prompt14
```text
Ok. Let's create a new page that will show structure response and next step
suggestion. This would be basically reviewer workflow
```

#### AI output / outcome
AI added a request-detail endpoint and a React JSX reviewer page that loads a
saved request, shows every structured brief field, and visually emphasizes the
suggested next action.

#### My review and action
I used a URL-based request ID so the reviewer page works after a browser refresh
and after navigation from the intake page. A reviewer queue and triage controls
will follow as separate workflow increments.

---

## 2026-08-07 - Live mock generator

### Prompt15
```text
Lets use Live Mock AI model to generate this report
```

#### AI output / outcome
AI replaced the fixed brief output with an input-sensitive local mock generator.
It derives recommendations, users, questions, risks, and next actions from
keywords in the submitted request while producing deterministic results.

#### My review and action
I kept the implementation local and deterministic to meet the no-paid-API and
testability requirements. A real AI provider can later implement the existing
`BriefGenerator` interface without changing routes or persistence logic.

---

## 2026-08-07 - Reviewer queue and triage workflow

### Prompt16
```text
There should be queue listing, request details, triage updates, then persisted
update history—each with focused API tests.
```

#### AI output / outcome
AI planned the reviewer workflow as small increments and first added a compact
queue-listing endpoint with a focused API test.

#### My review and action
I chose a compact queue response so reviewers can scan the current state and
next action before opening the full request detail. Triage updates and history
will be implemented in the next increment.

---

## 2026-08-07 - Reviewer queue page fix

### Prompt17
```text
http://localhost:5173/requests

this gives blank page
```

#### AI output / outcome
AI diagnosed a missing React Router route for `/requests` and added a JSX
reviewer-queue page that fetches and links to saved request details.

#### My review and action
I added explicit loading, empty, and error states so an API or routing problem
does not appear as an unexplained blank page.

---

## 2026-08-08 - Reviewer queue as the entrypoint

### Prompt18
```text
I want default entrypoint to be index page of requests with an option to add
request and then the workflow goes
```

#### AI output / outcome
AI made the reviewer queue the React application's default route, moved intake
to a dedicated new-request route, and retained request-detail navigation after
submission.

#### My review and action
I kept `/requests` as an alias for the queue so existing bookmarked links
continue to work. The workflow is now queue → add request → reviewer detail →
queue.

---

## 2026-08-08 - Reviewer triage updates

### Prompt19
```text
A triage queue and request-detail view where a reviewer can see saved requests
and update at least one field, such as status, owner, priority, or notes. We
have created this view. Lets add update functionality to it to update priority
and status
```

#### AI output / outcome
AI added a validated triage-update endpoint and JSX controls for changing status
and priority. Each update also saves a persistent triage-history record and the
detail response exposes that history.

#### My review and action
I limited this increment to status and priority so the review flow stays small.
The endpoint validates controlled values, atomically updates the request and
history record, and leaves owner and notes for a follow-up increment.

---

## 2026-08-08 - React component organization

### Prompt20
```text
Can we refactor our react code to use different files for different components
rather than everything in one file?
```

#### AI output / outcome
AI separated JSX routes, pages, reusable components, and API calls into focused
files while keeping the existing frontend behavior and routes unchanged.

#### My review and action
I chose a small pages/components/api structure so each feature has an obvious
home without adding a state-management library or excessive directory layers.

---

## 2026-08-08 - Generator helper methods

### Prompt21
```text
why have declared these methods as static?
```

#### AI output / outcome
AI explained that the helper methods do not need instance state, so static
methods communicate that they are pure helper logic grouped with the generator.

#### My review and action
I kept the helpers static because they share the generator's domain but do not
need `self`. They can become instance methods if generator configuration or
provider-specific state is added later.

---

## 2026-08-08 - Paginated triage history display

### Prompt22
```text
If triage history gets too big ( lots of updates to triage ), it gets messy in
single page. AShow only 3 latest rows by default and add View complete history
button that will take you to triage history page showing complete history.
```

#### AI output / outcome
AI limited the detail-page display to the three latest updates and added a
dedicated full-history page backed by a complete triage-history API endpoint.

#### My review and action
I kept the detail view concise while preserving access to the complete audit
trail on a separate route. The history endpoint orders updates newest first.

---

## 2026-08-09 - Optional live AI provider evaluation

### Prompt23
```text
Can we use any free tier Ai endpoint for content generation to replace mock
service for brief generator. We will still load risks, questions, solution type,
likely users, and next action but that will be generated using AI rather than
mock service.
```

#### AI output / outcome
AI evaluated current free-tier options and recommended an optional Gemini API
implementation behind the existing `BriefGenerator` interface, while retaining
the deterministic mock as the default and test implementation.

#### My review and action
No live provider was added yet. A live provider would require a server-side API
key, structured-output validation, timeout and fallback handling, and only
non-confidential demo data because free-tier provider terms may allow submitted
content to improve their products.

---

## 2026-08-09 - Opt-in AI generation with mock fallback

### Prompt24
```text
Yes. We can have mock service as default and have two options ( generate through
mock service & generate through AI ) with mock service as default selected. If
user chooses to use AI, we can implement that. If due to any reason, Ai endpoint
fails or any error/exception occurs, generate report through mock service but
throwing an error notice on app that AI is down for some reason and report has
been fetched using mock service
```

#### AI output / outcome
AI added mock and AI generation options, a Gemini REST generator, and a
fail-safe fallback generator. AI failures return a safe app notice and use the
mock brief rather than failing submission.

#### My review and action
I kept mock selected by default and did not include a key in the repository.
The AI path is enabled only when `GEMINI_API_KEY` is set locally; its structured
JSON output is validated before it is saved.

---

## 2026-08-09 - AI key configuration debugging

### Prompt25
```text
I created an api key in https://aistudio.google.com/api-keys?project=flutterlogin-98993.
and used it in env file and reloaded uvicorn. but, AI fetch is still failing.
```

#### AI output / outcome
AI inspected the local configuration without exposing secrets and found that the
backend `.env` values for the Gemini key and model were empty. It also made blank
optional model configuration fall back to the supported default model.

#### My review and action
I need to place the actual API key in `backend/.env` and save the file before
restarting Uvicorn. The key remains local and uncommitted.

---

## 2026-08-09 - Gemini model availability debugging

### Prompt26
```text
I now added api key to .env and reloaded uvicorn, still it didn't work. Can you
please check if i am creating api key from right place. do not see any api key
data from my file.
```

#### AI output / outcome
AI confirmed the key loaded without displaying it, made a sanitized provider
probe, and found that the prior default Gemini model was retired for new users.
It queried the key's available models and selected `gemini-3.6-flash` after a
successful provider probe.

#### My review and action
I kept the key local and changed only the default model identifier. The mock
generator remains the default workflow option, while the AI option uses the
supported Gemini model when selected.

---

## 2026-08-09 - AI fallback after model correction

### Prompt27
```text
AI brief generation failed; using mock fallback: AIGenerationError
```

#### AI output / outcome
AI verified that a fresh backend process loads the configured key and
`gemini-3.6-flash`. A direct sanitized Gemini probe succeeded, isolating the
remaining failure to an older already-running Uvicorn process.

#### My review and action
I need to stop all existing Uvicorn processes and start a fresh server from the
`backend` directory so it imports the corrected model configuration.

---

## 2026-08-09 - Triage color indicators

### Prompt28
```text
Great. It's working. Can we have different colors for status and priority for
better indication
```

#### AI output / outcome
AI added reusable JSX status and priority badges with consistent workflow and
urgency colors across the queue, detail page, and persisted history.

#### My review and action
I used text labels as well as color so the triage state remains understandable
without relying on color alone.

---

## 2026-08-09 - Reviewer queue index

### Prompt29
```text
I see that page load time of index page has increased as the number of requests
increased. Can we. optimize db fetch using indexes ?
```

#### AI output / outcome
AI added an index on the request creation timestamp, matching the reviewer
queue's newest-first ordering query, with a focused schema test.

#### My review and action
I added only the index justified by the current query. If the queue grows much
larger, pagination will be needed because an index does not reduce the cost of
serializing every returned row.

---

## 2026-08-09 - React development load behavior

### Prompt30
```text
I see react-dom client taking long time to load which maybe preventing requests
fetch call to start. Can we fix that somehow ?
```

#### AI output / outcome
AI identified that React development StrictMode double-mounts the queue page and
therefore starts its fetch effect twice. It removed StrictMode from the app root
to issue one queue request per development page load.

#### My review and action
This is a targeted development-behavior fix, not a substitute for server-side
pagination. The queue should next paginate once request volume grows further.

---

## 2026-08-09 - Vite dependency-load diagnosis

### Prompt31
```text
http://localhost:5173/node_modules/.vite/deps/react-dom_client.js?v=08f66b66.
This is taking 5 seconds to load
```

#### AI output / outcome
AI identified this as Vite's development-only optimized dependency module rather
than an application API request. It recommended rebuilding the Vite dependency
cache once and checking behavior in the production preview.

#### My review and action
I will use Vite's supported `--force` cache rebuild before adding any custom
dependency optimizer configuration. Production builds do not serve this URL.

---

## 2026-08-09 - Application caching assessment

### Prompt32
```text
Great. Now it loads in less than a second. Cache was disabled from network. With
this cache in place, Should we cache some data that is frequently fetched but
infrequently updated. Also, Any UI fragment caching that we can perform to
improve performance?
```

#### AI output / outcome
AI assessed the current request queue and detail data as too small and mutable
to justify application caching. It recommended pagination before caching and
described browser caching of production static assets as the useful current cache.

#### My review and action
I will avoid server-side and UI-fragment caches for now because invalidation
would complicate a small prototype. I will revisit caching after measuring a
specific repeated expensive query or rendering bottleneck.

---

## 2026-08-09 - Queue pagination explanation

### Prompt33
```text
What is queue pagination and how will it help?
```

#### AI output / outcome
AI explained that pagination returns a bounded page of queue rows rather than
every request, reducing database work, payload size, and browser rendering.

#### My review and action
I will use cursor pagination when the reviewer queue needs it because the queue
is ordered newest first and new rows can arrive while a reviewer navigates.

---

## 2026-08-09 - Cursor-paginated reviewer queue

### Prompt34
```text
Great. Let's implement this. It will help with large number of requests.
```

#### AI output / outcome
AI implemented cursor pagination for the reviewer queue, returning 25 items by
default with an opaque next cursor and a frontend Load more requests control.

#### My review and action
I used the `(created_at, id)` sort key and composite index to keep pagination
stable as new requests arrive. The API enforces a maximum page size of 100.

---

## 2026-08-09 - Authentication and role separation design

### Prompt35
```text
Let's add authentication or role separation between requestor and reviewer
```

#### AI output / outcome
AI distinguished a lightweight demonstrative role switcher from real
authentication and authorization, which requires persistent users, credentials,
sessions or tokens, and server-side access checks.

#### My review and action
I need to choose whether the assessment prototype should demonstrate role-based
UI flows only or expand into real authentication before implementation begins.

---

## 2026-08-09 - Real authentication foundation

### Prompt37
```text
This doesn't differentiate much between requestor and reviewer. lets add real authentication.
```

#### AI output / outcome
AI added local users, PBKDF2 password hashes, hashed opaque bearer sessions,
demo-account seeding, and a tested login endpoint as the first authentication
increment.

#### My review and action
I chose database-backed opaque tokens so sessions can be revoked later and raw
tokens are never stored. The next increment will apply authenticated identities
and role checks to request and triage endpoints, then replace the demo switcher
with a login screen.

---

## 2026-08-09 - Server-side role authorization

### Prompt38
```text
yes go ahead
```

#### AI output / outcome
AI added bearer-token authentication dependencies and server-side role checks:
requestors can submit requests, while reviewers can access the queue, details,
history, and triage updates.

#### My review and action
I made the backend return `401` for missing or invalid tokens and `403` for a
valid user with the wrong role. The next increment will connect the React app to
login and replace demo-only client role selection.

---

## 2026-08-09 - Frontend authentication integration

### Prompt39
```text
yes
```

#### AI output / outcome
AI replaced the demo role switcher with a login screen, session storage, bearer
token attachment for API calls, authenticated route guards, and sign-out.

#### My review and action
I store the local prototype's opaque token in browser storage and derive UI
access from the authenticated server response. Production systems should prefer
secure, httpOnly cookies and add token-expiry handling.

---

## 2026-08-09 - CORS preflight troubleshooting

### Prompt40
```text
Access to fetch at 'http://127.0.0.1:8000/requests?limit=5' from origin 'http://localhost:5173' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: It does not have HTTP ok status.
when logging in as reviewer
```

#### AI output / outcome
AI identified that authenticated browser requests send an `Authorization` header,
which must be explicitly allowed by the FastAPI CORS middleware for the browser's
preflight request to succeed.

#### My review and action
I added only `Authorization` to the allowed CORS request headers. This preserves
the existing specific origins and methods rather than using an unnecessarily broad
development configuration.

---

## 2026-08-09 - Demo role separation implementation

### Prompt36
```text
for now, lets do demo role separation
```

#### AI output / outcome
AI added a persistent React demo-role switcher, role-specific home workflows,
reviewer-only queue/history/triage controls, and requestor submission/detail
views.

#### My review and action
I kept this as an explicit demo feature rather than authentication. The browser
can switch roles, and the backend does not enforce access; real authorization is
a separate future scope.

---

## 2026-08-09 - Request submission confirmation

### Prompt41
```text
When request submit is successful, display a notification message that request have been submitted. reviewer will review it soon. something like that
```

#### AI output / outcome
AI rendered a success notification on the requestor home page after a successful
submission: “Request submitted successfully. A reviewer will review it soon.”

#### My review and action
I reused the existing navigation success state rather than adding new server
state. The message is marked as a status update so assistive technology can
announce it after the navigation.

---

## 2026-08-09 - Reviewer UI and account signup

### Prompt42
```text
Add request button shouldn't be visible for reviewer. Also, Rather than fixed credentials to login. It's better we introduce signup with email password & role selection.
```

#### AI output / outcome
AI separated the work into two testable increments: first remove the reviewer
queue's incorrect request-submission button; next add user registration with an
email, password, and role selection.

#### My review and action
I removed the reviewer button while retaining route and backend role protection.
Signup will be implemented as the next vertical slice so the account-creation API
and its validation can be tested independently.

---

## 2026-08-09 - Signup endpoint

### Prompt43
```text
yes
```

#### AI output / outcome
AI added a signup endpoint that validates email, password, and selected role,
hashes the password, persists the user, and returns an authenticated session.

#### My review and action
I made duplicate email registration return `409 Conflict` and added an API test
covering successful reviewer signup and duplicate-email rejection. The React
signup form remains the next separate increment.

---

## 2026-08-09 - Signup screen

### Prompt44
```text
yes
```

#### AI output / outcome
AI added a React signup page with email, password, and role selection, connected
it to the signup endpoint, and signed users in automatically after registration.

#### My review and action
I removed prefilled demo credentials from the login form and added reciprocal
login/signup links. The selected role determines the first workflow shown after
registration, while the backend remains responsible for enforcing permissions.

---

## 2026-08-09 - Concurrent triage updates

### Prompt45
```text
should I be worried about concurrency? Suppose on production, there are multiple reviewers and two of them updates the triage at same time? Should we implement optimistic locking?
```

#### AI output / outcome
AI identified a last-write-wins race in the current triage update flow and
recommended optimistic locking for concurrent reviewer edits.

#### My review and action
No implementation was made in this step. The proposed next change is a
`version` column sent with the request update; a stale version will return
`409 Conflict` instead of silently overwriting a newer review decision.

---

## 2026-08-09 - Optimistic locking implementation

### Prompt46
```text
Yes, implement the version locking for triage update.
```

#### AI output / outcome
AI added a version column and an atomic compare-and-swap triage update. A stale
version now returns `409 Conflict`; no overwrite or additional history record is
created.

#### My review and action
I added a one-off SQLite migration command for existing local databases. The
frontend will send the displayed version and explain the conflict in the next
separate increment.

#### Follow-up action
I connected the reviewer triage form to send the displayed version and remount
after a successful, incremented response. A stale submission shows the API's
refresh-and-review conflict message.

---

## 2026-08-09 - Structured brief list storage

### Prompt47
```text
I see that structured brief table has columns that store users, risks etc in form of array of strings. Is this approach safer and extendable for production. SHould we use associations in this case? Like one brief can have many questions, many risks.
```

#### AI output / outcome
AI explained the trade-off between JSON text arrays and normalized child records
for brief risks, questions, and likely users.

#### My review and action
No schema change was made. JSON arrays remain appropriate while the generated
items are read-only display content; associations become appropriate when items
need individual ownership, state, metadata, filtering, or audit history.

---

## 2026-08-09 - AI data safety

### Prompt48
```text
Also just wanted to be sure, Are we safe sending request to AI? In future, if we want to inclue user name in request, would that be safe?
```

#### AI output / outcome
AI inspected the Gemini request payload and reviewed the current official Gemini
API data-use terms. The optional unpaid AI path sends the complete request text
to the external provider and is not suitable for personal, sensitive, or
confidential data.

#### My review and action
I removed a real-looking credential from the example environment file and
replaced it with a placeholder. A production implementation should minimize or
redact prompt data, obtain the required approvals, and use a provider plan and
data-handling agreement suitable for confidential business data.

---

## 2026-08-09 - Reviewer triage notes

### Prompt49
```text
Also, I dont see any option to add notes to triage. Implement that field for a reviewer
```

#### AI output / outcome
AI added notes to the validated triage-update API contract and persisted the
current note plus its history snapshot in the same version-locked transaction.

#### My review and action
Notes may be changed independently of status and priority. Omitted notes remain
unchanged, while an explicitly empty value can clear them; whitespace is trimmed.
The reviewer form will be connected in the next small increment.

#### Follow-up action
I added a reviewer notes textarea, included it in the version-locked update
request, and display notes in both the recent and complete triage histories.

---

## 2026-08-09 - Triage notes verification

### Prompt50
```text
I don't see notes column value updated in db table
```

#### AI output / outcome
AI inspected the local SQLite database and confirmed that the latest request's
`business_requests.notes` value and its associated triage-history snapshots are
being updated correctly.

#### My review and action
No code change was needed. The likely issue is inspecting a different request
row or database file; the verified recent row contains the saved note.

---

## 2026-08-10 - Duplicate business-request validation

### Prompt51
```text
Lets work on adding validation to business request in a way that it detects duplicate request and inform the user that same request exists. Suggest me some ideas on how it can be implemented? One idea i have in mind is through AI to detect similar request and avoid creration of request. I am not sure if there is any manual direct way to detect it.
```

#### AI output / outcome
AI recommended a staged approach: enforce exact duplicates with a normalized
database fingerprint and use deterministic local text similarity to warn about
near-duplicates. AI-based similarity was identified as optional, not the first
or only guard.

#### My review and action
No implementation was made in this step. The proposed first increment is a
unique normalized-request fingerprint, returning `409 Conflict` and the existing
request ID before any brief generation occurs.

---

## 2026-08-10 - Exact duplicate prevention

### Prompt52
```text
Yeah. This approach works but only if we pass almost the same text. We can AI enhancement for future. Lets implement using fingerprinting & local similarity.
```

#### AI output / outcome
AI began with exact duplicate prevention using a normalized SHA-256 fingerprint
and a database unique index, before adding deterministic local near-similarity.

#### My review and action
I chose global duplicate detection because requests are not yet associated with a
submitting user. Exact duplicates return `409 Conflict` before brief generation;
the local SQLite migration backfills fingerprints while preserving historical
duplicates under distinct legacy fingerprints so the unique index can be added.

#### Follow-up action
I added deterministic local token-set similarity with a 70% threshold and a
minimum of three shared tokens. A possible match returns a structured `409`
warning; requestors may explicitly submit anyway, while exact matches remain
blocked.

#### Follow-up action
I added requestor-facing handling: exact duplicates show an error, while a local
similarity warning explains the choice and provides a separate submit-anyway
action. Similar request text is not exposed to the requestor.

---

## 2026-08-10 - Duplicate feedback placement

### Prompt53
```text
Put the error/warning above test input field to be clearly visible
```

#### AI output / outcome
AI moved duplicate errors and similarity warnings inside the request form,
immediately above the business-request textarea.

#### My review and action
I kept the messages as accessible alerts and added form-specific spacing, so the
feedback is visually associated with the text input it concerns.

---

## 2026-08-10 - Transient submission confirmation

### Prompt54
```text
Request submitted successfully. A reviewer will review it soon. this message after successful request submission stays and doesn't go.
```

#### AI output / outcome
AI changed the submission confirmation from persistent route state into a
transient flash-style message.

#### My review and action
I consume the navigation state immediately and dismiss the local message after
five seconds, preventing it from reappearing on refresh or later navigation.

---

## 2026-08-10 - Local similarity explanation

### Prompt55
```text
Can you explain me what logic you used to detect similar requests and not completely identical?
```

#### AI output / outcome
AI explained the deterministic token-set Jaccard similarity rule used for
near-duplicate request warnings.

#### My review and action
No code change was made. The current rule requires at least three shared words
and 70% overlap among normalized unique words, so it remains explainable and
does not rely on an external AI service.

---

## 2026-08-11 - Test coverage and role visibility audit

### Prompt56
```text
Have we covered all test cases? Did we add a test case to check requester & reviewer separate visibilty?
```

#### AI output / outcome
AI audited the current suite and found partial API role-separation coverage but
no React component or browser-level visibility tests.

#### My review and action
No test was added in this audit step. The recommended next increment is to add
focused API tests that deny requestors access to detail, history, and triage
updates, then add frontend tests for role-specific navigation and route guards.

---

## 2026-08-11 - Reviewer page authorization tests

### Prompt57
```text
Can we not add backend test cases to check routes and accessibility in a way that requesteor cannot access /requests . If yes, let's add minimal test cases to verify requestor and reviewer accessibility to 3 pagesd we have
```

#### AI output / outcome
AI expanded the existing backend authorization test to cover the reviewer queue,
request detail, and triage-history routes for both roles.

#### My review and action
The test now asserts that requestors receive `403` and reviewers receive `200`
for all three reviewer pages. This covers backend authorization; React visibility
and redirects remain a separate frontend-testing concern.

---

## 2026-08-11 - Requestor brief exposure review

### Prompt58
```text
I found one issue after hosting on production. As a requestor, I can send a requestor but not be able to see the generted response in UI, but i can see that in response tab in network console. Is this an issue? Because as a requestor, I should not be able to see the generated brief. right?
```

#### AI output / outcome
AI confirmed that the request-submission endpoint currently returns the complete
structured brief to a requestor even though the React UI does not render it.

#### My review and action
No code change was made in this diagnostic step. The proposed fix is a dedicated
requestor submission-response schema with acknowledgement-only fields; the full
brief remains available only from reviewer-authorized endpoints.

---

## 2026-08-11 - Requestor-safe submission response

### Prompt59
```text
yes lets implement it
```

#### AI output / outcome
AI replaced the request-submission response with an acknowledgement-only schema
and retained the complete brief solely in reviewer-authorized detail responses.

#### My review and action
I added tests asserting that requestor submission responses omit `brief` and
triage history, while the reviewer detail response includes the structured brief.
