from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Supplier(Base):
    """Thambili's registered suppliers (master data, seeded from data/suppliers.csv)."""

    __tablename__ = "suppliers"

    supplier_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    registered_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    trading_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    address: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    city: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    vat_number: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    payment_terms: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="")
