import os
import json
import chromadb
from chromadb.config import Settings

CHROMA_DIR = os.path.join(os.path.dirname(__file__), ".chromadb")
COLLECTION_NAME = "medical_knowledge"


def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def ingest_training_data(json_path):
    """Ingest training data from JSON into vector store."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    records = data if isinstance(data, list) else data.get('records', [])

    collection = get_collection()
    existing = collection.count()

    if existing >= len(records):
        print(f"Vector store already has {existing} records, skipping ingest")
        return existing

    batch_size = 500
    total = 0
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        ids, documents, metadatas = [], [], []
        for j, rec in enumerate(batch):
            doc_id = f"rec_{i + j}"
            text = (
                f"Disease: {rec.get('Disease', '')}. "
                f"Symptoms: {rec.get('Symptoms', '')}. "
                f"Causes: {rec.get('Causes', '')}. "
                f"Medicine: {rec.get('Medicine', '')}. "
                f"Patient age: {rec.get('Age', '')}, gender: {rec.get('Gender', '')}."
            )
            metadata = {
                "disease": str(rec.get('Disease', '')),
                "symptoms": str(rec.get('Symptoms', '')),
                "medicine": str(rec.get('Medicine', '')),
            }
            ids.append(doc_id)
            documents.append(text)
            metadatas.append(metadata)
        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        total += len(batch)

    print(f"Ingested {total} records into vector store")
    return total


def query_relevant_docs(query_text, n_results=5):
    """Query vector store for relevant medical knowledge."""
    collection = get_collection()
    results = collection.query(
        query_texts=[query_text],
        n_results=min(n_results, collection.count() or 1)
    )
    docs = []
    if results and results['documents']:
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            docs.append({
                "text": doc,
                "metadata": meta,
                "distance": dist
            })
    return docs


def build_rag_context(query_text, n_results=5):
    """Build context string from vector store for LLM prompt."""
    docs = query_relevant_docs(query_text, n_results)
    if not docs:
        return ""

    context_parts = []
    for i, doc in enumerate(docs, 1):
        meta = doc["metadata"]
        context_parts.append(
            f"[{i}] Disease: {meta.get('disease', 'N/A')} | "
            f"Symptoms: {meta.get('symptoms', 'N/A')} | "
            f"Medicine: {meta.get('medicine', 'N/A')}"
        )
    return "\n".join(context_parts)
