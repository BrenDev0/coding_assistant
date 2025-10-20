from typing_extensions import TypedDict
from src.workflow.domain.models import OrchestratorOutput
from  uuid import UUID
from typing import Dict, List, Any

class State(TypedDict):
    company_id: UUID
    chat_history: List[Dict[str, Any]]
    input: str
    final_response: str
    chat_id: UUID
    orchestrator_response: OrchestratorOutput
