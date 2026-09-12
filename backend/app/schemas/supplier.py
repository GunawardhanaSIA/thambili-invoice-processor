from pydantic import BaseModel


class Supplier(BaseModel):
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
