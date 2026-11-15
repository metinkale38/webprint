import asyncio
from contextlib import asynccontextmanager, suppress
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .api import auth, jobs, printers, stats, system, users
from .config import settings
from .db import Base, SessionLocal, engine
from .models import PrintJob, Printer, Setting, User  # noqa: F401
from .security import hash_password
from .services.discovery import discovery_loop
from .services.job_sync import job_sync_loop


def bootstrap_admin() -> None:
    if not settings.admin_username or not settings.admin_password:
        return
    with SessionLocal() as db:
        if db.query(User).filter(User.role == "admin").first():
            return
        if db.query(User).filter(User.username == settings.admin_username).first():
            return
        db.add(
            User(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
                display_name="Administrator",
                role="admin",
            )
        )
        db.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    bootstrap_admin()

    background_tasks = []
    if settings.discovery_enabled:
        background_tasks.append(asyncio.create_task(discovery_loop(settings.discovery_interval)))
    if settings.job_sync_enabled:
        background_tasks.append(asyncio.create_task(job_sync_loop(settings.job_sync_interval)))

    try:
        yield
    finally:
        for task in background_tasks:
            task.cancel()
        for task in background_tasks:
            with suppress(asyncio.CancelledError):
                await task


app = FastAPI(title="PrintTool API", version="0.8.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            length = int(content_length)
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Ungültiger Content-Length"})
        max_bytes = settings.upload_max_mb * 1024 * 1024 + 1_000_000
        if length > max_bytes:
            return JSONResponse(status_code=413, content={"detail": "Datei zu groß"})
    return await call_next(request)


@app.middleware("http")
async def security_headers(_request: Request, call_next):
    response = await call_next(_request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault(
        "Permissions-Policy", "geolocation=(), microphone=(), camera=()"
    )
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; "
        "form-action 'self'",
    )
    return response


app.include_router(system.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(printers.router, prefix="/api/printers", tags=["printers"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])

static_dir = Path(settings.static_dir)
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
