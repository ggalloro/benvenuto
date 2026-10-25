"""Sample data for the Benvenuto portal. Everything here is fictional."""

EMPLOYEES = [
    # Managers and people the new hires interact with.
    dict(id="E0042", first_name="Marco", last_name="Bianchi", role="Engineering Manager",
         team="Digital Channels", department="Technology", manager_id=None,
         start_date="2019-03-04", location="Milano, Piazza Gae Aulenti", is_new_hire=0, origin_city=None),
    dict(id="E0057", first_name="Chiara", last_name="Ferri", role="Head of Risk Analytics",
         team="Risk Analytics", department="Risk", manager_id=None,
         start_date="2017-09-11", location="Milano, Piazza Gae Aulenti", is_new_hire=0, origin_city=None),
    dict(id="E0063", first_name="Paolo", last_name="Greco", role="Branch Manager",
         team="Torino Centro Branch", department="Retail Banking", manager_id=None,
         start_date="2015-01-12", location="Torino, Via Roma", is_new_hire=0, origin_city=None),
    # New hires.
    dict(id="E1001", first_name="Giulia", last_name="Rossi", role="Junior Software Developer",
         team="Digital Channels", department="Technology", manager_id="E0042",
         start_date="2026-10-27", location="Milano, Piazza Gae Aulenti", is_new_hire=1, origin_city="Bari"),
    dict(id="E1002", first_name="Luca", last_name="Esposito", role="Data Analyst",
         team="Risk Analytics", department="Risk", manager_id="E0057",
         start_date="2026-09-30", location="Milano, Piazza Gae Aulenti", is_new_hire=1, origin_city="Napoli"),
    dict(id="E1003", first_name="Sara", last_name="Conti", role="Relationship Manager",
         team="Torino Centro Branch", department="Retail Banking", manager_id="E0063",
         start_date="2026-11-02", location="Torino, Via Roma", is_new_hire=1, origin_city=None),
]

# category, title, due_day (onboarding day by which it should be done)
CHECKLIST_TEMPLATE = [
    ("HR", "Sign employment contract and code of conduct", -5),
    ("HR", "Upload IBAN and tax details for payroll", 1),
    ("IT", "Receive laptop and complete first login", 3),
    ("IT", "Enroll in multi-factor authentication", 3),
    ("Security", "Upload badge photo", 2),
    ("Training", "Complete Privacy and GDPR course", 10),
    ("Training", "Complete Information Security course", 10),
    ("Training", "Complete Anti-Money Laundering (AML) course", 14),
    ("Access", "Request access to the systems for your role", 5),
    ("Team", "First 1:1 with your manager", 2),
    ("Team", "30-day check-in with your manager", 30),
]

# Status of each checklist item per employee (same order as the template).
CHECKLIST_STATUS = {
    "E1001": ["done", "done", "in_progress", "done", "todo", "done", "done", "todo", "in_progress", "done", "todo"],
    "E1002": ["done", "done", "done", "done", "done", "done", "done", "done", "done", "done", "todo"],
    "E1003": ["done", "todo", "todo", "todo", "todo", "todo", "todo", "todo", "todo", "todo", "todo"],
}

LAPTOPS = [
    dict(employee_id="E1001", model="ThinkPad T16 Gen 4, 32 GB", status="in_transit",
         shipped_on="2026-10-27", expected_delivery="2026-10-30", carrier="BRT",
         tracking_number="BRT-7781-2026-0457", delivery_address="Milano, Piazza Gae Aulenti, reception desk"),
    dict(employee_id="E1002", model="MacBook Pro 14, 36 GB", status="delivered",
         shipped_on="2026-09-28", expected_delivery="2026-09-30", carrier="BRT",
         tracking_number="BRT-7781-2026-0311", delivery_address="Milano, Piazza Gae Aulenti, reception desk"),
    dict(employee_id="E1003", model="ThinkPad T14 Gen 5, 16 GB", status="preparing",
         shipped_on=None, expected_delivery="2026-11-02", carrier=None,
         tracking_number=None, delivery_address="Torino, Via Roma branch"),
]

ACCOUNTS = [
    ("E1001", "Corporate email", "giulia.rossi@bancafutura.example", "active"),
    ("E1001", "Single sign-on and MFA", "grossi", "active"),
    ("E1001", "VPN", "grossi", "pending_laptop"),
    ("E1002", "Corporate email", "luca.esposito@bancafutura.example", "active"),
    ("E1002", "Single sign-on and MFA", "lesposito", "active"),
    ("E1002", "VPN", "lesposito", "active"),
    ("E1003", "Corporate email", "sara.conti@bancafutura.example", "provisioning"),
]

SYSTEMS = [
    dict(id="collab-suite", name="Collaboration Suite", sensitivity="low",
         description="Wiki, chat and team calendars.", requires_manager_approval=0,
         prerequisites=[], owner_team="Workplace IT"),
    dict(id="source-code", name="Source Code Platform", sensitivity="medium",
         description="Git repositories, CI pipelines and code review.", requires_manager_approval=1,
         prerequisites=["INFOSEC-101"], owner_team="Developer Platform"),
    dict(id="payments-sandbox", name="Payments Sandbox", sensitivity="medium",
         description="SEPA and instant payments test environment with synthetic accounts.",
         requires_manager_approval=1, prerequisites=["INFOSEC-101", "GDPR-101"], owner_team="Payments"),
    dict(id="core-banking-test", name="Core Banking Test Environment", sensitivity="high",
         description="Pre-production copy of the core banking platform (accounts, ledgers, customers).",
         requires_manager_approval=1, prerequisites=["AML-101", "INFOSEC-101"], owner_team="Core Banking"),
    dict(id="data-warehouse", name="Enterprise Data Warehouse", sensitivity="high",
         description="Analytical data marts with pseudonymised customer data.",
         requires_manager_approval=1, prerequisites=["GDPR-101", "INFOSEC-101"], owner_team="Data Office"),
]

ACCESS_REQUESTS = [
    # Pending approval since 2026-10-27.
    dict(id="AR-2041", employee_id="E1001", system_id="source-code",
         justification="Daily development on the mobile banking app repositories.",
         status="pending_approval", requested_on="2026-10-27", updated_on="2026-10-27", approver_id="E0042"),
    dict(id="AR-2042", employee_id="E1001", system_id="collab-suite",
         justification="Team wiki and chat.", status="granted",
         requested_on="2026-10-27", updated_on="2026-10-27", approver_id=None),
    dict(id="AR-1987", employee_id="E1002", system_id="data-warehouse",
         justification="Credit risk dashboards.", status="granted",
         requested_on="2026-10-08", updated_on="2026-10-10", approver_id="E0057"),
]

COURSES = [
    dict(id="GDPR-101", title="Privacy and GDPR essentials", duration_hours=2, due_within_days=10),
    dict(id="INFOSEC-101", title="Information Security fundamentals", duration_hours=3, due_within_days=10),
    dict(id="AML-101", title="Anti-Money Laundering (AML) and counter-terrorist financing", duration_hours=4,
         due_within_days=14),
]

TRAINING_RECORDS = [
    ("E1001", "GDPR-101", "completed", "2026-10-27"),
    ("E1001", "INFOSEC-101", "completed", "2026-10-28"),
    ("E1001", "AML-101", "not_started", None),
    ("E1002", "GDPR-101", "completed", "2026-10-02"),
    ("E1002", "INFOSEC-101", "completed", "2026-10-03"),
    ("E1002", "AML-101", "completed", "2026-10-09"),
    ("E1003", "GDPR-101", "not_started", None),
    ("E1003", "INFOSEC-101", "not_started", None),
    ("E1003", "AML-101", "not_started", None),
]

TRAINING_SESSIONS = [
    dict(id="S-AML-1103", course_id="AML-101", starts_at="2026-11-03T14:00", format="online",
         location="Virtual classroom", seats_total=25, seats_available=0),
    dict(id="S-AML-1105", course_id="AML-101", starts_at="2026-11-05T09:30", format="in_person",
         location="Milano, Piazza Gae Aulenti, Sala Verdi", seats_total=12, seats_available=4),
    dict(id="S-AML-1112", course_id="AML-101", starts_at="2026-11-12T14:00", format="online",
         location="Virtual classroom", seats_total=25, seats_available=18),
    dict(id="S-GDPR-1104", course_id="GDPR-101", starts_at="2026-11-04T10:00", format="online",
         location="Virtual classroom", seats_total=30, seats_available=22),
    dict(id="S-INFOSEC-1106", course_id="INFOSEC-101", starts_at="2026-11-06T09:00", format="in_person",
         location="Torino, Via Roma, Sala Mole", seats_total=10, seats_available=6),
]

BADGES = [
    dict(employee_id="E1001", status="pending_photo", tier="standard", badge_number=None,
         sites=["Milano Gae Aulenti"], temporary_pass="TMP-0291 (valid until 2026-11-06)"),
    dict(employee_id="E1002", status="active", tier="restricted_areas", badge_number="BF-55120",
         sites=["Milano Gae Aulenti", "Milano Data Center Lab"], temporary_pass=None),
    dict(employee_id="E1003", status="not_requested", tier="branch", badge_number=None,
         sites=["Torino Via Roma"], temporary_pass=None),
]

EXPENSES = [
    dict(id="EX-3101", employee_id="E1001", category="travel", amount=79.90, currency="EUR",
         expense_date="2026-10-25", description="Train Bari to Milano (one way)",
         receipt_filename="receipt_bari_milano_train.png", status="approved", submitted_on="2026-10-27"),
    dict(id="EX-3102", employee_id="E1001", category="temporary_housing", amount=345.00, currency="EUR",
         expense_date="2026-10-28", description="Residence Isola, 3 nights", receipt_filename=None,
         status="submitted", submitted_on="2026-10-28"),
    dict(id="EX-2950", employee_id="E1002", category="moving_services", amount=1200.00, currency="EUR",
         expense_date="2026-09-25", description="Movers Napoli to Milano", receipt_filename=None,
         status="paid", submitted_on="2026-10-02"),
]

TICKETS = [
    dict(id="TK-5501", employee_id="E1002", queue="IT", subject="Second monitor",
         description="Requesting a second 27 inch monitor.", related_ref=None, priority="low",
         status="resolved", created_on="2026-10-06"),
]
