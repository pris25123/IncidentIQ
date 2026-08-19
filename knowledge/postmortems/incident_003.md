# Postmortem: Incident #510 — Order Service Row Lock Contention on Hot SKU

## Incident Summary
- **Duration**: 55 minutes
- **Impact**: Checkout transaction drop of 40% during flash sale.
- **Affected Services**: `order-service`, `inventory-db`

## Root Cause
Concurrent transactions attempted to decrement inventory using `SELECT ... FOR UPDATE` on a single database row representing a popular SKU. Hundreds of concurrent transactions blocked on the same row lock, causing database connection backlog and deadlocks.

## Resolution
1. Implemented optimistic locking with Redis-based distributed reservation counters.
2. Switched from row-level pessimistic locks to decoupled batch updates.
