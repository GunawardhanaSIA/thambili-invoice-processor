from pydantic import BaseModel, ConfigDict


class Supplier(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supplier_id: str
    registered_name: str
    trading_name: str
    category: str
    address: str
    city: str
    phone: str
    email: str
    vat_number: str
    payment_terms: str
    currency: str
