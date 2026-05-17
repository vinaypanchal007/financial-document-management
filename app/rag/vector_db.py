import chromadb

_client = None
_collection = None


def _get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path="chroma_db")
        _collection = _client.get_or_create_collection(name="financial_documents")
    return _collection


def store_embeddings(
    chunks,
    embeddings,
    document_id
):

    collection = _get_collection()

    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        ids.append(f"{document_id}_{i}")

        metadatas.append({
            "document_id": str(document_id),
            "chunk": chunk
        })

    collection.add(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadatas
    )


def search_embeddings(
    query_embedding,
    n_results=20
):

    collection = _get_collection()

    total = collection.count()

    if total == 0:
        return {
            "ids": [],
            "documents": [],
            "metadatas": [],
            "distances": []
        }

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=min(n_results, total)
    )

    return results


def remove_document_embeddings(document_id: int):

    collection = _get_collection()

    results = collection.get(
        where={"document_id": str(document_id)}
    )

    ids_to_delete = results.get("ids", [])

    if not ids_to_delete:
        return 0

    collection.delete(ids=ids_to_delete)

    return len(ids_to_delete)


def get_document_context(document_id: int):

    collection = _get_collection()

    results = collection.get(
        where={"document_id": str(document_id)},
        include=["documents", "metadatas", "embeddings"]
    )

    return results
