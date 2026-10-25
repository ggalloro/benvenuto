"""Runtime settings, read from environment variables."""

import os
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite file with the mock systems of record (HR, ITSM, LMS, badge, expenses).
DB_PATH = Path(os.getenv("BENVENUTO_DB", BASE_DIR / "data" / "benvenuto.db"))

# Company policies (markdown). The onboarding agent packages these as a skill.
POLICIES_DIR = Path(os.getenv("BENVENUTO_POLICIES_DIR", BASE_DIR / "policies"))

# The portal runs on a fixed "business date" (BENVENUTO_TODAY) so results are repeatable.
# Giulia Rossi starts on 2026-10-27, so 2026-10-29 is her day 3.
TODAY = date.fromisoformat(os.getenv("BENVENUTO_TODAY", "2026-10-29"))

# Default persona shown on the dashboard.
DEFAULT_EMPLOYEE_ID = os.getenv("BENVENUTO_DEFAULT_EMPLOYEE", "E1001")
