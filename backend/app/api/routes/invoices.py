from fastapi import APIRouter

from app.schemas.invoice import ReviewInvoice

router = APIRouter(tags=["invoices"])


@router.get("/invoices", response_model=list[ReviewInvoice])
def list_review_invoices() -> list[ReviewInvoice]:
    return []
