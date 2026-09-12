from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice import ReviewInvoice

router = APIRouter(tags=["invoices"])


@router.get("/invoices", response_model=list[ReviewInvoice])
def list_review_invoices(db: Session = Depends(get_db)) -> list[Invoice]:
    return db.query(Invoice).order_by(Invoice.created_at.desc()).all()
