"""Seed suppliers/existing_records from the local sample dataset, if present.

backend/data/*.csv is local-only (gitignored) - see backend/data/README.md.
Seeding is a no-op when a table already has rows, or when the CSV isn't
present locally, so this stays safe to call on every startup.
"""

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.existing_record import ExistingRecord
from app.models.supplier import Supplier

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def seed_suppliers(db: Session) -> None:
    if db.query(Supplier).first() is not None:
        return

    csv_path = DATA_DIR / "suppliers.csv"
    if not csv_path.exists():
        return

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            db.add(
                Supplier(
                    supplier_id=row["supplier_id"],
                    registered_name=row["registered_name"],
                    trading_name=row["trading_name"],
                    category=row["category"],
                    address=row["address"],
                    city=row["city"],
                    phone=row["phone"],
                    email=row["email"],
                    vat_number=row["vat_number"],
                    payment_terms=row["payment_terms"],
                    currency=row["currency"],
                )
            )
    db.commit()


def seed_existing_records(db: Session) -> None:
    if db.query(ExistingRecord).first() is not None:
        return

    csv_path = DATA_DIR / "existing_records.csv"
    if not csv_path.exists():
        return

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            db.add(
                ExistingRecord(
                    record_id=row["record_id"],
                    supplier_id=row["supplier_id"],
                    supplier_name=row["supplier_name"],
                    invoice_number=row["invoice_number"],
                    date_entered=row["date_entered"],
                    net_amount=float(row["net_amount"]),
                    tax_amount=float(row["tax_amount"]),
                    gross_amount=float(row["gross_amount"]),
                    status=row["status"],
                    entered_by=row["entered_by"],
                    currency=row["currency"],
                    cost_centre=row["cost_centre"],
                )
            )
    db.commit()
