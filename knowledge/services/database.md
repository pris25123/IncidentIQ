# Service Architecture: Database Infrastructure (PostgreSQL Primary)

## Overview
`database-primary` is the multi-AZ high-availability PostgreSQL 15 cluster providing transactional persistence for payments, orders, and user identity.

## Specifications
- **Max Connections**: 300
- **Connection Pool**: PgBouncer sitting before PostgreSQL
- **Default Statement Timeout**: 10,000ms
- **Lock Timeout**: 5,000ms
