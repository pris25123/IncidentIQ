# Postmortem: Incident #950 — Cache Layer Stampede causing DB Overload

## Incident Summary
- **Date**: March 12, 2024
- **Duration**: 28 minutes
- **Impact**: Primary database CPU pegged at 98%, causing 500 errors across multiple read-heavy services.
- **Affected Services**: `cache-layer`, `database-primary`, `product-service`

## Root Cause
A bulk catalog update script was deployed which issued a mass `DEL catalog:products:*` command to the Redis cluster instead of performing targeted invalidation. This sudden loss of 45,000 cached product keys caused an immediate cache miss rate spike.
The resulting cache stampede sent 9,500 simultaneous read queries to the `database-primary` replica nodes. The database CPU spiked to 98% and read query queues overflowed, degrading performance for all dependent services.

## Key Indicators During Incident
- Metric `cache_hit_ratio` dropped from 98.5% to 12.5% in 5 minutes.
- Metric `read_iops` on `database-primary` spiked from 450 to 9,500.
- Logs flooded with `High CPU usage detected on replica nodes. Read connections queuing.` and `Mass eviction triggered for key pattern`.

## Resolution
1. Temporarily paused the bulk catalog update script.
2. Implemented a gradual "cache-warming" script to slowly repopulate Redis from the database at 50 IOPS.
3. Scaled up read replicas to absorb the initial stampede.

## Lessons Learned & Action Items
- Never use wildcard `DEL` or `KEYS` commands in production for massive datasets.
- Implement random jitter on cache TTLs to prevent synchronized expiration.
- Add application-level "probabilistic early expiration" to mitigate cache stampedes on hot keys.
