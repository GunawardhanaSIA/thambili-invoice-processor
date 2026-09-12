from sqlalchemy import Float, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ExistingRecord(Base):
    """Invoice records already entered into the CRM (seeded from data/existing_records.csv)."""

    __tablename__ = "existing_records"

    record_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    date_entered: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    net_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    entered_by: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="")
    cost_centre: Mapped[str] = mapped_column(String(50), nullable=False, default="")
