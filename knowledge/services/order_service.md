# Service Architecture: Order & Fulfillment Service

## Overview
`order-service` handles the shopping cart checkout pipeline, inventory reservations, order lifecycle transitions, and shipment creation.

## Technical Specifications
- **Framework**: Node.js / Express
- **Databases**: PostgreSQL (`inventory-db`, `order-db`)
- **Dependencies**: `payment-service`, `auth-service`, `inventory-db`

## Key Operations
- `POST /orders`: Coordinates inventory reservation, payment authorization via `payment-service`, and order confirmation.
