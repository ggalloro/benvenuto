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
# Giulio Rossi starts on 2026-10-27, so 2026-10-29 is his day 3.
TODAY = date.fromisoformat(os.getenv("BENVENUTO_TODAY", "2026-10-29"))

# Default persona shown on the dashboard.
DEFAULT_EMPLOYEE_ID = os.getenv("BENVENUTO_DEFAULT_EMPLOYEE", "E1001")


def assistant_enabled() -> bool:
    """True when the assistant chat bubble is enabled (via CONCIERGE_AGENT_ID or BENVENUTO_ASSISTANT_ENABLED)."""
    flag = os.getenv("BENVENUTO_ASSISTANT_ENABLED", "").strip().lower()
    if flag in ("1", "true", "yes", "on"):
        return True
    if flag in ("0", "false", "no", "off"):
        return False
    return bool(os.getenv("CONCIERGE_AGENT_ID", "").strip())
