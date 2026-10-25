"""JSON API routes. This is the integration surface for the onboarding agent."""

from fastapi import APIRouter, HTTPException

from app import data_service as ds
from app import models
from app.services import onboarding_service, policy_service

router = APIRouter(prefix="/api")


def _call(fn, *args):
    try:
        return fn(*args)
    except ds.NotFound as e:
        raise HTTPException(404, str(e))
    except ds.Conflict as e:
        raise HTTPException(409, str(e))


@router.get("/today", tags=["portal"], summary="Portal business date")
def get_today() -> dict:
    return {"today": ds.today().isoformat()}


@router.get("/employees/{employee_id}", response_model=models.Employee, tags=["HR"])
def get_employee(employee_id: str):
    return _call(ds.get_employee, employee_id)


@router.get("/employees/{employee_id}/checklist", response_model=models.Checklist, tags=["HR"])
def get_checklist(employee_id: str):
    items = _call(ds.get_checklist, employee_id)
    return dict(employee_id=employee_id, items=items, progress_percent=onboarding_service.checklist_progress(items))


@router.get("/employees/{employee_id}/it", response_model=models.ITStatus, tags=["IT"],
            summary="Laptop shipment and account status")
def get_it(employee_id: str):
    laptop = _call(ds.get_laptop, employee_id)
    return dict(employee_id=employee_id, laptop=laptop, accounts=ds.get_accounts(employee_id))


@router.get("/systems", response_model=list[models.System], tags=["IT"],
            summary="Internal systems, sensitivity and access prerequisites")
def list_systems():
    return ds.list_systems()


@router.get("/employees/{employee_id}/access-requests", response_model=list[models.AccessRequest], tags=["IT"])
def list_access_requests(employee_id: str):
    return _call(ds.list_access_requests, employee_id)


@router.post("/employees/{employee_id}/access-requests", response_model=models.AccessRequest, status_code=201,
             tags=["IT"], summary="File an access request (recorded for the approver; prerequisites not checked)")
def create_access_request(employee_id: str, body: models.AccessRequestCreate):
    return _call(ds.create_access_request, employee_id, body.system_id, body.justification)


@router.get("/employees/{employee_id}/training", response_model=list[models.TrainingRecord], tags=["Training"])
def get_training(employee_id: str):
    return _call(ds.get_training, employee_id)


@router.get("/training/sessions", response_model=list[models.TrainingSession], tags=["Training"],
            summary="Upcoming course sessions with available seats")
def list_sessions(course_id: str | None = None):
    return ds.list_sessions(course_id)


@router.post("/employees/{employee_id}/training/bookings", response_model=models.Booking, status_code=201,
             tags=["Training"])
def book_session(employee_id: str, body: models.BookingCreate):
    return _call(ds.book_session, employee_id, body.session_id)


@router.get("/employees/{employee_id}/badge", response_model=models.Badge, tags=["Security"])
def get_badge(employee_id: str):
    return _call(ds.get_badge, employee_id)


@router.get("/employees/{employee_id}/expenses", response_model=list[models.Expense], tags=["Expenses"])
def list_expenses(employee_id: str):
    return _call(ds.list_expenses, employee_id)


@router.post("/employees/{employee_id}/expenses", response_model=models.Expense, status_code=201,
             tags=["Expenses"], summary="Submit an expense claim (policy limits not checked)")
def create_expense(employee_id: str, body: models.ExpenseCreate):
    return _call(ds.create_expense, employee_id, body.model_dump())


@router.get("/employees/{employee_id}/tickets", response_model=list[models.Ticket], tags=["Tickets"])
def list_tickets(employee_id: str):
    return _call(ds.list_tickets, employee_id)


@router.post("/tickets", response_model=models.Ticket, status_code=201, tags=["Tickets"],
             summary="Open a ticket to the HR, IT, Security or Payroll team")
def create_ticket(body: models.TicketCreate):
    return _call(ds.create_ticket, body.model_dump())


@router.get("/policies", response_model=list[models.PolicySummary], tags=["Policies"])
def list_policies():
    return policy_service.list_policies()


@router.get("/policies/{name}", response_model=models.Policy, tags=["Policies"])
def get_policy(name: str):
    return _call(policy_service.get_policy, name)


@router.post("/assistant", response_model=models.AssistantReply, tags=["Assistant"],
             summary="Onboarding assistant (placeholder)")
def assistant(body: models.AssistantRequest):
    # TODO: connect the onboarding assistant (see README, "Assistant").
    return dict(reply="Assistant not available yet. We are working on it!", available=False,
                session_id=body.session_id)
