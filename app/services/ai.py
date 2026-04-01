from app.model.payment import Transaction
from groq import Groq
from dotenv import load_dotenv
import os
from app.services.vector_db import search_data, store_data
import uuid

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

def build_vector_query(user_query, user_data):
    return user_query.strip()

def build_ai_prompt(user_query, user_data, transactions, summary, context):
    return f"""
    You are a smart financial assistant AI.

    🔹 Context (Policies / Memory / Knowledge):
    {context}

    🔹 User Question:
    {user_query}

    🔹 User Details:
    {user_data}

    🔹 Transactions:
    {transactions}

    🔹 Summary:
    {summary}

    Instructions:
    - Use context if relevant
    - Follow business rules strictly
    - Be accurate and concise
    - Return JSON only

    Format:
    {{
        "answer": "...",
        "type": "profile | transaction | policy | mixed",
        "graph": {{
            "labels": [...],
            "values": [...]
        }}
    }}
    """

import uuid

def ask_ai(user_query, user_data, transactions, summary):

    # Step 1: Clean query
    vector_query = build_vector_query(user_query, user_data)

    # Step 2: Search vector DB with filters
    results = search_data(
        vector_query,
        top_k=5,
        filters={
            "$or": [
                {"type": "policy"},
                {"user_id": str(user_data["id"])}
            ]
        }
    )

    # Step 3: Extract context properly
    context = ""
    documents = results.get("documents", [])

    if documents:
        for doc_list in documents:
            if isinstance(doc_list, list):
                context += "\n".join(doc_list) + "\n"


    # Step 4: Build prompt
    prompt = build_ai_prompt(
        user_query,
        user_data,
        transactions,
        summary,
        context
    )

    # Step 5: Call AI
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )

    ai_response = response.choices[0].message.content

    # Step 6: Store history in vector DB
    store_data(
        id=str(uuid.uuid4()),
        text=f"Q: {user_query} A: {ai_response}",
        metadata={
            "type": "history",
            "user_id": str(user_data["id"])
        }
    )

    return ai_response