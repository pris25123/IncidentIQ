# Runbook: Memory Exhaustion (OOM) & Garbage Collection Thrashing

## Overview
Procedures for identifying and mitigating Out-Of-Memory (OOM) kills and high JVM/Node memory pressure across production services.

## Triage Signals
- Pod restarts with termination reason: `OOMKilled` (Exit code 137).
- Memory usage constantly climbing with sawtooth pattern and high GC pause times (>2000ms).
- Drop in throughput as CPU is spent on full GC cycles.

## Remediation
1. Capture heap dump before pod eviction if leak suspect (`-XX:+HeapDumpOnOutOfMemoryError`).
2. Temporarily increase memory limits in Helm values / deployment manifest.
3. Roll back any release that introduced in-memory caching or unbounded collection growth.
