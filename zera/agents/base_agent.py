import os
from zera.schemas import AgentTrace, AgentExecutionStatus
from typing import Any, Tuple

class BaseAgent:
    def __init__(self, name: str, order: int):
        self.name = name
        self.order = order
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        self.is_local = not bool(self.api_key)

    def execute(self, inputs: Any, **kwargs) -> Tuple[Any, AgentTrace]:
        raise NotImplementedError
