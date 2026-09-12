import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


class Invoice(Base):
    """A supplier invoice in the review queue, populated from an AI extraction."""

    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)
    document_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("extracted_documents.id"), nullable=False, index=True
    )
    extraction_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("invoice_extractions.id"), nullable=False
    )
    supplier_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    supplier_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    net_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    gross_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cost_centre: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Pending Review")
    issue: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="")
    document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
