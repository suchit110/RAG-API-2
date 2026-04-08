from fastapi import APIRouter
import numpy as np
import database
from document_service import model

router = APIRouter()


# ── 1. Index a document ──────────────────────────────────────────────────────
# Split document into small chunks, turn each chunk into an embedding, save in FAISS
# You must call this after uploading a document

@router.post("/rag/index-document")
def index_document(doc_id: int):

    # Find the document
    for doc in database.documents:
        if doc["id"] == doc_id:

            # Split document info into small chunks (simple chunking)
            chunks = [
                f"{doc['title']} is a {doc['document_type']} document.",
                f"This document belongs to {doc['company_name']}.",
                f"It was uploaded by {doc['uploaded_by']} on {doc['created_at']}.",
            ]

            # Turn each chunk into an embedding and save in FAISS
            for chunk in chunks:
                embedding = model.encode(chunk)                        # text → numbers
                embedding = np.array([embedding]).astype("float32")    # format for FAISS
                database.index.add(embedding)                          # save in FAISS
                database.doc_mapping.append({"doc": doc, "chunk": chunk})  # remember which doc

            return {"message": f"document {doc_id} indexed", "chunks_stored": len(chunks)}

    return {"message": "document not found"}


# ── 2. Remove document embeddings ────────────────────────────────────────────
# Removes the document chunks from doc_mapping
# Note: FAISS does not support deletion, so we just remove from our tracking list

@router.delete("/rag/remove-document/{doc_id}")
def remove_document(doc_id: int):
    before = len(database.doc_mapping)
    database.doc_mapping = [entry for entry in database.doc_mapping if entry["doc"]["id"] != doc_id]
    removed = before - len(database.doc_mapping)
    return {"message": f"removed {removed} chunks for document {doc_id}"}


# ── 3. Semantic search with reranking ────────────────────────────────────────
# Step 1: Turn query into embedding
# Step 2: Search FAISS for top 20 similar chunks
# Step 3: Rerank by relevance score (lower FAISS distance = more relevant)
# Step 4: Return top 5

@router.post("/rag/search")
def rag_search(query: str):

    if len(database.doc_mapping) == 0:
        return {"message": "no documents indexed yet"}

    # Step 1 - turn query into embedding
    query_vector = model.encode(query)
    query_vector = np.array([query_vector]).astype("float32")

    # Step 2 - search FAISS for top 20
    k = min(20, len(database.doc_mapping))
    D, I = database.index.search(query_vector, k=k)

    # Step 3 - rerank: convert distance to a score (higher score = more relevant)
    results = []
    for dist, idx in zip(D[0], I[0]):
        if idx < len(database.doc_mapping):
            entry = database.doc_mapping[idx]
            score = round(1 / (1 + float(dist)), 4)   # simple rerank formula
            results.append({
                "document": entry["doc"],
                "chunk": entry["chunk"],
                "relevance_score": score
            })

    # Step 4 - sort by score, return top 5
    results = sorted(results, key=lambda x: x["relevance_score"], reverse=True)[:5]
    return {"query": query, "results": results}


# ── 4. Get all indexed chunks for a document ─────────────────────────────────

@router.get("/rag/context/{doc_id}")
def rag_context(doc_id: int):
    chunks = [entry for entry in database.doc_mapping if entry["doc"]["id"] == doc_id]
    if not chunks:
        return {"message": "no indexed content found for this document"}
    return {"document_id": doc_id, "chunks": chunks}
