class InvoiceAIError(Exception):
    """Base exception for the invoice AI module."""


class ModelCallError(InvoiceAIError):
    """Raised when calling the LLM fails."""


class ModelResponseError(InvoiceAIError):
    """Raised when the LLM returns invalid output."""


class InvoiceValidationError(InvoiceAIError):
    """Raised when extracted invoice data cannot be validated."""