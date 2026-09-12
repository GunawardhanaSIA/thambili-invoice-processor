from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.ai_module import extract_invoice_from_text
from app.core.config import settings
from app.core.database import get_db
from app.models.extracted_document import ExtractedDocument
from app.models.invoice import Invoice
from app.models.invoice_extraction import InvoiceExtraction
from app.schemas.extracted_document import ExtractedDocumentOut
from app.schemas.invoice_extraction import InvoiceExtractionOut
from app.services.pdf_extraction import extract_pdf_text
from app.services.supplier_lookup import format_known_suppliers

router = APIRouter(tags=["documents"])


@router.post("/documents/extract", response_model=ExtractedDocumentOut)
async def extract_document(
    file: UploadFile, db: Session = Depends(get_db)
) -> ExtractedDocument:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    result = extract_pdf_text(pdf_bytes, ocr_dpi=settings.ocr_dpi)

    document = ExtractedDocument(
        filename=file.filename or "unknown.pdf",
        pdf_type=result.pdf_type,
        page_count=result.page_count,
        extracted_text=result.text,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


@router.get("/documents", response_model=list[ExtractedDocumentOut])
def list_documents(db: Session = Depends(get_db)) -> list[ExtractedDocument]:
    return db.query(ExtractedDocument).order_by(ExtractedDocument.created_at.desc()).all()


@router.get("/documents/{document_id}", response_model=ExtractedDocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)) -> ExtractedDocument:
    document = db.get(ExtractedDocument, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.post("/documents/{document_id}/extract-invoice", response_model=InvoiceExtractionOut)
def extract_invoice_fields(document_id: str, db: Session = Depends(get_db)) -> InvoiceExtraction:
    """Run the extracted document's raw text through the Claude-powered ai_module
    to pull out structured invoice fields (supplier, amounts, dates, confidence),
    and persist the result."""
    document = db.get(ExtractedDocument, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    known_suppliers = format_known_suppliers(db)
    result = extract_invoice_from_text(document.extracted_text, known_suppliers=known_suppliers)

    extraction = InvoiceExtraction(
        document_id=document.id,
        success=result.success,
        fields=result.fields.model_dump(mode="json"),
        overall_confidence=result.overall_confidence,
        confidence_level=result.confidence_level,
        requires_review=result.requires_review,
        warnings=[w.model_dump(mode="json") for w in result.warnings],
        error=result.error,
    )
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    if result.success:
        fields = result.fields
        invoice = Invoice(
            document_id=document.id,
            extraction_id=extraction.id,
            supplier_id=fields.supplier_id.value or "",
            supplier_name=fields.supplier_name.value or "",
            invoice_number=fields.invoice_number.value or "",
            net_amount=fields.subtotal.value or 0.0,
            tax_amount=fields.tax_amount.value or 0.0,
            gross_amount=fields.total_amount.value or 0.0,
            currency=fields.currency.value or "",
            status="Needs Attention" if result.requires_review else "Pending Review",
            issue=result.warnings[0].message if result.warnings else "",
        )
        db.add(invoice)
        db.commit()

    return extraction


@router.get("/documents/{document_id}/invoice-extraction", response_model=InvoiceExtractionOut)
def get_invoice_extraction(document_id: str, db: Session = Depends(get_db)) -> InvoiceExtraction:
    """Return the most recent stored AI extraction for a document, without
    re-calling Claude."""
    extraction = (
        db.query(InvoiceExtraction)
        .filter(InvoiceExtraction.document_id == document_id)
        .order_by(InvoiceExtraction.created_at.desc())
        .first()
    )
    if extraction is None:
        raise HTTPException(status_code=404, detail="No invoice extraction found for this document")
    return extraction
