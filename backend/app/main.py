from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api import auth, jobs, printers, stats, system, users
from .config import settings
from .db import Base, SessionLocal, engine
from .models import PrintJob, Printer, Setting, User  # noqa: F401
from .security import hash_password


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
    yield


app = FastAPI(title="PrintTool API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(printers.router, prefix="/api/printers", tags=["printers"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])

static_dir = Path(settings.static_dir)
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
