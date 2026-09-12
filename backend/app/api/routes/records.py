from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.record import ExistingRecord as ExistingRecordModel
from app.schemas.record import ExistingRecord

router = APIRouter(tags=["records"])


@router.get("/records", response_model=list[ExistingRecord])
def list_existing_records(db: Session = Depends(get_db)) -> list[ExistingRecordModel]:
    return db.query(ExistingRecordModel).all()
