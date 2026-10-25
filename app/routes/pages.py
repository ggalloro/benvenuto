"""Server-rendered HTML pages."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app import config
from app import data_service as ds
from app.services import onboarding_service, policy_service

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=config.BASE_DIR / "app" / "templates")


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request, employee: str = config.DEFAULT_EMPLOYEE_ID):
    try:
        context = onboarding_service.dashboard(employee)
    except ds.NotFound:
        raise HTTPException(404, f"Employee {employee} not found")
    return templates.TemplateResponse(request, "dashboard.html", context)


@router.get("/policies", response_class=HTMLResponse)
def policies(request: Request, employee: str = config.DEFAULT_EMPLOYEE_ID):
    return templates.TemplateResponse(request, "policies.html", dict(
        policies=policy_service.list_policies(), employee=ds.get_employee(employee), policy=None))


@router.get("/policies/{name}", response_class=HTMLResponse)
def policy(request: Request, name: str, employee: str = config.DEFAULT_EMPLOYEE_ID):
    try:
        html = policy_service.render_policy_html(name)
    except ds.NotFound:
        raise HTTPException(404, f"Policy {name} not found")
    return templates.TemplateResponse(request, "policies.html", dict(
        policies=policy_service.list_policies(), employee=ds.get_employee(employee),
        policy=dict(name=name, html=html)))
