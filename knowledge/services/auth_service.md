# Service Architecture: Authentication & Identity Service

## Overview
`auth-service` manages identity, single sign-on (SSO), JWT token minting/verification, and API key management across all services.

## Technical Specifications
- **Framework**: Go / Gin
- **Primary Datastore**: PostgreSQL (`database-primary`)
- **Cache**: Redis Cluster (`redis-cluster`)
- **Tokens**: RS256 signed JSON Web Tokens (JWT) with 15-minute expiration

## Dependencies
- `redis-cluster`: Caches public keys, session revokations, and rate limit counters
- `database-primary`: Source of truth for user accounts and credential hashes
