# Runbook: Database Connection Pool Exhaustion & PoolTimeoutException

## Overview
This runbook provides diagnostic and remediation steps when microservices experience database connection pool exhaustion (e.g. HikariCP `PoolTimeoutException`, `CannotAcquireConnectionException`).

## Service Scope
- `payment-service`
- `order-service`
- `auth-service`

## Symptoms & Triage Signals
- **Metrics**:
  - `db_connection_pool_utilization` > 90%
  - Spike in `http_5xx_error_rate` on endpoints performing transactional DB writes (e.g., `/v1/charges`, `/v1/checkout`)
  - Sudden jump in `p99_latency_ms` matching the connection timeout threshold (default 30000ms / 30s)
  - `active_db_connections` equal to `max_pool_size` (e.g., 100/100)
- **Log Signatures**:
  - `[HikariPool-1] Connection is not available, request timed out after 30000ms`
  - `HikariCP PoolTimeoutException: Timeout after 30001ms waiting for connection`
  - `Failed to acquire database connection from pool`

## Potential Root Causes
1. **Unclosed DB Connections / Connection Leak**: Code paths holding open connections while waiting on slow external HTTP requests (e.g. holding DB transaction while calling Stripe or 3rd party API).
2. **Long-Running Unindexed Queries**: Queries holding locks or scanning large tables, preventing connections from returning to the pool.
3. **Traffic Spike Exceeding Pool Capacity**: Sudden concurrency surge where `max_pool_size` is insufficient for the pod count and request volume.
4. **Database Thread Saturation**: PostgreSQL database reaching `max_connections` limit or running out of worker threads.

## Immediate Mitigation Steps
1. **Verify Upstream Status**: Check if 3rd-party APIs (e.g. Stripe, Auth0) are slow. If upstream is healthy and latency is normal, the issue is internal.
2. **Increase Pool Capacity**:
   - Temporarily increase `SPRING_DATASOURCE_HIKARI_MAX_LIFETIME` and `SPRING_DATASOURCE_HIKARI_MAXIMUM_POOL_SIZE` from 100 to 150 if PostgreSQL server has available capacity.
3. **Restart Degraded Pods**:
   - Execute rolling restart of `payment-service` deployment to purge leaked connections:
     `kubectl rollout restart deployment/payment-service`
4. **Enable Connection Leak Detection**:
   - Set `leakDetectionThreshold: 2000` in HikariCP configuration to log stack traces of unclosed connections.

## Long-term Prevention
- Ensure database transactions are scoped tightly around DB operations only, never spanning external network calls.
- Implement aggressive query timeouts (`statement_timeout = 3000ms`).
