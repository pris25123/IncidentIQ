import psycopg2
from psycopg2.extras import RealDictCursor
from src.config import DATABASE_URL


def get_db_connection():
    """Create a new PostgreSQL database connection using the configured DATABASE_URL."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set. Please check your .env or secrets.")
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def execute_script(sql: str):
    """Execute raw SQL statements / scripts."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def fetch_all(query: str, params=None) -> list[dict]:
    """Execute a SELECT query and return all rows as list of dicts."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            return [dict(row) for row in rows]


def fetch_one(query: str, params=None) -> dict | None:
    """Execute a SELECT query and return a single row as dict."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            row = cur.fetchone()
            return dict(row) if row else None


# Dedicated operational data queries
def get_incident_by_id(incident_id: str) -> dict | None:
    query = "SELECT * FROM incidents WHERE incident_id = %s"
    return fetch_one(query, (incident_id,))


def list_all_incidents() -> list[dict]:
    query = "SELECT * FROM incidents ORDER BY start_time DESC"
    return fetch_all(query)


def get_service_logs(service: str, level: str = None, limit: int = 30) -> list[dict]:
    if level:
        query = """
            SELECT timestamp, service, level, message, context 
            FROM logs 
            WHERE service = %s AND level = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        return fetch_all(query, (service, level.upper(), limit))
    else:
        query = """
            SELECT timestamp, service, level, message, context 
            FROM logs 
            WHERE service = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        return fetch_all(query, (service, limit))


def get_service_metrics(service: str, metric_name: str = None, limit: int = 30) -> list[dict]:
    if metric_name:
        query = """
            SELECT timestamp, service, metric_name, value, unit 
            FROM metrics 
            WHERE service = %s AND metric_name = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        return fetch_all(query, (service, metric_name, limit))
    else:
        query = """
            SELECT timestamp, service, metric_name, value, unit 
            FROM metrics 
            WHERE service = %s 
            ORDER BY timestamp DESC 
            LIMIT %s
        """
        return fetch_all(query, (service, limit))


def get_service_details(service_name: str) -> dict | None:
    query = "SELECT * FROM services WHERE service_name = %s"
    return fetch_one(query, (service_name,))


def get_past_incidents(service: str) -> list[dict]:
    query = """
        SELECT incident_id, title, severity, status, start_time, end_time, description 
        FROM incidents 
        WHERE service = %s 
        ORDER BY start_time DESC
    """
    return fetch_all(query, (service,))
