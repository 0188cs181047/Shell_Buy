from sqlmodel import Session, select
from typing import Optional, List
from datetime import datetime

from app.model.payment import Transaction, TransactionStatus, TransactionType

def get_transactions_service(
    session: Session,
    user_id: str,

    offset: int = 0,
    limit: int = 100,

    status: Optional[TransactionStatus] = None,
    transaction_type: Optional[TransactionType] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,

    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,

    search: Optional[str] = None
) -> List[Transaction]:

    statement = select(Transaction).where(
        (Transaction.sender_id == user_id) |
        (Transaction.receiver_id == user_id)
    )

    # Filters
    if status:
        statement = statement.where(Transaction.status == status)

    if transaction_type:
        statement = statement.where(Transaction.transaction_type == transaction_type)

    if min_amount is not None:
        statement = statement.where(Transaction.amount >= min_amount)

    if max_amount is not None:
        statement = statement.where(Transaction.amount <= max_amount)

    if start_date:
        statement = statement.where(Transaction.created_at >= start_date)

    if end_date:
        statement = statement.where(Transaction.created_at <= end_date)

    # Search
    if search:
        statement = statement.where(
            (Transaction.order_id.contains(search)) |
            (Transaction.payment_id.contains(search))
        )

    # Pagination
    statement = statement.offset(offset).limit(limit)

    return session.exec(statement).all()