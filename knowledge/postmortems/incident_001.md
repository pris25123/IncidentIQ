# Postmortem: Incident #817 — Payment Service Database Connection Pool Exhaustion

## Incident Summary
- **Date**: November 24, 2023
- **Duration**: 42 minutes
- **Impact**: 38% of checkout transactions failed with HTTP 500 errors. Estimated $140k GMV impact.
- **Affected Services**: `payment-service`, `order-service`

## Root Cause
A deployment introduced a code change in `PaymentController.java` where a database transaction was held open while synchronously awaiting a webhook confirmation response from an external payment gateway. When gateway latency experienced a minor 100ms jitter, the database connection hold duration increased from 15ms to 1200ms. 

This rapidly exhausted the HikariCP connection pool (100 max connections), reaching 99% pool utilization within 6 minutes. Subsequent requests queued up and threw `PoolTimeoutException` after 30 seconds, generating widespread 500 Internal Server Errors on `POST /v1/charges`.

## Key Indicators During Incident
- Metric `db_connection_pool_utilization` jumped from 32% to 98.4%.
- Metric `http_5xx_error_rate` climbed to 36.8%.
- Metric `p99_latency_ms` pegged at 30,000ms (timeout limit).
- Logs flooded with `[HikariPool-1] Connection is not available, request timed out after 30000ms`.
- Upstream Stripe gateway error rate was 0.0%, confirming the issue was entirely internal.

## Resolution
1. Executed immediate rollback to previous build v2.13.4.
2. Restarted all 12 `payment-service` pods to clear deadlocked connections.
3. Added HikariCP connection leak detection (`leakDetectionThreshold = 2000ms`).

## Lessons Learned & Action Items
- Never hold active database transactions across network boundaries / external HTTP calls.
- Configure separate asynchronous workers for webhook handling.
- Set alerting on `db_connection_pool_utilization > 80%` for > 2 minutes.
