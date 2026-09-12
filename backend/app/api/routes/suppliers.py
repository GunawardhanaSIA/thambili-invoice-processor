from fastapi import APIRouter

from app.schemas.supplier import Supplier

router = APIRouter(tags=["suppliers"])


@router.get("/suppliers", response_model=list[Supplier])
def list_suppliers() -> list[Supplier]:
    return []
