from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.document_model import Document

from app.auth.rbac import role_required

from app.rag.chunker import chunk_text
from app.rag.embedding import create_embeddings
from app.rag.reranker import rerank_results
from app.rag.vector_db import (
    store_embeddings,
    search_embeddings,
    remove_document_embeddings,
    get_document_context
)


router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post("/index-document/{document_id}")
def index_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        role_required(["admin", "analyst"])
    )
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if not document.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="Document has no extracted text to index"
        )

    chunks = chunk_text(
        document.extracted_text
    )

    embeddings = create_embeddings(
        chunks
    )

    store_embeddings(
        chunks,
        embeddings,
        document_id
    )

    return {
        "message": "Document indexed successfully",
        "document_id": document_id,
        "chunks": len(chunks)
    }


@router.delete("/remove-document/{document_id}")
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        role_required(["admin"])
    )
):

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    deleted_count = remove_document_embeddings(document_id)

    if deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="No embeddings found for this document. Was it indexed?"
        )

    return {
        "message": "Document embeddings removed successfully",
        "document_id": document_id,
        "chunks_deleted": deleted_count
    }


@router.post("/search")
def semantic_search(
    query: str,
    current_user=Depends(
        role_required(["admin", "analyst", "client", "auditor"])
    )
):
    """
    Full RAG retrieval pipeline:
    Query → Embed → Vector Search (top 20) → Rerank → Top 5 results
    """

    query_embedding = create_embeddings([query])[0]
    raw_results = search_embeddings(
        query_embedding,
        n_results=20
    )

    documents = raw_results.get("documents", [[]])[0]

    if not documents:
        return {
            "query": query,
            "results": [],
            "message": "No documents indexed yet"
        }
    reranked = rerank_results(
        query=query,
        documents=documents,
        top_k=5
    )

    return {
        "query": query,
        "results": reranked
    }


@router.get("/context/{document_id}")
def get_context(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        role_required(["admin", "analyst", "auditor", "client"])
    )
):
    """
    Retrieve all stored chunks/context for a specific document.
    """

    document = db.query(Document).filter(
        Document.id == document_id
    ).first()

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    context = get_document_context(document_id)

    chunks = context.get("documents", [])

    if not chunks:
        raise HTTPException(
            status_code=404,
            detail="No indexed context found for this document. Index it first."
        )

    return {
        "document_id": document_id,
        "title": document.title,
        "company_name": document.company_name,
        "total_chunks": len(chunks),
        "chunks": chunks
    }
