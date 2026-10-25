# Benvenuto · Banca Futura new-hire portal

Benvenuto is the onboarding portal that new hires at **Banca Futura** (a fictional Italian bank) use in their first 30 days. It aggregates the bank's systems of record behind one dashboard and one REST API:

- **HR**: employee profile, onboarding checklist.
- **IT**: laptop shipment, accounts, access requests to internal systems.
- **Training (LMS)**: mandatory courses (GDPR, Information Security, AML) and course sessions.
- **Security**: badge status.
- **Expenses**: relocation expense claims.
- **Service desk**: tickets to the HR, IT, Security and Payroll teams.
- **Policies**: company policies as markdown documents in [`policies/`](policies/).

The portal has a floating **assistant bubble** that is not connected to anything yet: `POST /api/assistant` answers "Assistant not available yet" and the frontend calls it through a single `askAssistant()` function in [`app/static/js/assistant.js`](app/static/js/assistant.js).

> All people, systems, vendors and data in this repository are synthetic.

## Run locally

Requirements: Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python -m app.seed            # (re)create data/benvenuto.db with sample data
uv run uvicorn app.main:app --reload
```

Open:
- Dashboard: http://localhost:8000 (persona picker in the header card; default Giulio Rossi, `E1001`)
- Policies: http://localhost:8000/policies
- OpenAPI docs: http://localhost:8000/docs (spec at `/openapi.json`)

The database is created and seeded automatically on the first request if it does not exist. Re-run `python -m app.seed` at any time to reset the data.

### Business date

All dates are computed against a fixed **portal business date**, so results are repeatable: `BENVENUTO_TODAY` (default `2026-10-29`). `GET /api/today` returns it. Other settings: `BENVENUTO_DB` (SQLite path), `BENVENUTO_POLICIES_DIR`, `BENVENUTO_DEFAULT_EMPLOYEE`.

## Tests

```bash
uv run pytest -q
```


## REST API

| Method | Path | Description |
|---|---|---|
| GET | `/api/today` | Portal business date |
| GET | `/api/employees/{id}` | Profile, manager, start date, `onboarding_day` |
| GET | `/api/employees/{id}/checklist` | Checklist items and `progress_percent` |
| GET | `/api/employees/{id}/it` | Laptop shipment (status, expected delivery, tracking) and accounts |
| GET | `/api/systems` | Internal systems with sensitivity, manager approval flag and prerequisite courses |
| GET | `/api/employees/{id}/access-requests` | Access requests with `status` and `days_pending` |
| POST | `/api/employees/{id}/access-requests` | File an access request `{system_id, justification}` |
| GET | `/api/employees/{id}/training` | Mandatory courses: status, due date, booked session |
| GET | `/api/training/sessions?course_id=` | Upcoming sessions with seats available |
| POST | `/api/employees/{id}/training/bookings` | Book a session `{session_id}` (409 if full or already completed) |
| GET | `/api/employees/{id}/badge` | Badge status, tier, sites, temporary pass |
| GET | `/api/employees/{id}/expenses` | Relocation expense claims |
| POST | `/api/employees/{id}/expenses` | Submit a claim `{category, amount, currency, expense_date, description, receipt_filename}` |
| GET | `/api/employees/{id}/tickets` | Tickets opened by the employee |
| POST | `/api/tickets` | Open a ticket `{employee_id, queue, subject, description, related_ref, priority}` |
| GET | `/api/policies` | Policy list (name, title, summary) |
| GET | `/api/policies/{name}` | Policy markdown |
| POST | `/api/assistant` | Assistant placeholder `{employee_id, message, session_id}` |

Known behaviour to be aware of:
- `POST /access-requests` **records** the request (status `pending_approval` for medium/high systems) and does **not** check training prerequisites. The access policy is enforced by the approver, not by this endpoint.
- `POST /expenses` stores the claim as `submitted` and does **not** check policy limits or the eligibility window.
- There is no authentication: the portal trusts the `employee_id` in the path (no authentication yet).

## Project structure

```
app/
  main.py                 FastAPI app (API + pages + static)
  config.py               Settings from env vars
  models.py               Pydantic models (the API contract)
  data_service.py         SQLite data access (mock systems of record)
  seed.py, seed_data.py   Schema and synthetic data
  routes/api.py           JSON API
  routes/pages.py         Dashboard and policy pages (Jinja2)
  services/               Dashboard aggregation, policy loader
  templates/, static/     UI, assistant bubble (assistant.js)
policies/                 Company policies (markdown with front matter)
tests/                    pytest suite
```

## Deploy to Cloud Run

```bash
gcloud run deploy benvenuto --source . --region europe-west1 --allow-unauthenticated --max-instances 1
```

The container seeds a fresh SQLite database in `/tmp` on startup, so each new instance starts from the sample data. Keep `--max-instances 1` so all requests share one database.
