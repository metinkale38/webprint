from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

if TYPE_CHECKING:
    from .printer import Printer
    from .user import User


class PrintJob(Base):
    __tablename__ = "print_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    printer_id: Mapped[int] = mapped_column(ForeignKey("printers.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), default="")
    options: Mapped[dict] = mapped_column(JSON, default=dict)
    pages: Mapped[int] = mapped_column(Integer, default=1)
    copies: Mapped[int] = mapped_column(Integer, default=1)
    color_mode: Mapped[str] = mapped_column(String(16), default="monochrome")
    duplex: Mapped[str] = mapped_column(String(32), default="one-sided")
    status: Mapped[str] = mapped_column(String(32), default="queued")
    cups_job_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", lazy="joined")
    printer: Mapped["Printer"] = relationship("Printer", lazy="joined")

    @property
    def user_name(self) -> str:
        return self.user.username if self.user else ""

    @property
    def printer_name(self) -> str:
        return self.printer.name if self.printer else ""
