from pydantic import BaseModel


class ReviewInvoice(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    invoice_number: str
    net_amount: float
    tax_amount: float
    gross_amount: float
    cost_centre: str
    status: str
    issue: str
    currency: str
    document_url: str | None = None
