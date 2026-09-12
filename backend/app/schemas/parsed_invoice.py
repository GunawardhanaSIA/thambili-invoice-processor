from pydantic import BaseModel, ConfigDict


class ParsedInvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    supplier_name: str | None = None
    supplier_vat_number: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    due_date: str | None = None
    currency: str | None = None
    net_amount: float | None = None
    tax_amount: float | None = None
    gross_amount: float | None = None
