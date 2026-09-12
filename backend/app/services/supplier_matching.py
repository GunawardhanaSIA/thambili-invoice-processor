"""Match an AI-extracted supplier name against the suppliers master data.

Extracted names vary in casing/punctuation/legal-suffix from the registered
name (e.g. "CEYLON FRESH PRODUCE PVT LTD" vs "Ceylon Fresh Produce (Pvt) Ltd"),
so matching normalizes both sides before comparing.
"""

import re

from sqlalchemy.orm import Session

from app.models.supplier import Supplier

_SUFFIX_PATTERN = re.compile(r"\b(pvt|private|ltd|limited|pty)\b\.?")
_NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")


def _normalize(name: str) -> str:
    name = name.lower()
    name = _SUFFIX_PATTERN.sub(" ", name)
    name = _NON_ALNUM_PATTERN.sub(" ", name)
    return " ".join(name.split())


def match_supplier_id(db: Session, supplier_name: str | None) -> str:
    if not supplier_name:
        return ""

    target = _normalize(supplier_name)
    if not target:
        return ""

    suppliers = db.query(Supplier).all()

    for supplier in suppliers:
        if _normalize(supplier.registered_name) == target or _normalize(supplier.trading_name) == target:
            return supplier.supplier_id

    for supplier in suppliers:
        norm_registered = _normalize(supplier.registered_name)
        norm_trading = _normalize(supplier.trading_name)
        if norm_trading and (norm_trading in target or target in norm_trading):
            return supplier.supplier_id
        if norm_registered and (norm_registered in target or target in norm_registered):
            return supplier.supplier_id

    return ""
