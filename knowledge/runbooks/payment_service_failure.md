# Runbook: Payment Service 5xx Outages & Failure Modes

## Overview
Guidelines for resolving Sev-1 / Sev-2 payment processing failures on `POST /v1/charges` and checkout webhooks.

## Architecture Context
`payment-service` connects to:
- `database-primary` (stores ledger transactions, card tokens, idempotent keys)
- `stripe-gateway` (external payment provider)
- `auth-service` (validates client and merchant credentials)

## Common Failure Modes & Indicators
1. **Third-Party Payment Gateway Outage**:
   - Indicator: `stripe_gateway_error_rate` > 5%, circuit breaker open.
   - Action: Check Stripe status page; activate backup payment processor if enabled.
2. **Internal Database Pool Starvation**:
   - Indicator: `db_connection_pool_utilization` > 95%, `PoolTimeoutException` in logs, Stripe latency is normal (<150ms).
   - Action: Check for connection leaks in recent release; restart pods and bump max pool size.
3. **Idempotency Key Conflict / Deadlock**:
   - Indicator: 409 Conflict errors or Postgres transaction serialization failures.
   - Action: Verify client retry logic and exponential backoff configuration.

## Escalation Path
- Primary On-Call: @payments-oncall
- Secondary: SRE Lead / Database Admin
