from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.ai_module.schemas import AIWarning, InvoiceFields


class InvoiceExtractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    success: bool
    fields: InvoiceFields
    overall_confidence: float
    confidence_level: str
    requires_review: bool
    warnings: list[AIWarning]
    error: Optional[str] = None
    created_at: datetime
