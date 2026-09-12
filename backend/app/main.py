from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, invoices, records, suppliers
from app.core.config import settings
from app.core.database import Base, engine
from app.models import (  # noqa: F401 (registers the tables)
    extracted_document,
    invoice,
    parsed_invoice,
    record,
    supplier,
)

Base.metadata.create_all(bind=engine)

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
