import json
from typing import Any
from src.db.postgres import (
    get_incident_by_id,
    get_service_logs,
    get_service_metrics,
    get_service_details,
    get_past_incidents,
)


class IncidentMCPClient:
    """
    Client for IncidentIQ Operational MCP Tools.
    Provides standard tool calling interface for the LangGraph agent.
    """

    @staticmethod
    def get_incident(incident_id: str) -> dict:
        inc = get_incident_by_id(incident_id.strip())
        return inc or {"error": f"Incident '{incident_id}' not found."}

    @staticmethod
    def get_logs(service: str, level: str | None = None, limit: int = 20) -> list[dict]:
        return get_service_logs(service=service.strip(), level=level, limit=limit)

    @staticmethod
    def get_metrics(service: str, metric_name: str | None = None, limit: int = 20) -> list[dict]:
        return get_service_metrics(service=service.strip(), metric_name=metric_name, limit=limit)

    @staticmethod
    def get_service_health(service_name: str) -> dict:
        details = get_service_details(service_name.strip())
        return details or {"error": f"Service '{service_name}' not found."}

    @staticmethod
    def get_incident_history(service: str) -> list[dict]:
        return get_past_incidents(service=service.strip())

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Route tool invocation to the corresponding operational MCP tool."""
        tool_map = {
            "get_incident": lambda a: self.get_incident(a.get("incident_id", "")),
            "get_logs": lambda a: self.get_logs(
                a.get("service", ""),
                level=a.get("level"),
                limit=a.get("limit", 20),
            ),
            "get_metrics": lambda a: self.get_metrics(
                a.get("service", ""),
                metric_name=a.get("metric_name"),
                limit=a.get("limit", 20),
            ),
            "get_service_health": lambda a: self.get_service_health(a.get("service_name", "")),
            "get_incident_history": lambda a: self.get_incident_history(a.get("service", "")),
        }

        handler = tool_map.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: '{tool_name}'"}
        return handler(arguments)
