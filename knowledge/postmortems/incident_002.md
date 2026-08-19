# Postmortem: Incident #402 — Auth Service Cache Eviction & Database CPU Surge

## Incident Summary
- **Duration**: 28 minutes
- **Impact**: Increased authentication latency (P99 > 900ms) across all API gateway ingress traffic.
- **Affected Services**: `auth-service`, `redis-cluster`, `database-primary`

## Root Cause
A misconfigured session TTL caused Redis to hit its `maxmemory` threshold. Redis began evicting active public signing keys, forcing `auth-service` to fall back to direct PostgreSQL queries for every token validation request. The sudden 10x query load drove Postgres CPU utilization to 92%, causing latency cascading to all downstream services.

## Key Indicators
- `redis_cache_hit_ratio` dropped from 99% to 15%.
- `jwt_validation_latency_ms` surged from 4ms to 850ms.
- Postgres CPU utilization spiked to 92%.
- Logs: `[RedisSessionStore] OOM command not allowed when used memory > 'maxmemory'`.

## Resolution
1. Flushed expired session keys and doubled Redis cluster memory allocation.
2. Updated eviction policy to `volatile-lru`.
