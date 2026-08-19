# Runbook: High API Latency & Degradation

## Overview
Diagnostic procedures when service p95 or p99 response times breach critical SLA thresholds (>500ms for tier-1 services).

## Diagnosis Workflow
1. **Identify Bottleneck Layer**:
   - Check API Gateway upstream response times.
   - Check Downstream Dependency Latency (DB, Redis, Third-Party Gateways).
   - If downstream latency is low but total response time is high, check CPU throttling and garbage collection pauses.
2. **Database Query Analysis**:
   - Inspect active queries in `pg_stat_activity` for locks, table scans, or missing indexes.
3. **Cache Layer Health**:
   - Check Redis/Memcached cache hit ratio. If hit ratio drops below 80%, investigate cache key eviction or stampede.

## Remediation
- Scale horizontal pod autoscaler (HPA) replicas.
- Enable circuit breakers for slow external dependencies.
- Enable query caching or adjust cache TTLs.
