from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _new_id() -> str:
    import uuid

    return uuid.uuid4().hex


class ParsedInvoice(Base):
    """Structured fields parsed out of an ExtractedDocument's raw text."""

    __tablename__ = "parsed_invoices"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)
    document_id: Mapped[str] = mapped_column(
        ForeignKey("extracted_documents.id"), nullable=False, unique=True
    )

    supplier_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplier_vat_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    due_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    net_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    tax_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    gross_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
