# Runbook: Cache Stampede & Database Overload

## Overview
Procedures for identifying and mitigating cache stampedes where mass key expiration or eviction causes a flood of database read queries.

## Triage Signals
- Sudden and severe drop in `cache_hit_ratio` (< 50%).
- Database `read_iops` or CPU spikes simultaneously with the cache miss spike.
- Logs indicating mass cache eviction, such as wildcard deletions or TTL expirations across huge key ranges.

## Remediation
1. Stop the offending script, job, or deploy that triggered the mass cache invalidation.
2. Implement a rate-limited cache warming process. Do not allow all application pods to query the DB directly to fill the cache at once.
3. Temporarily scale out database read replicas to handle the thundering herd if cache warming is too slow.
4. If applicable, enable a circuit breaker on DB read paths to fail fast and shed load until the database recovers.
