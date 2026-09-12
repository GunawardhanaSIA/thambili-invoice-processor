import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _new_id() -> str:
    return uuid.uuid4().hex


class InvoiceExtraction(Base):
    """Stores the AI-structured invoice fields extracted from a document's text."""

    __tablename__ = "invoice_extractions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_id)
    document_id: Mapped[str] = mapped_column(
        String(32), ForeignKey("extracted_documents.id"), nullable=False, index=True
    )
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fields: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    overall_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence_level: Mapped[str] = mapped_column(String(10), nullable=False, default="LOW")
    requires_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    warnings: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
