from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from typing import List
from typing import List, Optional
import hmac
import hashlib
from app.database import get_session
from app.model.payment import Transaction
from app.model.user import User
from app.core.security import get_current_user
from datetime import datetime
from app.services.transaction import get_transactions_service
from app.schema.payment import TransactionResponse, CreateOrderResponse, TransactionCreate, TransactionStatus, TransactionType, VerifyPaymentRequest
from app.model.product import Product
import razorpay
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/transactions", tags=["Transactions"])

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@router.post("/create", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    data: TransactionCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        # Validate product exists (optional but recommended)
        product = session.exec(
            select(Product).where(Product.id == data.product_id)
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Create transaction (PENDING)
        transaction = Transaction(
            sender_id=current_user.id,
            receiver_id=product.user_id,
            product_id=data.product_id,
            amount=data.amount,
            currency=data.currency,
            status="pending",
            description=data.description
        )

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        # Create Razorpay Order
        order = razorpay_client.order.create({
            "amount": int(data.amount * 100),  # convert to paisa
            "currency": data.currency,
            "payment_capture": 1
        })

        # Save order_id in DB
        transaction.order_id = order["id"]
        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        #  Response
        return CreateOrderResponse(
            transaction_id=transaction.id,
            order_id=order["id"],
            amount=data.amount,
            currency=data.currency
        )

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
def get_all_transactions(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),

    offset: int = 0,
    limit: int = 100,

    status: Optional[TransactionStatus] = None,
    transaction_type: Optional[TransactionType] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,

    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),

    search: Optional[str] = None
):
    try:
        transactions = get_transactions_service(
            session=session,
            user_id=current_user.id,
            offset=offset,
            limit=limit,
            status=status,
            transaction_type=transaction_type,
            min_amount=min_amount,
            max_amount=max_amount,
            start_date=start_date,
            end_date=end_date,
            search=search
        )

        return transactions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
def get_transaction(
    transaction_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = session.get(Transaction, transaction_id)

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Authorization check
        if (
            transaction.sender_id != current_user.id and
            transaction.receiver_id != current_user.id
        ):
            raise HTTPException(status_code=403, detail="Not authorized")

        return transaction

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error") 
    

@router.delete("/{transaction_id}", status_code=status.HTTP_200_OK)
def delete_transaction(
    transaction_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = session.get(Transaction, transaction_id)

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Only sender can delete (you can change logic)
        if transaction.sender_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        session.delete(transaction)
        session.commit()

        return {
            "message": "Transaction deleted successfully",
            "transaction_id": transaction_id
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/verify", status_code=status.HTTP_200_OK)
def verify_payment(
    data: VerifyPaymentRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        # Get transaction
        transaction = session.exec(
            select(Transaction).where(Transaction.id == data.transaction_id)
        ).first()

        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Security check (optional but recommended)
        if transaction.sender_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        # Verify signature
        generated_signature = hmac.new(
            bytes(RAZORPAY_KEY_SECRET, "utf-8"),
            bytes(f"{data.razorpay_order_id}|{data.razorpay_payment_id}", "utf-8"),
            hashlib.sha256
        ).hexdigest()

        if generated_signature == data.razorpay_signature:
            # Payment success
            transaction.status = TransactionStatus.SUCCESS
            transaction.payment_id = data.razorpay_payment_id
            transaction.signature = data.razorpay_signature

        else:
            # Payment failed
            transaction.status = TransactionStatus.FAILED

        session.add(transaction)
        session.commit()
        session.refresh(transaction)

        return {
            "message": "Payment verified",
            "status": transaction.status,
            "transaction_id": transaction.id
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))