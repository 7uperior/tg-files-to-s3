from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
import logging

from ..core.database import get_session
from ..core.models import User, Transaction

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)

@router.get("/balance/{telegram_id}")
def get_balance(telegram_id: str, db: Session = Depends(get_session)):
    logger.info(f"Fetching balance for Telegram ID: {telegram_id}")
    user = db.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        logger.error(f"User not found for Telegram ID: {telegram_id}")
        raise HTTPException(status_code=404, detail="User not found")

    transactions = db.exec(select(Transaction).where(Transaction.user_id == user.id)).all()
    balance = sum(t.amount for t in transactions if t.transaction_type == 'top-up') + \
              sum(t.amount for t in transactions if t.transaction_type == 'reduction')
    logger.info(f"Balance for user {user.id}: {balance}")
    return {"user_id": user.id, "balance": balance}
