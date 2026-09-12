from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.extracted_document import ExtractedDocument
from app.schemas.extracted_document import ExtractedDocumentOut
from app.services.pdf_extraction import extract_pdf_text

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
