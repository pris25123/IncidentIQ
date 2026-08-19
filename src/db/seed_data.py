from datetime import datetime, timedelta, timezone
from pathlib import Path
from src.db.postgres import get_db_connection, execute_script


def seed_database():
    """Initializes tables and seeds synthetic DevOps operational data into Supabase PostgreSQL."""
    print("Executing schema DDL...")
    schema_path = Path(__file__).resolve().parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    execute_script(schema_sql)

    now = datetime.now(timezone.utc)

    # 1. Seed Services
    services_data = [
        (
            "payment-service",
            "Payments Core Team",
            "Processes credit card transactions, digital wallets, and payout integrations.",
            ["database-primary", "auth-service", "stripe-gateway"],
            "tier-1",
        ),
        (
            "auth-service",
            "Security & Identity Team",
            "Handles OAuth2, JWT generation/validation, and user sessions.",
            ["redis-cluster", "database-primary"],
            "tier-1",
        ),
        (
            "order-service",
            "Logistics & Checkout Team",
            "Orchestrates checkout pipeline, order state machines, and cart fulfillment.",
            ["payment-service", "inventory-db", "auth-service"],
            "tier-1",
        ),
        (
            "database-primary",
            "Data Infrastructure Team",
            "High-availability PostgreSQL cluster storing core ledger, user profiles, and orders.",
            [],
            "tier-0",
        ),
        (
            "cache-layer",
            "Platform Engineering Team",
            "Distributed Redis cache for session storage and frequent read queries.",
            [],
            "tier-1",
        ),
        (
            "gateway-service",
            "API Platform Team",
            "API Gateway for external routing, rate-limiting, and 3rd-party webhook handling.",
            ["payment-service", "auth-service", "order-service"],
            "tier-1",
        ),
        (
            "worker-node",
            "Compute Team",
            "Asynchronous worker pool processing background jobs, report generation, and email dispatches.",
            ["database-primary", "cache-layer"],
            "tier-2",
        ),
    ]

    # 2. Seed Incidents
    incidents_data = [
        (
            "INC-2024-817",
            "Payment API — HTTP 500 Spike & Connection Timeout",
            "payment-service",
            "critical",
            "active",
            now - timedelta(minutes=45),
            None,
            "Spike in HTTP 500 responses on POST /v1/charges and checkout endpoints. Customers unable to complete orders.",
        ),
        (
            "INC-2024-902",
            "Auth Service — High Latency & Token Verification Spike",
            "auth-service",
            "high",
            "investigating",
            now - timedelta(hours=2),
            None,
            "P99 latency on JWT authentication jumped from 5ms to 900ms. Intermittent 504 timeouts across dependent services.",
        ),
        (
            "INC-2024-945",
            "Order Service — Cascading Deadlocks on High Concurrency",
            "order-service",
            "medium",
            "mitigated",
            now - timedelta(days=1),
            now - timedelta(hours=22),
            "Inventory reservation locks causing deadlocks on concurrent flash sale checkout requests.",
        ),
        (
            "INC-2024-950",
            "Cache Layer — Stampede causing DB Overload",
            "cache-layer",
            "high",
            "investigating",
            now - timedelta(minutes=30),
            None,
            "Mass cache eviction of product catalog resulted in a cache stampede, overloading the primary database with read queries.",
        ),
        (
            "INC-2024-960",
            "Gateway Service — 3rd-Party Rate Limiting & 503s",
            "gateway-service",
            "critical",
            "active",
            now - timedelta(minutes=15),
            None,
            "Upstream SMS provider returning 429 Rate Limited, cascading into 503s for all user registration flows.",
        ),
        (
            "INC-2024-970",
            "Worker Node — Memory Leak & OOMKilled",
            "worker-node",
            "medium",
            "investigating",
            now - timedelta(hours=4),
            None,
            "Gradual memory bloat in the report generation worker leading to constant OOMKilled pod restarts.",
        ),
    ]

    # 3. Seed Metrics
    metrics_data = [
        # Payment service metrics (INC-2024-817)
        (now - timedelta(minutes=30), "payment-service", "db_connection_pool_utilization", 38.0, "%"),
        (now - timedelta(minutes=25), "payment-service", "db_connection_pool_utilization", 65.5, "%"),
        (now - timedelta(minutes=20), "payment-service", "db_connection_pool_utilization", 88.0, "%"),
        (now - timedelta(minutes=15), "payment-service", "db_connection_pool_utilization", 98.4, "%"),
        (now - timedelta(minutes=10), "payment-service", "db_connection_pool_utilization", 99.2, "%"),
        (now - timedelta(minutes=5), "payment-service", "db_connection_pool_utilization", 99.8, "%"),

        (now - timedelta(minutes=30), "payment-service", "http_5xx_error_rate", 0.02, "%"),
        (now - timedelta(minutes=25), "payment-service", "http_5xx_error_rate", 1.8, "%"),
        (now - timedelta(minutes=20), "payment-service", "http_5xx_error_rate", 12.4, "%"),
        (now - timedelta(minutes=15), "payment-service", "http_5xx_error_rate", 36.8, "%"),
        (now - timedelta(minutes=10), "payment-service", "http_5xx_error_rate", 42.1, "%"),

        (now - timedelta(minutes=30), "payment-service", "p99_latency_ms", 115.0, "ms"),
        (now - timedelta(minutes=20), "payment-service", "p99_latency_ms", 780.0, "ms"),
        (now - timedelta(minutes=15), "payment-service", "p99_latency_ms", 3200.0, "ms"),
        (now - timedelta(minutes=10), "payment-service", "p99_latency_ms", 5100.0, "ms"),

        (now - timedelta(minutes=15), "payment-service", "active_db_connections", 99.0, "connections"),
        (now - timedelta(minutes=15), "payment-service", "max_pool_size", 100.0, "connections"),

        (now - timedelta(minutes=15), "payment-service", "stripe_gateway_latency_ms", 140.0, "ms"),
        (now - timedelta(minutes=15), "payment-service", "stripe_gateway_error_rate", 0.0, "%"),

        # Auth Service metrics (INC-2024-902)
        (now - timedelta(hours=2, minutes=30), "auth-service", "p99_latency_ms", 5.0, "ms"),
        (now - timedelta(hours=2, minutes=20), "auth-service", "p99_latency_ms", 120.0, "ms"),
        (now - timedelta(hours=2, minutes=10), "auth-service", "p99_latency_ms", 450.0, "ms"),
        (now - timedelta(hours=2), "auth-service", "p99_latency_ms", 900.0, "ms"),
        (now - timedelta(hours=2), "auth-service", "jwt_validation_errors", 145.0, "count"),

        # Order Service metrics (INC-2024-945)
        (now - timedelta(days=1, hours=1), "order-service", "active_transactions", 1500.0, "tx"),
        (now - timedelta(days=1, minutes=30), "order-service", "db_deadlocks", 5.0, "count"),
        (now - timedelta(days=1), "order-service", "db_deadlocks", 45.0, "count"),
        (now - timedelta(days=1), "order-service", "checkout_failure_rate", 18.5, "%"),

        # Cache Layer metrics (INC-2024-950)
        (now - timedelta(minutes=35), "cache-layer", "cache_hit_ratio", 98.5, "%"),
        (now - timedelta(minutes=30), "cache-layer", "cache_hit_ratio", 42.1, "%"),
        (now - timedelta(minutes=25), "cache-layer", "cache_hit_ratio", 12.5, "%"),
        (now - timedelta(minutes=35), "database-primary", "read_iops", 450.0, "iops"),
        (now - timedelta(minutes=30), "database-primary", "read_iops", 4800.0, "iops"),
        (now - timedelta(minutes=25), "database-primary", "read_iops", 9500.0, "iops"),

        # Gateway Service metrics (INC-2024-960)
        (now - timedelta(minutes=20), "gateway-service", "upstream_sms_429_rate", 0.0, "%"),
        (now - timedelta(minutes=15), "gateway-service", "upstream_sms_429_rate", 85.0, "%"),
        (now - timedelta(minutes=10), "gateway-service", "upstream_sms_429_rate", 99.9, "%"),

        # Worker Node metrics (INC-2024-970)
        (now - timedelta(hours=4), "worker-node", "memory_usage_mb", 250.0, "MB"),
        (now - timedelta(hours=3), "worker-node", "memory_usage_mb", 600.0, "MB"),
        (now - timedelta(hours=2), "worker-node", "memory_usage_mb", 1200.0, "MB"),
        (now - timedelta(hours=1), "worker-node", "memory_usage_mb", 1800.0, "MB"),
        (now - timedelta(minutes=30), "worker-node", "pod_restarts", 5.0, "count"),
    ]

    # 4. Seed Logs
    logs_data = [
        # Payment service logs (INC-2024-817)
        (
            now - timedelta(minutes=26),
            "payment-service",
            "INFO",
            "Deployment v2.14.0 completed successfully across 12 pods.",
            '{"commit": "a8f309", "deployed_by": "ci-runner"}',
        ),
        (
            now - timedelta(minutes=22),
            "payment-service",
            "WARN",
            "[HikariPool-1] Connection pool utilization exceeding 85% (85/100 connections in use).",
            '{"pool": "HikariPool-1", "active": 85, "max": 100}',
        ),
        (
            now - timedelta(minutes=18),
            "payment-service",
            "ERROR",
            "[HikariPool-1] Connection is not available, request timed out after 30000ms. Client: payment-checkout-worker-8.",
            '{"error_code": "POOL_TIMEOUT", "timeout_ms": 30000}',
        ),
        (
            now - timedelta(minutes=15),
            "payment-service",
            "ERROR",
            "POST /v1/charges 500 Internal Server Error - Failed to acquire database connection from pool within 30000ms.",
            '{"http_status": 500, "endpoint": "/v1/charges", "trace_id": "tr-9482910a"}',
        ),
        (
            now - timedelta(minutes=12),
            "payment-service",
            "ERROR",
            "Cannot open connection for transaction [tx-89410]: HikariCP PoolTimeoutException: Timeout after 30001ms waiting for connection.",
            '{"exception": "PoolTimeoutException", "threads_waiting": 47}',
        ),
        (
            now - timedelta(minutes=10),
            "payment-service",
            "INFO",
            "Circuit breaker [StripeGatewayClient] status is CLOSED. Upstream response time: 135ms.",
            '{"circuit_breaker": "StripeGatewayClient", "state": "CLOSED"}',
        ),
        (
            now - timedelta(minutes=8),
            "payment-service",
            "ERROR",
            "HealthCheck failed: Database connection test query SELECT 1 timed out after 5000ms.",
            '{"health_status": "DEGRADED", "subsystem": "db_pool"}',
        ),

        # Auth Service logs (INC-2024-902)
        (
            now - timedelta(hours=2, minutes=15),
            "auth-service",
            "WARN",
            "High latency observed connecting to Redis session store.",
            '{"latency_ms": 115}',
        ),
        (
            now - timedelta(hours=2, minutes=5),
            "auth-service",
            "ERROR",
            "JWT token verification failed: public key resolution timeout.",
            '{"error_code": "JWT_KEY_TIMEOUT"}',
        ),

        # Order Service logs (INC-2024-945)
        (
            now - timedelta(days=1, minutes=20),
            "order-service",
            "WARN",
            "Transaction rollback triggered due to optimistic locking failure on inventory_items.",
            '{"table": "inventory_items", "retry_count": 3}',
        ),
        (
            now - timedelta(days=1, minutes=5),
            "order-service",
            "ERROR",
            "PSQLException: ERROR: deadlock detected. Detail: Process 1824 waits for ShareLock on transaction 94829.",
            '{"sql_state": "40P01", "pid": 1824}',
        ),

        # Cache Layer logs (INC-2024-950)
        (
            now - timedelta(minutes=31),
            "cache-layer",
            "WARN",
            "Mass eviction triggered for key pattern 'catalog:products:*'.",
            '{"evicted_keys": 45000}',
        ),
        (
            now - timedelta(minutes=30),
            "database-primary",
            "WARN",
            "High CPU usage detected on replica nodes. Read connections queuing.",
            '{"cpu_usage": "98%", "queued_connections": 120}',
        ),

        # Gateway Service logs (INC-2024-960)
        (
            now - timedelta(minutes=16),
            "gateway-service",
            "WARN",
            "Upstream Twilio API returned 429 Too Many Requests for SMS OTP delivery.",
            '{"provider": "twilio", "endpoint": "/v1/messages"}',
        ),
        (
            now - timedelta(minutes=15),
            "gateway-service",
            "ERROR",
            "Circuit breaker [SmsProviderClient] changed state to OPEN.",
            '{"circuit_breaker": "SmsProviderClient", "state": "OPEN", "failed_calls": 50}',
        ),

        # Worker Node logs (INC-2024-970)
        (
            now - timedelta(hours=2),
            "worker-node",
            "WARN",
            "Garbage collection taking longer than expected. Heap usage at 85%.",
            '{"heap_usage_mb": 1050, "gc_time_ms": 1400}',
        ),
        (
            now - timedelta(minutes=35),
            "worker-node",
            "ERROR",
            "java.lang.OutOfMemoryError: Java heap space. Process terminating.",
            '{"exception": "OutOfMemoryError"}',
        ),
    ]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Upsert services
            for s in services_data:
                cur.execute(
                    """
                    INSERT INTO services (service_name, owner, description, dependencies, tier)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (service_name) DO UPDATE 
                    SET owner = EXCLUDED.owner, description = EXCLUDED.description, dependencies = EXCLUDED.dependencies;
                    """,
                    s,
                )

            # Upsert incidents
            for inc in incidents_data:
                cur.execute(
                    """
                    INSERT INTO incidents (incident_id, title, service, severity, status, start_time, end_time, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (incident_id) DO UPDATE 
                    SET title = EXCLUDED.title, severity = EXCLUDED.severity, status = EXCLUDED.status,
                        description = EXCLUDED.description, start_time = EXCLUDED.start_time;
                    """,
                    inc,
                )

            # Clear old logs and metrics for idempotent seeding
            cur.execute("DELETE FROM logs;")
            cur.execute("DELETE FROM metrics;")

            # Insert metrics
            for m in metrics_data:
                cur.execute(
                    """
                    INSERT INTO metrics (timestamp, service, metric_name, value, unit)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    m,
                )

            # Insert logs
            for l in logs_data:
                cur.execute(
                    """
                    INSERT INTO logs (timestamp, service, level, message, context)
                    VALUES (%s, %s, %s, %s, %s::jsonb);
                    """,
                    l,
                )

        conn.commit()
    print("Database schema created and operational telemetry seeded successfully into Supabase PostgreSQL!")


if __name__ == "__main__":
    seed_database()
