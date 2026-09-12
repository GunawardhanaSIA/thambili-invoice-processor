import json
from unittest.mock import MagicMock

from app.ai_module.extractor import extract_invoice_from_images, extract_invoice_from_text

VALID_RESPONSE = json.dumps(
    {
        "supplier_name": {"value": "ABC Food Suppliers", "confidence": 0.95, "evidence": "ABC FOOD SUPPLIERS"},
        "invoice_number": {"value": "INV-1001", "confidence": 0.9, "evidence": "Invoice No: INV-1001"},
        "invoice_date": {"value": "2026-01-15", "confidence": 0.9, "evidence": "15/01/2026"},
        "due_date": {"value": None, "confidence": 0.0, "evidence": None},
        "purchase_order_number": {"value": None, "confidence": 0.0, "evidence": None},
        "currency": {"value": "LKR", "confidence": 0.9, "evidence": "LKR"},
        "subtotal": {"value": "100000.00", "confidence": 0.85, "evidence": "Subtotal 100,000.00"},
        "tax_amount": {"value": "8000.00", "confidence": 0.85, "evidence": "Tax 8,000.00"},
        "discount_amount": {"value": None, "confidence": 0.0, "evidence": None},
        "total_amount": {"value": "108000.00", "confidence": 0.95, "evidence": "Grand Total 108,000.00"},
    }
)


def _mock_client(text_response: str = VALID_RESPONSE, repair_response: str | None = None) -> MagicMock:
    client = MagicMock()
    client.extract_text_invoice.return_value = text_response
    client.extract_image_invoice.return_value = text_response
    client.repair_json.return_value = repair_response
    return client


def test_extract_invoice_from_text_success():
    client = _mock_client()

    result = extract_invoice_from_text("some invoice text", client=client)

    assert result.success is True
    assert result.fields.supplier_name.value == "ABC Food Suppliers"
    assert result.fields.total_amount.value == 108000.00
    assert result.fields.invoice_date.value == "2026-01-15"
    assert result.requires_review is False
    assert result.error is None


def test_extract_invoice_from_text_empty_text_returns_error():
    result = extract_invoice_from_text("", client=_mock_client())

    assert result.success is False
    assert result.requires_review is True
    assert result.error == "Invoice text is empty."


def test_extract_invoice_from_text_repairs_malformed_json():
    client = _mock_client(text_response="not json at all", repair_response=VALID_RESPONSE)

    result = extract_invoice_from_text("some invoice text", client=client)

    assert result.success is True
    client.repair_json.assert_called_once_with("not json at all")
    assert result.fields.invoice_number.value == "INV-1001"


def test_extract_invoice_from_text_missing_critical_field_requires_review():
    response = json.loads(VALID_RESPONSE)
    response["total_amount"] = {"value": None, "confidence": 0.0, "evidence": None}
    client = _mock_client(text_response=json.dumps(response))

    result = extract_invoice_from_text("some invoice text", client=client)

    assert result.success is True
    assert result.requires_review is True
    assert any(w.code == "MISSING_TOTAL_AMOUNT" for w in result.warnings)


def test_extract_invoice_from_images_empty_list_returns_error():
    result = extract_invoice_from_images([], client=_mock_client())

    assert result.success is False
    assert result.requires_review is True
    assert result.error == "No invoice images were provided."


def test_extract_invoice_from_images_success():
    client = _mock_client()

    result = extract_invoice_from_images(["data:image/png;base64,AAAA"], client=client)

    assert result.success is True
    client.extract_image_invoice.assert_called_once_with(["data:image/png;base64,AAAA"])
