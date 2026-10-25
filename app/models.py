"""Pydantic models: the public contract of the Benvenuto REST API."""

from typing import Literal

from pydantic import BaseModel, Field


class Employee(BaseModel):
    id: str
    first_name: str
    last_name: str
    full_name: str
    role: str
    team: str
    department: str
    manager_id: str | None
    manager_name: str | None
    start_date: str
    location: str
    is_new_hire: bool
    origin_city: str | None = Field(None, description="City the employee relocated from, if any.")
    onboarding_day: int = Field(description="Day of onboarding as of the portal business date (day 1 = start date). Negative = not started yet.")


class ChecklistItem(BaseModel):
    id: int
    category: str
    title: str
    due_date: str
    status: Literal["todo", "in_progress", "done"]


class Checklist(BaseModel):
    employee_id: str
    progress_percent: int
    items: list[ChecklistItem]


class Laptop(BaseModel):
    model: str
    status: Literal["preparing", "in_transit", "delivered"]
    shipped_on: str | None
    expected_delivery: str | None
    carrier: str | None
    tracking_number: str | None
    delivery_address: str


class Account(BaseModel):
    system: str
    username: str
    status: str


class ITStatus(BaseModel):
    employee_id: str
    laptop: Laptop | None
    accounts: list[Account]


class System(BaseModel):
    id: str
    name: str
    description: str
    sensitivity: Literal["low", "medium", "high"]
    requires_manager_approval: bool
    prerequisites: list[str] = Field(description="Course ids that must be completed before access is granted (see policies/access-rules.md).")
    owner_team: str


class AccessRequest(BaseModel):
    id: str
    employee_id: str
    system_id: str
    system_name: str
    justification: str
    status: Literal["pending_approval", "granted", "rejected"]
    requested_on: str
    updated_on: str
    approver_id: str | None
    days_pending: int = Field(0, description="Days since the last update while pending.")


class AccessRequestCreate(BaseModel):
    system_id: str = Field(examples=["core-banking-test"])
    justification: str = Field(min_length=3, examples=["Integration tests for the mobile app"])


class TrainingRecord(BaseModel):
    course_id: str
    title: str
    duration_hours: int
    status: Literal["not_started", "booked", "in_progress", "completed"]
    completed_on: str | None
    due_date: str
    session_id: str | None = Field(None, description="Booked session, if any.")


class TrainingSession(BaseModel):
    id: str
    course_id: str
    course_title: str
    starts_at: str
    format: Literal["online", "in_person"]
    location: str
    seats_total: int
    seats_available: int


class BookingCreate(BaseModel):
    session_id: str = Field(examples=["S-AML-1105"])


class Booking(BaseModel):
    employee_id: str
    course_id: str
    session: TrainingSession
    status: Literal["booked"]


class Badge(BaseModel):
    employee_id: str
    status: Literal["not_requested", "pending_photo", "printing", "active", "suspended"]
    tier: str
    badge_number: str | None
    sites: list[str]
    temporary_pass: str | None


ExpenseCategory = Literal["travel", "temporary_housing", "moving_services", "meals", "other"]


class Expense(BaseModel):
    id: str
    employee_id: str
    category: ExpenseCategory
    amount: float
    currency: str
    expense_date: str
    description: str
    receipt_filename: str | None
    status: Literal["submitted", "approved", "rejected", "paid"]
    submitted_on: str


class ExpenseCreate(BaseModel):
    category: ExpenseCategory
    amount: float = Field(gt=0)
    currency: str = "EUR"
    expense_date: str = Field(examples=["2026-10-25"])
    description: str
    receipt_filename: str | None = None


class TicketCreate(BaseModel):
    employee_id: str
    queue: Literal["IT", "HR", "Security", "Payroll"]
    subject: str = Field(min_length=3)
    description: str
    related_ref: str | None = Field(None, description="Related record, e.g. an access request id.")
    priority: Literal["low", "normal", "high"] = "normal"


class Ticket(TicketCreate):
    id: str
    status: Literal["open", "in_progress", "resolved"]
    created_on: str


class PolicySummary(BaseModel):
    name: str
    title: str
    summary: str


class Policy(PolicySummary):
    content_markdown: str


class AssistantRequest(BaseModel):
    employee_id: str
    message: str
    session_id: str | None = None


class AssistantReply(BaseModel):
    reply: str
    available: bool
    session_id: str | None = None
