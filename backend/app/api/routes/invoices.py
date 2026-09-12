from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.existing_record import ExistingRecord
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceApprove, ReviewInvoice

router = APIRouter(tags=["invoices"])


@router.get("/invoices", response_model=list[ReviewInvoice])
def list_review_invoices(db: Session = Depends(get_db)) -> list[Invoice]:
    return (
        db.query(Invoice)
        .filter(Invoice.status != "Approved")
        .order_by(Invoice.created_at.desc())
        .all()
    )


def _next_record_id(db: Session) -> str:
    last = db.query(ExistingRecord).order_by(ExistingRecord.record_id.desc()).first()
    if last is None:
        return "FR-00001"
    try:
        next_seq = int(last.record_id.split("-")[-1]) + 1
    except ValueError:
        next_seq = 1
    return f"FR-{next_seq:05d}"


@router.post("/invoices/{invoice_id}/approve", response_model=ReviewInvoice)
def approve_invoice(
    invoice_id: str, payload: InvoiceApprove, db: Session = Depends(get_db)
) -> Invoice:
    """Approve a reviewed invoice and post it into the existing records table."""
    invoice = db.get(Invoice, invoice_id)
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")

    invoice.supplier_id = payload.supplier_id
    invoice.supplier_name = payload.supplier_name
    invoice.invoice_number = payload.invoice_number
    invoice.net_amount = payload.net_amount
    invoice.tax_amount = payload.tax_amount
    invoice.gross_amount = payload.gross_amount
    invoice.cost_centre = payload.cost_centre
    invoice.currency = payload.currency
    invoice.status = "Approved"
    invoice.issue = ""

    db.add(
        ExistingRecord(
            record_id=_next_record_id(db),
            supplier_id=invoice.supplier_id,
            supplier_name=invoice.supplier_name,
            invoice_number=invoice.invoice_number,
            date_entered=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            net_amount=invoice.net_amount,
            tax_amount=invoice.tax_amount,
            gross_amount=invoice.gross_amount,
            status="Posted",
            entered_by="Review Queue",
            currency=invoice.currency,
            cost_centre=invoice.cost_centre,
        )
    )
    db.commit()
    db.refresh(invoice)
    return invoice
