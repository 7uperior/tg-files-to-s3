from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

from ..core.database import get_session
from ..core.models import User, Transaction

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/balance/{user_id}")
def get_balance(user_id: int, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Calculate balance by summing all 'top-up' transactions and subtracting 'reduction' transactions
    transactions = db.exec(select(Transaction).where(Transaction.user_id == user_id)).all()
    balance = sum(t.amount for t in transactions if t.transaction_type == 'top-up') + \
              sum(t.amount for t in transactions if t.transaction_type == 'reduction')

    return {"user_id": user_id, "balance": balance}
