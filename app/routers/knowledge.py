from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlmodel import Session
import uuid
from app.database import get_session
from app.model.user import User
from app.core.security import get_current_user
from app.model.knowledge import KnowledgeBase
from app.services.knowledge import extract_text, store_knowledge_vector
from app.services.file_service import save_file

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.post("/upload")
async def upload_knowledge(
    title: str = Form(...),
    description: str = Form(None),
    category: str = Form("general"),
    content: str = Form(None),
    file: UploadFile = File(None),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    try:
        file_path = None
        file_url = None
        file_ext = None

        extracted_text = content.strip() if content else ""

        # ✅ Use separate function
        if file:
            file_path, file_url, file_ext = save_file(file, "knowledge")

            file_text = extract_text(file_path, file_ext)

            if file_text:
                extracted_text += "\n" + file_text

        # ❌ No content check
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No content provided")

        # 💾 Save DB
        kb = KnowledgeBase(
            title=title,
            description=description,
            file_name=file.filename if file else None,
            file_type=file_ext,
            file_path=file_path,
            content=extracted_text,
            category=category,
            created_by=current_user.id
        )

        session.add(kb)
        session.commit()
        session.refresh(kb)

        # 🧠 Store in vector DB
        store_knowledge_vector(
            doc_id=str(kb.id),
            text=extracted_text,
            category=category,
            user_id=str(current_user.id),
            title=title
        )

        return {
            "message": "Knowledge stored successfully",
            "id": str(kb.id),
            "file_url": file_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))