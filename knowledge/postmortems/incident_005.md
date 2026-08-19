# Postmortem: Incident #960 — Gateway Service 3rd-Party Rate Limiting & 503s

## Incident Summary
- **Date**: April 05, 2024
- **Duration**: 45 minutes
- **Impact**: 85% failure rate for user registration flows relying on SMS OTP verification.
- **Affected Services**: `gateway-service`, `auth-service`

## Root Cause
An aggressive marketing campaign led to a 400% surge in user sign-ups. Our `gateway-service`, which acts as a proxy for the upstream SMS provider (Twilio), hit the provider's hard rate limit of 100 requests per second. The upstream provider began returning `429 Too Many Requests`.
Our API Gateway circuit breaker incorrectly mapped 429s as fatal network errors and tripped the `SmsProviderClient` circuit breaker open. This resulted in instantaneous 503 Service Unavailable errors for all subsequent registration flows until the circuit breaker timeout window reset.

## Key Indicators During Incident
- Metric `upstream_sms_429_rate` jumped to 99.9%.
- Logs indicated `Upstream Twilio API returned 429 Too Many Requests for SMS OTP delivery.`
- Logs confirmed `Circuit breaker [SmsProviderClient] changed state to OPEN.`

## Resolution
1. Contacted Twilio account manager to provision a temporary rate limit increase to 500 RPS.
2. Manually force-closed the circuit breaker via the admin console once the limit was raised.
3. Users who failed OTP were placed into a retry queue for asynchronous delivery.

## Lessons Learned & Action Items
- Properly handle HTTP 429 status codes with exponential backoff rather than immediately tripping circuit breakers.
- Implement proactive rate-limiting on our own API endpoints during marketing campaigns to smooth out traffic spikes.
- Establish automated alerts when approaching 80% of any 3rd-party API quota.
