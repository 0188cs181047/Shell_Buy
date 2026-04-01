import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()
collection = client.get_or_create_collection(name="ai_knowledge")

model = SentenceTransformer("all-MiniLM-L6-v2")
import uuid


def get_embedding(text: str):
    return model.encode(text).tolist()


def store_data(id: str, text: str, metadata: dict):
    embedding = get_embedding(text)

    collection.add(
        ids=[id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[metadata]
    )


def search_data(query: str, top_k: int = 3, filters: dict = None):
    embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where=filters
    )

    return {
        "documents": results.get("documents", []),
        "metadatas": results.get("metadatas", [])
    }

def store_document(doc_id: str, text: str, metadata: dict):
    chunk_size = 500
    overlap = 100

    start = 0
    while start < len(text):
        chunk = text[start:start + chunk_size]

        store_data(
            id=str(uuid.uuid4()),
            text=chunk,
            metadata={
                **metadata,
                "doc_id": doc_id
            }
        )

        start += (chunk_size - overlap)