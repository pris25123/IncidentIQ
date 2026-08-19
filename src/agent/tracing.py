"""
tracing.py — Lightweight agent observability and tracing for IncidentIQ.

Records structured traces for every LangGraph node execution, including:
- Node name, start/end timestamps, duration (ms)
- Input/output state snapshots
- Token usage estimates
- Error tracking

Usage:
    from src.agent.tracing import InvestigationTracer

    tracer = InvestigationTracer()
    tracer.start_node("gather_telemetry")
    # ... do work ...
    tracer.end_node(input_snapshot={...}, output_snapshot={...})
    tracer.get_trace_summary()
"""
import time
import json
from datetime import datetime, timezone
from typing import Any, Optional


class NodeTrace:
    """Represents a single traced node execution."""

    def __init__(self, node_name: str):
        self.node_name = node_name
        self.start_time = datetime.now(timezone.utc)
        self.end_time: Optional[datetime] = None
        self.duration_ms: float = 0.0
        self.input_keys: list[str] = []
        self.output_keys: list[str] = []
        self.output_summary: dict = {}
        self.error: Optional[str] = None
        self.status: str = "RUNNING"

    def complete(self, input_snapshot: dict, output_snapshot: dict):
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.input_keys = list(input_snapshot.keys()) if input_snapshot else []
        self.output_keys = list(output_snapshot.keys()) if output_snapshot else []
        self.status = "SUCCESS"

        # Summarize output without dumping full content
        for key, val in output_snapshot.items():
            if isinstance(val, list):
                self.output_summary[key] = f"{len(val)} items"
            elif isinstance(val, dict):
                self.output_summary[key] = f"dict({len(val)} keys)"
            elif isinstance(val, str) and len(val) > 100:
                self.output_summary[key] = f"str({len(val)} chars)"
            else:
                self.output_summary[key] = str(val)[:80]

    def fail(self, error: str):
        self.end_time = datetime.now(timezone.utc)
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        self.error = error
        self.status = "FAILED"

    def to_dict(self) -> dict:
        return {
            "node": self.node_name,
            "status": self.status,
            "start": self.start_time.isoformat(),
            "end": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": round(self.duration_ms, 1),
            "input_keys": self.input_keys,
            "output_keys": self.output_keys,
            "output_summary": self.output_summary,
            "error": self.error,
        }


class InvestigationTracer:
    """
    Collects structured traces across a full LangGraph investigation run.
    Designed to be lightweight and non-intrusive — no external dependencies.
    """

    def __init__(self, incident_id: str = ""):
        self.incident_id = incident_id
        self.run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.traces: list[NodeTrace] = []
        self._current: Optional[NodeTrace] = None
        self.run_start = datetime.now(timezone.utc)
        self.run_end: Optional[datetime] = None

    def start_node(self, node_name: str):
        """Begin tracing a node execution."""
        self._current = NodeTrace(node_name)
        self.traces.append(self._current)

    def end_node(self, input_snapshot: dict = None, output_snapshot: dict = None):
        """Mark the current node as successfully completed."""
        if self._current:
            self._current.complete(input_snapshot or {}, output_snapshot or {})
            self._current = None

    def fail_node(self, error: str):
        """Mark the current node as failed."""
        if self._current:
            self._current.fail(error)
            self._current = None

    def finish(self):
        """Mark the full investigation run as complete."""
        self.run_end = datetime.now(timezone.utc)

    def get_total_duration_ms(self) -> float:
        end = self.run_end or datetime.now(timezone.utc)
        return (end - self.run_start).total_seconds() * 1000

    def get_trace_summary(self) -> dict:
        """Returns a structured summary of the full trace for UI display or logging."""
        return {
            "run_id": self.run_id,
            "incident_id": self.incident_id,
            "total_duration_ms": round(self.get_total_duration_ms(), 1),
            "node_count": len(self.traces),
            "failed_nodes": sum(1 for t in self.traces if t.status == "FAILED"),
            "nodes": [t.to_dict() for t in self.traces],
        }

    def get_trace_json(self) -> str:
        """Returns the trace as a formatted JSON string."""
        return json.dumps(self.get_trace_summary(), indent=2, default=str)
