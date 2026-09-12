from pydantic import BaseModel, ConfigDict


class ExistingRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    record_id: str
    supplier_id: str
    supplier_name: str
    invoice_number: str
    date_entered: str
    net_amount: float
    tax_amount: float
    gross_amount: float
    status: str
    entered_by: str
    currency: str
    cost_centre: str
