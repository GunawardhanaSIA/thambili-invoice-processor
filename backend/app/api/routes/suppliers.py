from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.supplier import Supplier as SupplierModel
from app.schemas.supplier import Supplier

router = APIRouter(tags=["suppliers"])


@router.get("/suppliers", response_model=list[Supplier])
def list_suppliers(db: Session = Depends(get_db)) -> list[SupplierModel]:
    return db.query(SupplierModel).all()
