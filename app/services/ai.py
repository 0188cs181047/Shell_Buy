from app.model.payment import Transaction
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

GROB_API_KEY = os.getenv("GROB_API_KEY", "")
client = Groq(api_key=GROB_API_KEY)

def get_user_transactions(db, user_id):
    return db.query(Transaction).filter(
        (Transaction.sender_id == user_id) |
        (Transaction.receiver_id == user_id)
    ).all()

def process_transactions(transactions, user_id):
    data = []

    for t in transactions:
        txn_type = "spent" if t.sender_id == user_id else "received"

        data.append({
            "amount": t.amount,
            "type": txn_type,
            "status": t.status.value,
            "category": t.transaction_type.value,
            "product_id": t.product_id,
            "date": str(t.created_at)
        })

    return data


def calculate_summary(transactions):
    total_spent = 0
    total_received = 0

    category_data = {}

    for t in transactions:
        if t["type"] == "spent":
            total_spent += t["amount"]
        else:
            total_received += t["amount"]

        cat = t["category"]
        category_data[cat] = category_data.get(cat, 0) + t["amount"]

    return {
        "total_spent": total_spent,
        "total_received": total_received,
        "category_data": category_data
    }

def get_user_details(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number
    }

def build_prompt(user_query, user_data, transactions, summary):
    return f"""
            You are a smart financial assistant AI.

            User Question:
            {user_query}

            User Details:
            {user_data}

            Transaction Data:
            {transactions}

            Summary:
            {summary}

            Instructions:
            - If user asks about profile → use User Details
            - If user asks about transactions → use Transaction Data
            - If both → combine answer
            - Be accurate
            - Return JSON only

            Format:
            {{
            "answer": "...",
            "type": "profile | transaction | mixed",
            "graph": {{
                "labels": [...],
                "values": [...]
            }}
            }}
        """

def ask_ai(user_query, user_data, transactions, summary):
    prompt = build_prompt(user_query, user_data, transactions, summary)

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content