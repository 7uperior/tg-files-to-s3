from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session
import logging


from ..core.database import get_session, get_latest_files_pricing
from ..core.models import FilesPricing, FilesPricingCreate

router = APIRouter(prefix="/settings", tags=["Settings"])

logger = logging.getLogger(__name__)

@router.post("/filespricing/", response_model=FilesPricing, status_code=status.HTTP_201_CREATED)
def create_files_pricing(pricing: FilesPricingCreate, session: Session = Depends(get_session)):
    new_pricing = FilesPricing(**pricing.dict())
    session.add(new_pricing)
    try:
        session.commit()
        session.refresh(new_pricing)
        return new_pricing
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filespricing/latest", response_model=FilesPricing)
def fetch_latest_files_pricing(session: Session = Depends(get_session)):
    latest_pricing = get_latest_files_pricing(session)
    if not latest_pricing:
        raise HTTPException(status_code=404, detail="No files pricing information found.")
    return latest_pricing
