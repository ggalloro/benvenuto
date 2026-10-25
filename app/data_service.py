"""Data access layer over the SQLite "systems of record".

In production these would be separate systems (HR, ITSM, LMS, badge office,
expense tool). The portal aggregates them; so does the onboarding agent, through
the REST API.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta

from app import config
from app.seed import seed


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


@contextmanager
def _db():
    if not config.DB_PATH.exists():
        seed(config.DB_PATH)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _rows(sql: str, *args) -> list[dict]:
    with _db() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def _one(sql: str, *args) -> dict | None:
    rows = _rows(sql, *args)
    return rows[0] if rows else None


def _execute(sql: str, *args) -> None:
    with _db() as conn:
        conn.execute(sql, args)


def _next_id(table: str, prefix: str) -> str:
    ids = [r["id"] for r in _rows(f"SELECT id FROM {table} WHERE id LIKE ?", f"{prefix}-%")]
    return f"{prefix}-{max((int(i.split('-')[1]) for i in ids), default=1000) + 1}"


def today() -> date:
    return config.TODAY


# Employees ----------------------------------------------------------------

def get_employee(employee_id: str) -> dict:
    e = _one("SELECT * FROM employees WHERE id = ?", employee_id)
    if not e:
        raise NotFound(f"Employee {employee_id} not found")
    manager = _one("SELECT first_name, last_name FROM employees WHERE id = ?", e["manager_id"])
    e["full_name"] = f"{e['first_name']} {e['last_name']}"
    e["manager_name"] = f"{manager['first_name']} {manager['last_name']}" if manager else None
    e["is_new_hire"] = bool(e["is_new_hire"])
    e["onboarding_day"] = (today() - date.fromisoformat(e["start_date"])).days + 1
    return e


def list_new_hires() -> list[dict]:
    return [get_employee(r["id"]) for r in _rows("SELECT id FROM employees WHERE is_new_hire = 1 ORDER BY id")]


def get_checklist(employee_id: str) -> list[dict]:
    get_employee(employee_id)
    return _rows("SELECT id, category, title, due_date, status FROM checklist_items "
                 "WHERE employee_id = ? ORDER BY due_date, id", employee_id)


# IT ------------------------------------------------------------------------

def get_laptop(employee_id: str) -> dict | None:
    get_employee(employee_id)
    return _one("SELECT * FROM laptops WHERE employee_id = ?", employee_id)


def get_accounts(employee_id: str) -> list[dict]:
    return _rows("SELECT system, username, status FROM accounts WHERE employee_id = ? ORDER BY id", employee_id)


# Access requests -------------------------------------------------------------

def _system(row: dict) -> dict:
    row["prerequisites"] = json.loads(row["prerequisites"])
    row["requires_manager_approval"] = bool(row["requires_manager_approval"])
    return row


def list_systems() -> list[dict]:
    return [_system(r) for r in _rows("SELECT * FROM systems ORDER BY id")]


def get_system(system_id: str) -> dict:
    row = _one("SELECT * FROM systems WHERE id = ?", system_id)
    if not row:
        raise NotFound(f"System {system_id} not found")
    return _system(row)


def _access_request(row: dict) -> dict:
    row["system_name"] = get_system(row["system_id"])["name"]
    pending = row["status"] == "pending_approval"
    row["days_pending"] = (today() - date.fromisoformat(row["updated_on"])).days if pending else 0
    return row


def list_access_requests(employee_id: str) -> list[dict]:
    get_employee(employee_id)
    rows = _rows("SELECT * FROM access_requests WHERE employee_id = ? ORDER BY requested_on, id", employee_id)
    return [_access_request(r) for r in rows]


def create_access_request(employee_id: str, system_id: str, justification: str) -> dict:
    """Records the request for the approver. Prerequisites are NOT checked here:
    the access policy is enforced downstream (approver, onboarding assistant)."""
    employee = get_employee(employee_id)
    system = get_system(system_id)
    rid = _next_id("access_requests", "AR")
    status = "pending_approval" if system["requires_manager_approval"] else "granted"
    _execute("INSERT INTO access_requests VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rid, employee_id, system_id,
             justification, status, today().isoformat(), today().isoformat(), employee["manager_id"])
    return _access_request(_one("SELECT * FROM access_requests WHERE id = ?", rid))


# Training ------------------------------------------------------------------

def get_training(employee_id: str) -> list[dict]:
    start = date.fromisoformat(get_employee(employee_id)["start_date"])
    rows = _rows("SELECT c.id AS course_id, c.title, c.duration_hours, c.due_within_days, t.status, "
                 "t.completed_on, t.session_id FROM training_records t JOIN courses c ON c.id = t.course_id "
                 "WHERE t.employee_id = ? ORDER BY c.id", employee_id)
    for r in rows:
        r["due_date"] = (start + timedelta(days=r.pop("due_within_days") - 1)).isoformat()
    return rows


def list_sessions(course_id: str | None = None) -> list[dict]:
    sql = ("SELECT s.*, c.title AS course_title FROM training_sessions s JOIN courses c ON c.id = s.course_id "
           "WHERE (? IS NULL OR s.course_id = ?) AND s.starts_at >= ? ORDER BY s.starts_at")
    return _rows(sql, course_id, course_id, today().isoformat())


def book_session(employee_id: str, session_id: str) -> dict:
    get_employee(employee_id)
    session = next((s for s in list_sessions() if s["id"] == session_id), None)
    if not session:
        raise NotFound(f"Session {session_id} not found")
    record = _one("SELECT * FROM training_records WHERE employee_id = ? AND course_id = ?",
                  employee_id, session["course_id"])
    if record and record["status"] == "completed":
        raise Conflict(f"{session['course_id']} already completed")
    if session["seats_available"] <= 0:
        raise Conflict(f"Session {session_id} is full")
    _execute("UPDATE training_sessions SET seats_available = seats_available - 1 WHERE id = ?", session_id)
    _execute("INSERT OR REPLACE INTO training_records VALUES (?, ?, 'booked', NULL, ?)",
             employee_id, session["course_id"], session_id)
    session["seats_available"] -= 1
    return dict(employee_id=employee_id, course_id=session["course_id"], session=session, status="booked")


# Badge ---------------------------------------------------------------------

def get_badge(employee_id: str) -> dict:
    get_employee(employee_id)
    badge = _one("SELECT * FROM badges WHERE employee_id = ?", employee_id)
    if not badge:
        raise NotFound(f"No badge record for {employee_id}")
    badge["sites"] = json.loads(badge["sites"])
    return badge


# Expenses ------------------------------------------------------------------

def list_expenses(employee_id: str) -> list[dict]:
    get_employee(employee_id)
    return _rows("SELECT * FROM expenses WHERE employee_id = ? ORDER BY expense_date, id", employee_id)


def create_expense(employee_id: str, data: dict) -> dict:
    """Stores the claim as submitted. Policy limits are checked by the expense
    approver (and, later, by the onboarding assistant), not by this endpoint."""
    get_employee(employee_id)
    eid = _next_id("expenses", "EX")
    _execute("INSERT INTO expenses VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'submitted', ?)", eid, employee_id,
             data["category"], data["amount"], data["currency"], data["expense_date"], data["description"],
             data.get("receipt_filename"), today().isoformat())
    return _one("SELECT * FROM expenses WHERE id = ?", eid)


# Tickets -------------------------------------------------------------------

def list_tickets(employee_id: str) -> list[dict]:
    get_employee(employee_id)
    return _rows("SELECT * FROM tickets WHERE employee_id = ? ORDER BY created_on, id", employee_id)


def create_ticket(data: dict) -> dict:
    get_employee(data["employee_id"])
    tid = _next_id("tickets", "TK")
    _execute("INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?, 'open', ?)", tid, data["employee_id"],
             data["queue"], data["subject"], data["description"], data.get("related_ref"),
             data.get("priority", "normal"), today().isoformat())
    return _one("SELECT * FROM tickets WHERE id = ?", tid)
