# Runbook: 3rd-Party API Rate Limiting & Circuit Breakers

## Overview
Procedures for handling scenarios where upstream APIs (e.g. Stripe, Twilio, SendGrid) return 429 Too Many Requests, causing circuit breakers to open and local services to fail.

## Triage Signals
- Metric `upstream_<provider>_429_rate` spikes.
- Application logs show `Circuit breaker [...] changed state to OPEN`.
- Widespread 503 Service Unavailable errors on local endpoints that depend on the upstream provider.

## Remediation
1. Identify the upstream provider returning 429s from logs or metrics.
2. If the traffic spike is legitimate (e.g., marketing campaign), immediately contact the vendor's enterprise support to request a quota increase.
3. If the traffic spike is abusive (bot traffic), block the offending IP ranges at the WAF level to stop the API calls.
4. Once the rate limit is resolved, verify the circuit breaker returns to CLOSED state automatically, or force it closed via admin overrides if it remains stuck.
5. Push failed asynchronous tasks into a Dead Letter Queue (DLQ) for replay.
