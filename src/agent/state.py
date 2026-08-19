from typing import Any, List, Optional
from pydantic import BaseModel, Field


class IncidentInvestigationState(BaseModel):
    """
    Typed state representation for IncidentIQ LangGraph workflow.
    """
    query: str
    incident_id: Optional[str] = None

    # Structured telemetry gathered via MCP Tools (Supabase PostgreSQL)
    incident_data: Optional[dict] = None
    service_health: Optional[dict] = None
    telemetry_metrics: Optional[List[dict]] = None
    telemetry_logs: Optional[List[dict]] = None
    incident_history: Optional[List[dict]] = None

    # Unstructured operational knowledge retrieved via RAG (Qdrant Cloud)
    retrieved_knowledge: Optional[List[dict]] = None

    # Synthesized investigation findings from Gemini LLM
    root_cause: Optional[str] = None
    evidence_points: Optional[List[str]] = None
    recommended_actions: Optional[List[str]] = None
    confidence_score: Optional[str] = "High"
    raw_synthesis: Optional[str] = None

    # Trace log of agent execution steps
    investigation_steps: List[str] = Field(default_factory=list)
