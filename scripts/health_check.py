import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.memory.qdrant_store import QdrantStore

def run_health_check():
    print("Running Health Check...")
    print("-----------------------")
    
    # Check Memory
    store = QdrantStore()
    info = store.get_info()
    print(f"[OK] Qdrant Store initialized. Mode: {info['mode']}, Count: {info['count']}")
    
    # Check Environment
    if os.environ.get("GOOGLE_API_KEY"):
        print("[OK] GOOGLE_API_KEY found.")
    else:
        print("[INFO] GOOGLE_API_KEY not found. Operating in local deterministic mode.")
        
    print("\nAll internal services appear to be healthy.")

if __name__ == "__main__":
    run_health_check()
