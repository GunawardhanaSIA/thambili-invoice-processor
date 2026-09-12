"""Best-effort extraction of structured invoice fields from raw invoice text.

Invoice layouts vary a lot between suppliers, so this uses a set of common
label patterns (e.g. "Invoice No.", "TAX INVOICE NO", "BILL NO") and takes the
value that follows each one. Any field that can't be found is left as None
rather than guessed.
"""

import re
from dataclasses import dataclass

_CURRENCY_CODES = ("LKR", "USD", "EUR", "GBP", "INR")

_LABELS: dict[str, list[str]] = {
    "invoice_number": [
        r"invoice\s*(?:no\.?|number|#)\s*:?$",
        r"tax\s*invoice\s*no\.?$",
        r"bill\s*no\.?$",
        r"reference$",
    ],
    "invoice_date": [
        r"date\s*(?:of\s*issue)?\s*:?$",
        r"issued$",
        r"dated:?$",
    ],
    "due_date": [
        r"due\s*date\s*:?$",
        r"payment\s*due\s*:?$",
        r"due$",
        r"payable\s*by$",
    ],
    "supplier_vat_number": [
        r"vat\s*reg(?:istration)?\.?\s*(?:no\.?)?\s*:?$",
    ],
}

_AMOUNT_RE = re.compile(r"-?[\d,]+\.\d{2}")

_GENERIC_HEADER_LINES = re.compile(
    r"^(supplier|invoice|bill|tax\s*invoice|credit\s*note)s?\s*(/\s*bill)?$", re.IGNORECASE
)


def _clean_amount(raw: str) -> float | None:
    match = _AMOUNT_RE.search(raw)
    if not match:
        return None
    return float(match.group(0).replace(",", ""))


def _find_label_value(lines: list[str], patterns: list[str]) -> str | None:
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    for index, line in enumerate(lines):
        normalized = line.strip()
        if any(pattern.match(normalized) for pattern in compiled):
            # Value is usually on the same line after a ':' or on the next line.
            if ":" in normalized:
                _, _, tail = normalized.partition(":")
                tail = tail.strip()
                if tail:
                    return tail
            for next_line in lines[index + 1 : index + 3]:
                candidate = next_line.strip()
                if candidate:
                    return candidate
    return None


def _find_amount_near_label(
    lines: list[str], patterns: list[str], exclude: str | None = None
) -> float | None:
    compiled = [re.compile(p, re.IGNORECASE) for p in patterns]
    excluded = re.compile(exclude, re.IGNORECASE) if exclude else None
    for index, line in enumerate(lines):
        normalized = line.strip()
        if excluded and excluded.search(normalized):
            continue
        if any(pattern.search(normalized) for pattern in compiled):
            amount = _clean_amount(normalized)
            if amount is not None:
                return amount
            for next_line in lines[index + 1 : index + 3]:
                amount = _clean_amount(next_line)
                if amount is not None:
                    return amount
    return None


def _find_currency(text: str) -> str | None:
    for code in _CURRENCY_CODES:
        if re.search(rf"\b{code}\b", text):
            return code
    return None


@dataclass
class ParsedInvoiceFields:
    supplier_name: str | None
    supplier_vat_number: str | None
    invoice_number: str | None
    invoice_date: str | None
    due_date: str | None
    currency: str | None
    net_amount: float | None
    tax_amount: float | None
    gross_amount: float | None


def parse_invoice_fields(text: str) -> ParsedInvoiceFields:
    lines = [line for line in text.splitlines()]
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    supplier_name = next(
        (line for line in non_empty_lines if not _GENERIC_HEADER_LINES.match(line)), None
    )

    return ParsedInvoiceFields(
        supplier_name=supplier_name,
        supplier_vat_number=_find_label_value(lines, _LABELS["supplier_vat_number"]),
        invoice_number=_find_label_value(lines, _LABELS["invoice_number"]),
        invoice_date=_find_label_value(lines, _LABELS["invoice_date"]),
        due_date=_find_label_value(lines, _LABELS["due_date"]),
        currency=_find_currency(text),
        net_amount=_find_amount_near_label(
            lines, [r"subtotal", r"total\s*before\s*tax", r"total\s*value\s*of\s*goods"]
        ),
        tax_amount=_find_amount_near_label(
            lines,
            [r"vat\b(?!\s*reg)", r"tax\b(?!\s*invoice)"],
            exclude=r"before",
        ),
        gross_amount=_find_amount_near_label(
            lines, [r"total\s*payable", r"^total\b(?!\s*before)", r"grand\s*total"]
        ),
    )
