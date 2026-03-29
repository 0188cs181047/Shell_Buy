from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from enum import Enum
from app.model.base import CommonBaseModel

class TransactionStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"

class TransactionType(str, Enum):
    PAYMENT = "payment"
    REFUND = "refund"

class Transaction(CommonBaseModel, table=True):
    __tablename__ = "transactions"

    sender_id: str = Field(foreign_key="users.id", index= True)
    receiver_id: str = Field(foreign_key="users.id", index=True)

    product_id: Optional[str] = Field(default=None, foreign_key="product.id")

    amount: float

    currency: str = Field(default="INR")

    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    transaction_type: TransactionType = Field(default=TransactionType.PAYMENT)

    # Payment gateway fields (important)
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    signature: Optional[str] = None

    # Optional metadata
    description: Optional[str] = None

    sender: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Transaction.sender_id]"})
    receiver: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "[Transaction.receiver_id]"})