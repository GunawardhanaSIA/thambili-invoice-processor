from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, invoices, records, suppliers
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.models import (  # noqa: F401 (registers the tables)
    existing_record,
    extracted_document,
    invoice,
    invoice_extraction,
    supplier,
)
from app.services.seed_data import seed_existing_records, seed_suppliers

Base.metadata.create_all(bind=engine)

_seed_db = SessionLocal()
try:
    seed_suppliers(_seed_db)
    seed_existing_records(_seed_db)
finally:
    _seed_db.close()

app = FastAPI(title="Thambili Invoice Processor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(invoices.router, prefix=settings.api_prefix)
app.include_router(suppliers.router, prefix=settings.api_prefix)
app.include_router(records.router, prefix=settings.api_prefix)
