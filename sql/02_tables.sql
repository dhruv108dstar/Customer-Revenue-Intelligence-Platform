CREATE TABLE IF NOT EXISTS raw_customer_snapshot (
    customer_id BIGINT,
    gender VARCHAR(30),
    age INTEGER,
    city VARCHAR(100),
    state VARCHAR(20),
    region VARCHAR(50),
    signup_date DATE,
    tenure_months INTEGER,
    plan_id VARCHAR(20),
    contract_type VARCHAR(30),
    payment_method VARCHAR(30),
    device_type VARCHAR(30),
    churn INTEGER
);

CREATE TABLE IF NOT EXISTS raw_transaction_snapshot (
    transaction_id BIGINT,
    customer_id BIGINT,
    transaction_date DATE,
    transaction_type VARCHAR(50),
    amount NUMERIC(12,2),
    payment_status VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS raw_usage_snapshot (
    usage_id BIGINT,
    customer_id BIGINT,
    usage_date DATE,
    data_used_gb NUMERIC(12,2),
    voice_minutes NUMERIC(12,2),
    sms_count NUMERIC(12,2),
    roaming_minutes NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS quality_summary (
    table_name VARCHAR(100),
    records INTEGER,
    duplicate_rate_pct NUMERIC(8,4),
    missing_rate_pct NUMERIC(8,4),
    overall_quality_score NUMERIC(8,4),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
