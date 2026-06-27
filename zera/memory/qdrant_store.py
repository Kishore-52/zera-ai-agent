import os
import uuid
import json
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from zera.schemas import RetrievedMemory

_client_instance = None

class QdrantStore:
    def __init__(self):
        global _client_instance
        # Local Qdrant mode
        self.path = os.path.join(os.path.dirname(__file__), '..', '..', 'storage', 'qdrant')
        os.makedirs(self.path, exist_ok=True)
        
        url = os.environ.get("QDRANT_URL")
        api_key = os.environ.get("QDRANT_API_KEY")
        self.collection_name = os.environ.get("QDRANT_COLLECTION", "zera_safety_memory")
        
        if url and api_key:
            self.client = QdrantClient(url=url, api_key=api_key)
            self.mode = "Cloud"
        else:
            if "PYTEST_CURRENT_TEST" in os.environ:
                self.client = QdrantClient(location=":memory:")
                self.mode = "Test Memory"
            else:
                if _client_instance is None:
                    _client_instance = QdrantClient(path=self.path)
                self.client = _client_instance
                self.mode = "Local"
            
        self._ensure_collection()

    def _ensure_collection(self):
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def _get_mock_vector(self, text: str):
        # A deterministic fake vector for local demo mode
        if "rebound" in text.lower():
            return [1.0] * 384
        val = sum(ord(c) for c in text) / 10000.0
        return [val] * 384

    def add_documents(self, documents: list[dict]):
        points = []
        for doc in documents:
            point_id = str(uuid.uuid4())
            vector = self._get_mock_vector(doc.get("content", ""))
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=doc
                )
            )
        if points:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

    def search(self, query: str, limit: int = 3) -> list[RetrievedMemory]:
        try:
            vector = self._get_mock_vector(query)
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                limit=limit
            )
            
            memories = []
            for res in response.points:
                payload = res.payload or {}
                memories.append(RetrievedMemory(
                    source_id=payload.get("source_id", "unknown"),
                    title=payload.get("title", "Untitled"),
                    content=payload.get("content", ""),
                    similarity_score=float(res.score)
                ))
            return memories
        except Exception as e:
            print(f"Qdrant search error: {e}")
            return []
            
    def get_info(self):
        try:
            count = self.client.count(self.collection_name).count
            return {
                "mode": self.mode,
                "collection": self.collection_name,
                "count": count
            }
        except Exception:
            return {
                "mode": self.mode,
                "collection": self.collection_name,
                "count": 0
            }
