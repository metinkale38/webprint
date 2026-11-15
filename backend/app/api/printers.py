from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.printer import Printer
from ..models.user import User
from ..schemas.printer import PrinterCreate, PrinterOut, PrinterUpdate
from ..services.discovery import scan_network
from ..utils import slugify
from .deps import get_current_user, require_admin

router = APIRouter()


@router.get("", response_model=list[PrinterOut])
def list_printers(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[Printer]:
    return db.query(Printer).order_by(Printer.name).all()


@router.post("", response_model=PrinterOut, status_code=status.HTTP_201_CREATED)
def create_printer(
    payload: PrinterCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Printer:
    slug = payload.slug or slugify(payload.name)
    exists = db.query(Printer).filter((Printer.slug == slug) | (Printer.name == payload.name)).first()
    if exists is not None:
        raise HTTPException(status_code=409, detail="Drucker existiert bereits")
    printer = Printer(**payload.model_dump(exclude={"slug"}), slug=slug)
    db.add(printer)
    db.commit()
    db.refresh(printer)
    return printer


@router.get("/{printer_id}", response_model=PrinterOut)
def get_printer(
    printer_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> Printer:
    printer = db.get(Printer, printer_id)
    if printer is None:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    return printer


@router.patch("/{printer_id}", response_model=PrinterOut)
def update_printer(
    printer_id: int,
    payload: PrinterUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> Printer:
    printer = db.get(Printer, printer_id)
    if printer is None:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(printer, field, value)
    db.commit()
    db.refresh(printer)
    return printer


@router.delete("/{printer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_printer(
    printer_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
) -> None:
    printer = db.get(Printer, printer_id)
    if printer is None:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    db.delete(printer)
    db.commit()


@router.post("/scan")
async def scan(
    _admin: User = Depends(require_admin),
) -> dict[str, list[dict]]:
    return {"printers": await scan_network()}


@router.get("/{printer_id}/capabilities")
def capabilities(
    printer_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> dict:
    printer = db.get(Printer, printer_id)
    if printer is None:
        raise HTTPException(status_code=404, detail="Drucker nicht gefunden")
    return printer.capabilities
