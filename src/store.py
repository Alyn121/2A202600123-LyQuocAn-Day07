from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    Tries to use ChromaDB if available; falls back to an in-memory store.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = False
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0

        try:
            import chromadb  # noqa: F401

            # Use EphemeralClient for isolated in-memory storage typically used in tests
            self._client = chromadb.EphemeralClient()
            try:
                self._client.delete_collection(name=self._collection_name)
            except Exception:
                pass
            self._collection = self._client.get_or_create_collection(name=self._collection_name)
            self._use_chroma = True
        except Exception:
            self._use_chroma = False
            self._collection = None

    def _make_record(self, doc: Document) -> dict[str, Any]:
        metadata = doc.metadata.copy()
        metadata["doc_id"] = doc.id
        return {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content)
        }

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        query_emb = self._embedding_fn(query)
        scored = []
        for r in records:
            sim = _dot(query_emb, r["embedding"])
            r_copy = r.copy()
            r_copy["score"] = sim
            scored.append((sim, r_copy))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in scored[:top_k]]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: use collection.add(ids=[...], documents=[...], embeddings=[...])
        For in-memory: append dicts to self._store
        """
        if not docs:
            return

        # 1. Batch generate embeddings with conservative rate limiting for Free Tier
        # Free tier limit: 100 instances per minute. We use 20 per batch with 20s sleep.
        import time
        batch_size = 20
        all_embeddings = []
        
        for i in range(0, len(docs), batch_size):
            batch_contents = [doc.content for doc in docs[i:i + batch_size]]
            if i > 0:
                print(f"      (Đang chờ 20 giây để hồi phục API quota... {i}/{len(docs)})")
                time.sleep(20) 
            
            try:
                batch_emb = self._embedding_fn(batch_contents)
                all_embeddings.extend(batch_emb)
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    print("      (!) Hết quota, đang chờ 60 giây để thử lại...")
                    time.sleep(60)
                    batch_emb = self._embedding_fn(batch_contents)
                    all_embeddings.extend(batch_emb)
                else:
                    raise e

        # 2. Prepare records and IDs for ChromaDB
        metadatas = []
        ids = []
        for i, (doc, emb) in enumerate(zip(docs, all_embeddings)):
            full_metadata = {**doc.metadata, "doc_id": doc.id}
            metadatas.append(full_metadata)
            ids.append(f"{doc.id}_{self._next_index + i}")

        self._next_index += len(docs)

        if self._use_chroma and self._collection is not None:
            self._collection.add(
                ids=ids,
                documents=[doc.content for doc in docs],
                embeddings=all_embeddings,
                metadatas=metadatas
            )
        else:
            # Fallback for in-memory store if needed
            for i in range(len(docs)):
                self._store.append({
                    "id": ids[i],
                    "content": docs[i].content,
                    "metadata": metadatas[i],
                    "embedding": all_embeddings[i]
                })

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma and self._collection is not None:
            query_emb = self._embedding_fn(query)
            results = self._collection.query(query_embeddings=[query_emb], n_results=top_k)
            formatted = []
            if results and results.get("ids") and results["ids"]:
                for i in range(len(results["ids"][0])):
                    # Map distance to score. Cosine distance is usually 1 - similarity.
                    # We subtract distance from 1 to get a similarity-like score.
                    dist = results["distances"][0][i] if results.get("distances") else 0.0
                    formatted.append({
                        "id": results["ids"][0][i].rsplit("_", 1)[0], # Strip our unique suffix
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "score": 1.0 - dist 
                    })
            return formatted
        else:
            return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma and self._collection is not None:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if not metadata_filter:
            return self.search(query, top_k)
        
        if self._use_chroma and self._collection is not None:
            query_emb = self._embedding_fn(query)
            results = self._collection.query(
                query_embeddings=[query_emb], 
                n_results=top_k, 
                where=metadata_filter
            )
            formatted = []
            if results and results.get("ids") and results["ids"]:
                for i in range(len(results["ids"][0])):
                    dist = results["distances"][0][i] if results.get("distances") else 0.0
                    formatted.append({
                        "id": results["ids"][0][i].rsplit("_", 1)[0],
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                        "score": 1.0 - dist
                    })
            return formatted
        else:
            filtered = []
            for r in self._store:
                match = all(r.get("metadata", {}).get(k) == v for k, v in metadata_filter.items())
                if match:
                    filtered.append(r)
            return self._search_records(query, filtered, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma and self._collection is not None:
            initial_count = self._collection.count()
            self._collection.delete(where={"doc_id": doc_id})
            return self._collection.count() < initial_count
        else:
            initial_len = len(self._store)
            self._store = [r for r in self._store if r.get("metadata", {}).get("doc_id") != doc_id]
            return len(self._store) < initial_len
