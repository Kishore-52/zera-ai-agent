import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from zera.memory.qdrant_store import QdrantStore

def seed_qdrant():
    store = QdrantStore()
    
    # Check if we already have data
    if store.get_info().get("count", 0) > 0:
        print(f"Collection {store.collection_name} is already populated.")
        return

    data_dir = os.path.join(os.path.dirname(__file__), '..', 'zera', 'data')
    
    documents = []

    # 1. Incident History
    incidents_path = os.path.join(data_dir, 'incident_history.json')
    if os.path.exists(incidents_path):
        with open(incidents_path, 'r') as f:
            incidents = json.load(f)
            for inc in incidents:
                documents.append({
                    "source_id": inc["incident_id"],
                    "title": f"Incident: {inc['hazard']} Hazard",
                    "content": f"{inc['event_summary']} Cause: {inc['cause']}. Action: {inc['corrective_action']}"
                })

    # 2. Hazard Catalogue
    hazards_path = os.path.join(data_dir, 'hazard_catalogue.json')
    if os.path.exists(hazards_path):
        with open(hazards_path, 'r') as f:
            hazards = json.load(f)
            for haz in hazards:
                documents.append({
                    "source_id": haz["hazard_id"],
                    "title": f"Hazard: {haz['type']}",
                    "content": haz["description"]
                })

    # 3. LOTO Procedure
    loto_path = os.path.join(data_dir, 'loto_procedure.md')
    if os.path.exists(loto_path):
        with open(loto_path, 'r') as f:
            loto_text = f.read()
            documents.append({
                "source_id": "LOTO-HP-01",
                "title": "LOTO Procedure",
                "content": loto_text
            })

    if documents:
        store.add_documents(documents)
        print(f"Successfully seeded {len(documents)} documents to {store.mode} Qdrant.")
    else:
        print("No documents found to seed.")

if __name__ == "__main__":
    seed_qdrant()
