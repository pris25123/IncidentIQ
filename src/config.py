import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


def _get_secret_or_env(key: str, default: str = "") -> str:
    """Retrieve config from os.environ first, then Streamlit secrets if missing."""
    val = os.getenv(key, "").strip()
    if val:
        return val
    if "streamlit" in sys.modules:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and key in st.secrets:
                return str(st.secrets[key]).strip()
        except Exception:
            pass
    return default


def sanitize_db_url(url: str) -> str:
    """
    Sanitizes database URL:
    1. Removes bracket placeholders like :[password]@ -> :password@
    2. Fallback to Supabase pooler host for IPv4 networks when direct host db.<ref>.supabase.co fails DNS.
    """
    if not url:
        return ""
    clean = re.sub(r':\[([^\]]+)\]@', r':\1@', url)

    # Detect Supabase direct connection and provide pooler-compatible format
    match = re.search(r'postgresql://([^:]+):([^@]+)@db\.([a-zA-Z0-9_-]+)\.supabase\.co(?::\d+)?/(.+)', clean)
    if match:
        user_orig, pwd, ref, dbname = match.groups()
        pooler_host = "aws-0-ap-southeast-2.pooler.supabase.com"
        pooler_user = f"postgres.{ref}"
        clean = f"postgresql://{pooler_user}:{pwd}@{pooler_host}:5432/{dbname}"

    return clean


# Application credentials & URLs
GEMINI_API_KEY = _get_secret_or_env("GEMINI_API_KEY")
QDRANT_API_KEY = _get_secret_or_env("QDRANT_API_KEY")
QDRANT_URL = _get_secret_or_env("QDRANT_URL")
RAW_DATABASE_URL = _get_secret_or_env("DATABASE_URL")
DATABASE_URL = sanitize_db_url(RAW_DATABASE_URL)

QDRANT_COLLECTION = "incidentiq_knowledge"
EMBEDDING_MODEL_NAME = "gemini-embedding-001"
EMBEDDING_DIMENSION = 3072
DEFAULT_LLM_MODEL = "gemini-flash-latest"
