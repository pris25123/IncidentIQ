"""
guardrails.py — Input validation and output verification for IncidentIQ agent.

Provides two layers of protection:
1. Input Guardrails: Validate incident_id format, sanitize query text,
   reject empty/malicious inputs before the agent runs.
2. Output Guardrails: Validate the LLM's synthesized JSON response
   contains all required fields with correct types and non-empty values.

Usage:
    from src.agent.guardrails import validate_input, validate_rca_output

    errors = validate_input(incident_id, query)
    if errors:
        raise ValueError(errors)

    validated_output = validate_rca_output(raw_llm_json)
"""
import re
from typing import Optional


# --- INPUT GUARDRAILS ---

INCIDENT_ID_PATTERN = re.compile(r"^INC-\d{4}-\d{3,5}$")
MAX_QUERY_LENGTH = 2000
MIN_QUERY_LENGTH = 10


def validate_input(incident_id: str, query: str) -> list[str]:
    """
    Validates user input before the agent workflow begins.
    Returns a list of error messages. Empty list = all valid.
    """
    errors = []

    # Validate incident_id format
    if not incident_id or not incident_id.strip():
        errors.append("Incident ID is required.")
    elif not INCIDENT_ID_PATTERN.match(incident_id.strip()):
        errors.append(
            f"Invalid incident ID format: '{incident_id}'. "
            f"Expected format: INC-YYYY-NNN (e.g., INC-2024-817)."
        )

    # Validate query
    if not query or not query.strip():
        errors.append("Investigation query cannot be empty.")
    elif len(query.strip()) < MIN_QUERY_LENGTH:
        errors.append(
            f"Query too short ({len(query.strip())} chars). "
            f"Minimum {MIN_QUERY_LENGTH} characters required for meaningful investigation."
        )
    elif len(query.strip()) > MAX_QUERY_LENGTH:
        errors.append(
            f"Query too long ({len(query.strip())} chars). "
            f"Maximum {MAX_QUERY_LENGTH} characters allowed."
        )

    return errors


# --- OUTPUT GUARDRAILS ---

REQUIRED_RCA_FIELDS = {
    "likely_root_cause": str,
    "evidence": list,
    "recommended_actions": list,
    "confidence": str,
}

VALID_CONFIDENCE_LEVELS = {"High", "Medium", "Low"}


def validate_rca_output(parsed_json: dict) -> dict:
    """
    Validates and normalizes the LLM's RCA output.
    Fills missing fields with safe defaults rather than crashing.
    Returns:
        {
            "is_valid": bool,
            "warnings": list[str],
            "output": dict  (cleaned/normalized)
        }
    """
    warnings = []
    output = dict(parsed_json)

    # Check required fields
    for field, expected_type in REQUIRED_RCA_FIELDS.items():
        if field not in output:
            warnings.append(f"Missing required field: '{field}'. Using default.")
            if expected_type == str:
                output[field] = "Unable to determine — insufficient evidence."
            elif expected_type == list:
                output[field] = []
        elif not isinstance(output[field], expected_type):
            warnings.append(
                f"Field '{field}' has wrong type: expected {expected_type.__name__}, "
                f"got {type(output[field]).__name__}. Attempting conversion."
            )
            if expected_type == list and isinstance(output[field], str):
                output[field] = [output[field]]
            elif expected_type == str:
                output[field] = str(output[field])

    # Validate evidence list is non-empty
    if not output.get("evidence"):
        warnings.append("Evidence list is empty. RCA may lack supporting data.")
        output["evidence"] = ["No corroborating evidence was generated."]

    # Validate recommended_actions is non-empty
    if not output.get("recommended_actions"):
        warnings.append("No recommended actions generated.")
        output["recommended_actions"] = ["Manual investigation recommended."]

    # Validate confidence level
    confidence = output.get("confidence", "")
    if confidence not in VALID_CONFIDENCE_LEVELS:
        warnings.append(
            f"Invalid confidence level: '{confidence}'. Defaulting to 'Medium'."
        )
        output["confidence"] = "Medium"

    # Validate root cause is substantive (not just a few words)
    root_cause = output.get("likely_root_cause", "")
    if len(root_cause) < 20:
        warnings.append(
            f"Root cause too short ({len(root_cause)} chars). May be incomplete."
        )

    is_valid = len(warnings) == 0

    return {
        "is_valid": is_valid,
        "warnings": warnings,
        "output": output,
    }
