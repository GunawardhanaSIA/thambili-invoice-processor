from fastapi import APIRouter

from app.schemas.record import ExistingRecord

router = APIRouter(tags=["records"])


@router.get("/records", response_model=list[ExistingRecord])
def list_existing_records() -> list[ExistingRecord]:
    return []
