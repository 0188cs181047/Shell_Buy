from sqlmodel import SQLModel
from typing import Optional
from app.model.payment import TransactionStatus, TransactionType

class TransactionCreate(SQLModel):
    product_id: str
    amount: float
    currency: Optional[str] = "INR"
    description: Optional[str] = None

class CreateOrderResponse(SQLModel):
    transaction_id: str
    order_id: str
    amount: float
    currency: str

class VerifyPaymentRequest(SQLModel):
    transaction_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class TransactionResponse(SQLModel):
    id: str
    sender_id: str
    receiver_id: str
    product_id: Optional[str]

    amount: float
    currency: str

    status: TransactionStatus
    transaction_type: TransactionType

    order_id: Optional[str]
    payment_id: Optional[str]

    description: Optional[str]

class VerifyPaymentRequest(SQLModel):
    transaction_id: str
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str