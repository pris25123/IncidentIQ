# Postmortem: Incident #970 — Worker Node Memory Leak & OOMKilled

## Incident Summary
- **Date**: May 18, 2024
- **Duration**: Occurred intermittently over 4 hours
- **Impact**: Delayed processing of background jobs, report generation timeouts, and email dispatch failures.
- **Affected Services**: `worker-node`

## Root Cause
A newly introduced PDF report generation library failed to properly close `OutputStream` buffers and release off-heap memory allocations when processing large datasets (>50,000 rows). Over the course of several hours, the `worker-node` JVM heap usage gradually climbed to 100%. 
The garbage collector began thrashing (using 85% of CPU time), eventually resulting in `java.lang.OutOfMemoryError: Java heap space`. The Kubernetes scheduler continually restarted the pods with `OOMKilled`, causing looping job failures.

## Key Indicators During Incident
- Metric `memory_usage_mb` climbed steadily from 250MB to 1800MB (pod limit).
- Metric `pod_restarts` recorded 5 restarts within 30 minutes.
- Logs showed `Garbage collection taking longer than expected. Heap usage at 85%.`
- Logs confirmed `java.lang.OutOfMemoryError: Java heap space. Process terminating.`

## Resolution
1. Reverted the PDF generation feature branch to the previous stable iText library version.
2. Flushed the dead-letter queue and re-queued failed background jobs to fresh worker pods.
3. Temporarily increased worker pod memory limits from 2GB to 4GB to stabilize processing during the backlog recovery.

## Lessons Learned & Action Items
- Ensure strict `try-with-resources` blocks are used for all file and stream operations.
- Introduce memory profiling steps in the CI/CD pipeline for heavy worker tasks.
- Isolate report generation into its own dedicated pod pool to prevent interference with critical email/job dispatching.
