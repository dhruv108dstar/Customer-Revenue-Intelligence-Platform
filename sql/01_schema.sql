CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id BIGINT PRIMARY KEY,
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
    churn INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_plan (
    plan_id VARCHAR(20) PRIMARY KEY,
    plan_name VARCHAR(100),
    plan_type VARCHAR(50),
    monthly_fee NUMERIC(12,2),
    data_limit_gb NUMERIC(12,2),
    voice_limit_minutes NUMERIC(12,2),
    sms_limit INTEGER,
    contract_type VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id DATE PRIMARY KEY,
    year_number INTEGER,
    month_number INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    day_number INTEGER,
    is_month_end BOOLEAN
);

CREATE TABLE IF NOT EXISTS dim_region (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(50),
    country_name VARCHAR(50) DEFAULT 'US',
    service_quality_score NUMERIC(5,2)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES dim_customer(customer_id),
    transaction_date DATE,
    transaction_type VARCHAR(50),
    amount NUMERIC(12,2),
    payment_status VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS fact_usage (
    usage_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES dim_customer(customer_id),
    usage_date DATE,
    data_used_gb NUMERIC(12,2),
    voice_minutes NUMERIC(12,2),
    sms_count NUMERIC(12,2),
    roaming_minutes NUMERIC(12,2)
);

CREATE TABLE IF NOT EXISTS fact_complaints (
    complaint_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES dim_customer(customer_id),
    complaint_date DATE,
    category VARCHAR(50),
    resolution_time_hours INTEGER,
    status VARCHAR(30),
    severity VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS fact_payments (
    payment_id BIGINT PRIMARY KEY,
    customer_id BIGINT REFERENCES dim_customer(customer_id),
    payment_date DATE,
    amount NUMERIC(12,2),
    payment_method VARCHAR(30),
    payment_status VARCHAR(30),
    days_late INTEGER
);
