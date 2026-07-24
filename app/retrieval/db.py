# app/retrieval/db.py
import chromadb

CHROMA_PATH = "../knowledge_base/clinical_agentic_db"

client = chromadb.PersistentClient(path=CHROMA_PATH)
memory_db = client.get_or_create_collection(
    name="clinical_memory",
    metadata={"hnsw:space": "cosine"}
)

