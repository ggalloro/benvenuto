"""FastAPI entry point.  Run:  uv run uvicorn app.main:app --reload"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from app import config
from app.routes import api, pages

app = FastAPI(
    title="Benvenuto API",
    version="1.4.0",
    description="Banca Futura new-hire portal. Aggregates HR, IT, training, badge and expense systems "
                "(synthetic data). All dates are relative to the portal business date (GET /api/today).",
)
app.mount("/static", StaticFiles(directory=config.BASE_DIR / "app" / "static"), name="static")
app.include_router(api.router)
app.include_router(pages.router)


@app.middleware("http")
async def no_cache_static(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict:
    return {"status": "ok"}
