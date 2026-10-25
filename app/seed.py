"""Create and populate the SQLite database with synthetic data.

Usage:  uv run python -m app.seed          # (re)create data/benvenuto.db
"""

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from app import config, seed_data as d

SCHEMA = """
CREATE TABLE employees (id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, role TEXT, team TEXT,
  department TEXT, manager_id TEXT, start_date TEXT, location TEXT, is_new_hire INTEGER, origin_city TEXT);
CREATE TABLE checklist_items (id INTEGER PRIMARY KEY, employee_id TEXT, category TEXT, title TEXT,
  due_date TEXT, status TEXT);
CREATE TABLE laptops (employee_id TEXT PRIMARY KEY, model TEXT, status TEXT, shipped_on TEXT,
  expected_delivery TEXT, carrier TEXT, tracking_number TEXT, delivery_address TEXT);
CREATE TABLE accounts (id INTEGER PRIMARY KEY, employee_id TEXT, system TEXT, username TEXT, status TEXT);
CREATE TABLE systems (id TEXT PRIMARY KEY, name TEXT, description TEXT, sensitivity TEXT,
  requires_manager_approval INTEGER, prerequisites TEXT, owner_team TEXT);
CREATE TABLE access_requests (id TEXT PRIMARY KEY, employee_id TEXT, system_id TEXT, justification TEXT,
  status TEXT, requested_on TEXT, updated_on TEXT, approver_id TEXT);
CREATE TABLE courses (id TEXT PRIMARY KEY, title TEXT, duration_hours INTEGER, due_within_days INTEGER);
CREATE TABLE training_records (employee_id TEXT, course_id TEXT, status TEXT, completed_on TEXT,
  session_id TEXT, PRIMARY KEY (employee_id, course_id));
CREATE TABLE training_sessions (id TEXT PRIMARY KEY, course_id TEXT, starts_at TEXT, format TEXT,
  location TEXT, seats_total INTEGER, seats_available INTEGER);
CREATE TABLE badges (employee_id TEXT PRIMARY KEY, status TEXT, tier TEXT, badge_number TEXT,
  sites TEXT, temporary_pass TEXT);
CREATE TABLE expenses (id TEXT PRIMARY KEY, employee_id TEXT, category TEXT, amount REAL, currency TEXT,
  expense_date TEXT, description TEXT, receipt_filename TEXT, status TEXT, submitted_on TEXT);
CREATE TABLE tickets (id TEXT PRIMARY KEY, employee_id TEXT, queue TEXT, subject TEXT, description TEXT,
  related_ref TEXT, priority TEXT, status TEXT, created_on TEXT);
"""


def _insert(conn: sqlite3.Connection, table: str, row: dict) -> None:
    row = {k: json.dumps(v) if isinstance(v, list) else v for k, v in row.items()}
    cols = ", ".join(row)
    marks = ", ".join("?" for _ in row)
    conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", list(row.values()))


def seed(db_path: Path = config.DB_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    for e in d.EMPLOYEES:
        _insert(conn, "employees", e)
        statuses = d.CHECKLIST_STATUS.get(e["id"])
        if statuses:
            start = date.fromisoformat(e["start_date"])
            for (category, title, due_day), status in zip(d.CHECKLIST_TEMPLATE, statuses):
                due = start + timedelta(days=due_day - 1 if due_day > 0 else due_day)
                _insert(conn, "checklist_items", dict(employee_id=e["id"], category=category,
                                                      title=title, due_date=due.isoformat(), status=status))
    for row in d.LAPTOPS:
        _insert(conn, "laptops", row)
    for emp, system, username, status in d.ACCOUNTS:
        _insert(conn, "accounts", dict(employee_id=emp, system=system, username=username, status=status))
    for row in d.SYSTEMS:
        _insert(conn, "systems", row)
    for row in d.ACCESS_REQUESTS:
        _insert(conn, "access_requests", row)
    for row in d.COURSES:
        _insert(conn, "courses", row)
    for emp, course, status, completed_on in d.TRAINING_RECORDS:
        _insert(conn, "training_records", dict(employee_id=emp, course_id=course, status=status,
                                                completed_on=completed_on, session_id=None))
    for row in d.TRAINING_SESSIONS:
        _insert(conn, "training_sessions", row)
    for row in d.BADGES:
        _insert(conn, "badges", row)
    for row in d.EXPENSES:
        _insert(conn, "expenses", row)
    for row in d.TICKETS:
        _insert(conn, "tickets", row)
    conn.commit()
    conn.close()
    return db_path


if __name__ == "__main__":
    print(f"Seeded {seed()}")
