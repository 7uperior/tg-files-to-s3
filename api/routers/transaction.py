from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..core.database import get_session
from ..core.models import Transaction, User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/transactions/top-up")
def top_up_transaction(user_id: int, amount: float, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    transaction = Transaction(user_id=user_id, amount=amount, transaction_type="top-up")
    db.add(transaction)
    db.commit()
    return {"message": "Balance topped up successfully", "transaction_id": transaction.id}

@router.post("/transactions/reduction")
def reduction_transaction(user_id: int, amount: float, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Sum up the top-up and reduction transactions to calculate the balance
    total_top_up = sum(t.amount for t in db.exec(select(Transaction).where(Transaction.user_id == user_id, Transaction.transaction_type == "top-up")))
    total_reduction = sum(t.amount for t in db.exec(select(Transaction).where(Transaction.user_id == user_id, Transaction.transaction_type == "reduction")))

    if total_top_up - total_reduction < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance for reduction")

    transaction = Transaction(user_id=user_id, amount=-amount, transaction_type="reduction")  # Note the negative amount
    db.add(transaction)
    db.commit()
    return {"message": "Balance reduced successfully", "transaction_id": transaction.id}

@router.post("/transactions/top-up-tg-bot")
def top_up_transaction_tg_bot(telegram_id: str, amount: float, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    transaction = Transaction(user_id=user.id, amount=amount, transaction_type="top-up")
    db.add(transaction)
    db.commit()
    return {"message": "Balance topped up successfully via Telegram", "transaction_id": transaction.id}

@router.post("/transactions/reduction-tg-bot")
def reduction_transaction_tg_bot(telegram_id: str, amount: float, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.telegram_id == telegram_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # Calculate the balance considering top-ups and reductions
    total_top_up = sum(t.amount for t in db.exec(select(Transaction).where(Transaction.user_id == user.id, Transaction.transaction_type == "top-up")))
    total_reduction = sum(t.amount for t in db.exec(select(Transaction).where(Transaction.user_id == user.id, Transaction.transaction_type == "reduction")))

    if total_top_up - total_reduction < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance for reduction")

    transaction = Transaction(user_id=user.id, amount=-amount, transaction_type="reduction")
    db.add(transaction)
    db.commit()
    return {"message": "Balance reduced successfully via Telegram", "transaction_id": transaction.id}
