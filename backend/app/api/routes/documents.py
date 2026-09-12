import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.extracted_document import ExtractedDocument
from app.models.parsed_invoice import ParsedInvoice
from app.schemas.extracted_document import ExtractedDocumentOut
from app.schemas.parsed_invoice import ParsedInvoiceOut
from app.services.invoice_parser import parse_invoice_fields
from app.services.pdf_extraction import extract_pdf_text

router = APIRouter(tags=["documents"])

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/documents/extract", response_model=ExtractedDocumentOut)
async def extract_document(
    file: UploadFile, db: Session = Depends(get_db)
) -> ExtractedDocument:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    original_name = file.filename or "unknown.pdf"
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    stored_path = UPLOAD_DIR / stored_name
    stored_path.write_bytes(pdf_bytes)

    result = extract_pdf_text(pdf_bytes, ocr_dpi=settings.ocr_dpi)

    document = ExtractedDocument(
        filename=original_name,
        file_path=str(stored_path),
        pdf_type=result.pdf_type,
        page_count=result.page_count,
        extracted_text=result.text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    fields = parse_invoice_fields(result.text)
    parsed_invoice = ParsedInvoice(document_id=document.id, **fields.__dict__)
    db.add(parsed_invoice)
    db.commit()

    return document


@router.get("/documents", response_model=list[ExtractedDocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[ExtractedDocument]:
    return db.query(ExtractedDocument).order_by(ExtractedDocument.created_at.desc()).all()


@router.get("/documents/parsed-invoices", response_model=list[ParsedInvoiceOut])
def list_parsed_invoices(db: Session = Depends(get_db)) -> list[ParsedInvoice]:
    return db.query(ParsedInvoice).all()


@router.get("/documents/{document_id}", response_model=ExtractedDocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)) -> ExtractedDocument:
    document = db.get(ExtractedDocument, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/documents/{document_id}/parsed-invoice", response_model=ParsedInvoiceOut)
def get_parsed_invoice(document_id: str, db: Session = Depends(get_db)) -> ParsedInvoice:
    parsed_invoice = (
        db.query(ParsedInvoice).filter(ParsedInvoice.document_id == document_id).first()
    )
    if parsed_invoice is None:
        raise HTTPException(status_code=404, detail="Parsed invoice not found")
    return parsed_invoice
