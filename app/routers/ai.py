from app.database import get_session
from app.model.user import User
from app.core.security import get_current_user
from fastapi import APIRouter, Depends, Request, status
from dotenv import load_dotenv
from sqlmodel import Session
from app.model.ai import AIQueryHistory
from app.services.ai import get_user_transactions, process_transactions, calculate_summary, get_user_details, ask_ai

load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/ai-transaction-query", status_code=status.HTTP_200_OK)
async def ai_query(
    request: Request,
    user_query: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    # User data
    user_data = get_user_details(current_user)

    # Transactions
    transactions = get_user_transactions(session, user_id)

    processed = process_transactions(transactions, user_id)

    summary = calculate_summary(processed)

    # AI Response
    ai_response = ask_ai(user_query, user_data, processed[:50], summary)

    # Save history
    history = AIQueryHistory(
        user_id=user_id,
        query=user_query,
        response=ai_response
    )
    session.add(history)
    session.commit()

    return {"data": ai_response}