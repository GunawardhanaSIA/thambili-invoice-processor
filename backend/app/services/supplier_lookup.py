from sqlalchemy.orm import Session

from app.models.supplier import Supplier


def format_known_suppliers(db: Session) -> str:
    """Format the suppliers master data as a compact block for the LLM prompt.

    One line per supplier: "supplier_id | registered_name | trading_name".
    The LLM matches the invoice's supplier against this list itself and
    returns the matching supplier_id (see ai_module/prompts.py).
    """
    suppliers = db.query(Supplier).order_by(Supplier.supplier_id).all()
    if not suppliers:
        return ""

    return "\n".join(
        f"{s.supplier_id} | {s.registered_name} | {s.trading_name}" for s in suppliers
    )
