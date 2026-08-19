-- IncidentIQ Operational Database Schema (Supabase PostgreSQL)

CREATE TABLE IF NOT EXISTS services (
    service_name VARCHAR(100) PRIMARY KEY,
    owner VARCHAR(100) NOT NULL,
    description TEXT,
    dependencies TEXT[],
    tier VARCHAR(20) DEFAULT 'tier-1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    service VARCHAR(100) REFERENCES services(service_name),
    severity VARCHAR(20) NOT NULL, -- critical, high, medium, low
    status VARCHAR(50) NOT NULL,   -- active, investigating, mitigated, resolved
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    description TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    service VARCHAR(100) NOT NULL,
    level VARCHAR(20) NOT NULL,    -- ERROR, WARN, INFO, DEBUG
    message TEXT NOT NULL,
    context JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    service VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL
);

-- Indexes for fast operational queries
CREATE INDEX IF NOT EXISTS idx_logs_service_time ON logs(service, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);
CREATE INDEX IF NOT EXISTS idx_metrics_service_metric ON metrics(service, metric_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_incidents_service ON incidents(service);
