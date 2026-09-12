from typing import Optional
from pydantic import BaseModel, Field


class ExtractedTextField(BaseModel):
    value: Optional[str] = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )

    evidence: Optional[str] = None


class ExtractedAmountField(BaseModel):
    value: Optional[float] = None

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )

    evidence: Optional[str] = None


class InvoiceFields(BaseModel):

    supplier_id: ExtractedTextField = Field(
        default_factory=ExtractedTextField
    )

    supplier_name: ExtractedTextField = Field(
        default_factory=ExtractedTextField
    )

    invoice_number: ExtractedTextField = Field(
        default_factory=ExtractedTextField
    )

    invoice_date: ExtractedTextField = Field(
        default_factory=ExtractedTextField
    )

    due_date: ExtractedTextField = Field(
        default_factory=ExtractedTextField
    )

    purchase_order_number: ExtractedTextField = Field(
        default_factory=ExtractedTextField
    )

    currency: ExtractedTextField = Field(
        default_factory=ExtractedTextField
    )

    subtotal: ExtractedAmountField = Field(
        default_factory=ExtractedAmountField
    )

    tax_amount: ExtractedAmountField = Field(
        default_factory=ExtractedAmountField
    )

    discount_amount: ExtractedAmountField = Field(
        default_factory=ExtractedAmountField
    )

    total_amount: ExtractedAmountField = Field(
        default_factory=ExtractedAmountField
    )


class AIWarning(BaseModel):

    code: str

    message: str

    severity: str = "MEDIUM"

    field: Optional[str] = None


class InvoiceAIResult(BaseModel):

    success: bool

    fields: InvoiceFields = Field(
        default_factory=InvoiceFields
    )

    overall_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0
    )

    confidence_level: str = "LOW"

    requires_review: bool = True

    warnings: list[AIWarning] = Field(
        default_factory=list
    )

    error: Optional[str] = None