from app.services.vector_db import store_data, store_document
import uuid

def extract_text(file_path, file_type):
    text = ""

    if file_type == "txt":
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

    elif file_type == "pdf":
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""

    elif file_type == "docx":
        import docx
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    return text

def store_in_vector_db(doc_id, text, category):
    # Chunk text (very important)
    chunk_size = 500
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    for chunk in chunks:
        store_data(
            id=str(uuid.uuid4()),
            text=chunk,
            metadata={
                "doc_id": str(doc_id),
                "type": category
            }
        )


def store_knowledge_vector(doc_id: str, text: str, category: str, user_id: str, title: str):
    store_document(
        doc_id=doc_id,
        text=text,
        metadata={
            "type": category,
            "user_id": user_id,
            "title": title
        }
    )