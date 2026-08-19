# Runbook: Authentication Service Degradation & Token Validation Failures

## Overview
Remediation procedures for high latency or error spikes in `auth-service` and JWT validation endpoints.

## Root Causes & Triage
1. **Redis Cache Eviction**:
   - Symptoms: `redis_cache_hit_ratio` collapses (<50%), Postgres DB CPU surges as auth queries bypass cache.
   - Action: Increase Redis cluster memory, tune `maxmemory-policy` to `allkeys-lru`.
2. **JWKS Key Rotation Lag**:
   - Symptoms: Validation failures for newly minted tokens while old tokens succeed.
   - Action: Force JWKS cache refresh on downstream gateway services.
3. **Database Connection Saturation**:
   - Symptoms: Auth service unable to query user profiles / session tables.
   - Action: Scale read-replicas for user authentication queries.
