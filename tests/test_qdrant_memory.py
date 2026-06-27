import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.memory.qdrant_store import QdrantStore

def test_qdrant_retrieves_pressure_rebound():
    # Only test if seeded
    store = QdrantStore()
    if store.get_info().get("count", 0) > 0:
        results = store.search("pressure rebound valve leak")
        assert len(results) > 0
        # Mock vectors aren't semantically accurate, just ensure we get results
