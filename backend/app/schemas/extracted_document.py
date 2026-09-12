from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExtractedDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_path: str
    pdf_type: str
    page_count: int
    extracted_text: str
    created_at: datetime
