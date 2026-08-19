# Service Architecture: Payment Service

## Overview
`payment-service` is a Tier-1 core microservice responsible for processing customer charges, payment method vaulting, fraud evaluation, and subscription billing.

## Technical Specifications
- **Framework**: Spring Boot / Java 21
- **Database**: PostgreSQL (Primary database: `database-primary`)
- **Connection Pool**: HikariCP (Max pool size: 100 connections, connection timeout: 30,000ms)
- **External Dependencies**:
  - `stripe-gateway`: External third-party payment gateway via HTTPS REST API
  - `auth-service`: OAuth2 token validation and merchant authentication
  - `database-primary`: Core transactional ledger for charge records

## Critical Endpoints
- `POST /v1/charges`: Synchronous payment processing endpoint
- `POST /v1/refunds`: Issue refund against transaction ID
- `POST /v1/webhooks/stripe`: Inbound webhook listener for asynchronous settlement

## Known Fragilities & Bottlenecks
- Synchronous database transaction locks during external webhook calls can saturate the HikariCP pool.
- Connection leaks if database sessions are not cleanly released in try-with-resources blocks.
