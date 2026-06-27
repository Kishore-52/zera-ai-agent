import time
from datetime import datetime
from zera.agents.base_agent import BaseAgent
from zera.schemas import AgentTrace, AgentExecutionStatus, RetrievedMemory, MaintenanceRequest
from zera.memory.qdrant_store import QdrantStore

class MemoryAgent(BaseAgent):
    def __init__(self):
        super().__init__("Safety Memory Agent", 2)
        self.store = QdrantStore()

    def execute(self, request: MaintenanceRequest, **kwargs) -> tuple[list[RetrievedMemory], AgentTrace]:
        start = time.time()
        start_dt = datetime.now().isoformat()
        
        query = f"{request.machine} {request.component} {request.maintenance_task} safety"
        memories = self.store.search(query, limit=5)

        out_summary = f"Retrieved {len(memories)} relevant documents from Qdrant."
        if self.is_local:
            out_summary += " (Local deterministic search)"

        trace = AgentTrace(
            order=self.order,
            agent=self.name,
            status=AgentExecutionStatus.SUCCESS,
            input_summary=f"Search query: {query}",
            output_summary=out_summary,
            tools_used=["Qdrant Semantic Search"],
            start_time=start_dt,
            completion_time=datetime.now().isoformat(),
            duration=time.time() - start
        )
        return memories, trace
