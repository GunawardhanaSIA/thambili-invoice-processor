from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ReviewInvoice(Base):
    __tablename__ = "review_invoices"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    supplier_id: Mapped[str] = mapped_column(ForeignKey("suppliers.supplier_id"), nullable=False)
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(100), nullable=False)
    net_amount: Mapped[float] = mapped_column(Float, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Float, nullable=False)
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False)
    cost_centre: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    issue: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
