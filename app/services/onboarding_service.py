"""Builds the aggregated view shown on the new-hire dashboard."""

from app import data_service as ds


def checklist_progress(items: list[dict]) -> int:
    if not items:
        return 0
    return round(100 * sum(1 for i in items if i["status"] == "done") / len(items))


def dashboard(employee_id: str) -> dict:
    employee = ds.get_employee(employee_id)
    checklist = ds.get_checklist(employee_id)
    return dict(
        employee=employee,
        today=ds.today().isoformat(),
        checklist=checklist,
        progress=checklist_progress(checklist),
        laptop=ds.get_laptop(employee_id),
        accounts=ds.get_accounts(employee_id),
        badge=ds.get_badge(employee_id),
        training=ds.get_training(employee_id),
        access_requests=ds.list_access_requests(employee_id),
        expenses=ds.list_expenses(employee_id),
        tickets=ds.list_tickets(employee_id),
        new_hires=ds.list_new_hires(),
    )
