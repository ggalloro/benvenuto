"""API tests for the Benvenuto portal."""

GIULIO = "E1001"


def test_employee_and_onboarding_day(client):
    e = client.get(f"/api/employees/{GIULIO}").json()
    assert e["full_name"] == "Giulio Rossi"
    assert e["manager_name"] == "Marco Bianchi"
    assert e["onboarding_day"] == 3


def test_unknown_employee_404(client):
    assert client.get("/api/employees/E9999").status_code == 404


def test_checklist_progress(client):
    body = client.get(f"/api/employees/{GIULIO}/checklist").json()
    assert 0 < body["progress_percent"] < 100
    assert len(body["items"]) == 11


def test_laptop_expected_delivery(client):
    laptop = client.get(f"/api/employees/{GIULIO}/it").json()["laptop"]
    assert laptop["status"] == "in_transit"
    assert laptop["expected_delivery"] == "2026-10-30"


def test_aml_not_completed_and_core_banking_prereqs(client):
    training = {t["course_id"]: t["status"] for t in client.get(f"/api/employees/{GIULIO}/training").json()}
    assert training == {"AML-101": "not_started", "GDPR-101": "completed", "INFOSEC-101": "completed"}
    systems = {s["id"]: s for s in client.get("/api/systems").json()}
    assert set(systems["core-banking-test"]["prerequisites"]) == {"AML-101", "INFOSEC-101"}


def test_access_request_stuck_two_days(client):
    reqs = client.get(f"/api/employees/{GIULIO}/access-requests").json()
    stuck = [r for r in reqs if r["status"] == "pending_approval"]
    assert stuck[0]["id"] == "AR-2041" and stuck[0]["days_pending"] == 2


def test_access_request_post_does_not_enforce_prerequisites(client):
    # By design: the gate is enforced by the approver / onboarding agent, not here.
    r = client.post(f"/api/employees/{GIULIO}/access-requests",
                    json={"system_id": "core-banking-test", "justification": "Integration tests"})
    assert r.status_code == 201
    assert r.json()["status"] == "pending_approval"
    assert r.json()["approver_id"] == "E0042"


def test_book_aml_session(client):
    sessions = client.get("/api/training/sessions", params={"course_id": "AML-101"}).json()
    assert [s["id"] for s in sessions if s["seats_available"] > 0][0] == "S-AML-1105"
    r = client.post(f"/api/employees/{GIULIO}/training/book", json={"session_id": "S-AML-1105"})
    assert r.status_code == 201 and r.json()["session"]["seats_available"] == 3
    aml = [t for t in client.get(f"/api/employees/{GIULIO}/training").json() if t["course_id"] == "AML-101"][0]
    assert aml["status"] == "booked"


def test_full_session_and_completed_course_conflict(client):
    assert client.post(f"/api/employees/{GIULIO}/training/bookings",
                       json={"session_id": "S-AML-1103"}).status_code == 409
    assert client.post(f"/api/employees/{GIULIO}/training/bookings",
                       json={"session_id": "S-INFOSEC-1106"}).status_code == 409


def test_badge_pending_photo(client):
    assert client.get(f"/api/employees/{GIULIO}/badge").json()["status"] == "pending_photo"


def test_expenses_and_tickets(client):
    r = client.post(f"/api/employees/{GIULIO}/expenses", json={
        "category": "moving_services", "amount": 1850, "expense_date": "2026-10-24",
        "description": "Movers", "receipt_filename": "receipt_movers.png"})
    assert r.status_code == 201 and r.json()["status"] == "submitted"
    t = client.post("/api/tickets", json={"employee_id": GIULIO, "queue": "IT", "subject": "Escalation",
                                          "description": "AR-2041 pending", "related_ref": "AR-2041"})
    assert t.status_code == 201 and t.json()["status"] == "open"
    assert len(client.get(f"/api/employees/{GIULIO}/tickets").json()) == 1


def test_policies(client):
    names = {p["name"] for p in client.get("/api/policies").json()}
    assert {"access-rules", "expenses-relocation", "badges", "it-equipment", "mandatory-training"} <= names
    access = client.get("/api/policies/access-rules").json()
    assert "AML-101" in access["content_markdown"]
    assert client.get("/api/policies/..%2Fsecrets").status_code == 404


def test_assistant_placeholder(client):
    r = client.post("/api/assistant", json={"employee_id": GIULIO, "message": "When does my laptop arrive?"})
    assert r.json()["available"] is False


def test_dashboard_renders(client, monkeypatch):
    monkeypatch.delenv("CONCIERGE_AGENT_ID", raising=False)
    monkeypatch.delenv("BENVENUTO_ASSISTANT_ENABLED", raising=False)
    html = client.get("/?employee=E1001").text
    assert "Giulio" in html and "assistant-bubble" not in html
    monkeypatch.setenv("CONCIERGE_AGENT_ID", "test-engine")
    assert "assistant-bubble" in client.get("/?employee=E1001").text
    assert client.get("/policies/expenses-relocation").status_code == 200
