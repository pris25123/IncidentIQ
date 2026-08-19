import json
import sys
from pathlib import Path
# pyrefly: ignore [missing-import]
from mcp.server.fastmcp import FastMCP

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.postgres import (
    get_incident_by_id,
    get_service_logs,
    get_service_metrics,
    get_service_details,
    get_past_incidents,
)

server = FastMCP(
    name="incidentiq-operational-mcp-server",
    instructions=(
        "Production Incident Investigation MCP Tool Server. "
        "Provides access to live operational telemetry, incidents, logs, metrics, and service topologies "
        "stored in Supabase PostgreSQL."
    ),
)


@server.tool(name="get_incident")
def get_incident(incident_id: str) -> str:
    """
    Fetch incident details including severity, affected service, timeline, and description.
    """
    inc = get_incident_by_id(incident_id.strip())
    if not inc:
        return json.dumps({"error": f"Incident '{incident_id}' not found."}, default=str)
    return json.dumps(inc, indent=2, default=str)


@server.tool(name="get_logs")
def get_logs(service: str, level: str | None = None, limit: int = 20) -> str:
    """
    Fetch recent system logs for a specific service.
    Can filter by log level (ERROR, WARN, INFO, DEBUG).
    """
    logs = get_service_logs(service=service.strip(), level=level, limit=int(limit))
    return json.dumps(logs, indent=2, default=str)


@server.tool(name="get_metrics")
def get_metrics(service: str, metric_name: str | None = None, limit: int = 20) -> str:
    """
    Fetch operational timeseries metrics (e.g. db_connection_pool_utilization, http_5xx_error_rate, p99_latency_ms).
    """
    metrics = get_service_metrics(service=service.strip(), metric_name=metric_name, limit=int(limit))
    return json.dumps(metrics, indent=2, default=str)


@server.tool(name="get_service_health")
def get_service_health(service_name: str) -> str:
    """
    Fetch service ownership, tier, architectural description, and upstream/downstream dependencies.
    """
    details = get_service_details(service_name.strip())
    if not details:
        return json.dumps({"error": f"Service '{service_name}' not found."}, default=str)
    return json.dumps(details, indent=2, default=str)


@server.tool(name="get_incident_history")
def get_incident_history(service: str) -> str:
    """
    Fetch historical incidents and outages associated with a specific service.
    """
    history = get_past_incidents(service=service.strip())
    return json.dumps(history, indent=2, default=str)


if __name__ == "__main__":
    server.run(transport="stdio")
