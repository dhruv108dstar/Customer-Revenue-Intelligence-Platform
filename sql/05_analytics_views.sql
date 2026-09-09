CREATE OR REPLACE VIEW analytics.customer_revenue_summary AS
SELECT
    c.customer_id,
    c.region,
    c.plan_id,
    p.plan_name,
    p.plan_type,
    c.tenure_months,
    COALESCE(SUM(t.amount), 0) AS total_revenue,
    COALESCE(AVG(t.amount), 0) AS avg_transaction_amount,
    COUNT(t.transaction_id) AS transaction_count,
    MAX(CASE WHEN t.payment_status = 'Late' THEN 1 ELSE 0 END) AS has_late_payment,
    c.churn
FROM dim_customer c
LEFT JOIN fact_transactions t ON t.customer_id = c.customer_id
LEFT JOIN dim_plan p ON p.plan_id = c.plan_id
GROUP BY c.customer_id, c.region, c.plan_id, p.plan_name, p.plan_type, c.tenure_months, c.churn;

CREATE OR REPLACE VIEW analytics.customer_usage_summary AS
SELECT
    c.customer_id,
    c.region,
    c.plan_id,
    SUM(u.data_used_gb) AS total_data_used_gb,
    SUM(u.voice_minutes) AS total_voice_minutes,
    SUM(u.sms_count) AS total_sms_count,
    COUNT(u.usage_id) AS usage_records,
    AVG(u.data_used_gb) AS avg_data_per_usage
FROM dim_customer c
LEFT JOIN fact_usage u ON u.customer_id = c.customer_id
GROUP BY c.customer_id, c.region, c.plan_id;

CREATE OR REPLACE VIEW analytics.customer_retention_score AS
SELECT
    c.customer_id,
    c.region,
    c.plan_id,
    c.tenure_months,
    c.churn,
    COALESCE(p.total_payments, 0) AS total_payments,
    COALESCE(p.late_payment_value, 0) AS late_payment_value,
    COALESCE(cp.complaint_count, 0) AS complaint_count
FROM dim_customer c
LEFT JOIN (
    SELECT
        customer_id,
        SUM(amount) AS total_payments,
        SUM(CASE WHEN payment_status = 'Late' THEN amount ELSE 0 END) AS late_payment_value
    FROM fact_payments
    GROUP BY customer_id
) p ON p.customer_id = c.customer_id
LEFT JOIN (
    SELECT customer_id, COUNT(*) AS complaint_count
    FROM fact_complaints
    GROUP BY customer_id
) cp ON cp.customer_id = c.customer_id;

CREATE OR REPLACE VIEW analytics.plan_performance AS
SELECT
    p.plan_id,
    p.plan_name,
    p.plan_type,
    COUNT(c.customer_id) AS customer_count,
    COALESCE(r.avg_transaction_amount, 0) AS avg_transaction_amount,
    COALESCE(r.total_revenue, 0) AS total_revenue,
    COALESCE(AVG(c.tenure_months), 0) AS avg_tenure_months
FROM dim_plan p
LEFT JOIN dim_customer c ON c.plan_id = p.plan_id
LEFT JOIN (
    SELECT
        c2.plan_id,
        AVG(t.amount) AS avg_transaction_amount,
        SUM(t.amount) AS total_revenue
    FROM dim_customer c2
    JOIN fact_transactions t ON t.customer_id = c2.customer_id
    GROUP BY c2.plan_id
) r ON r.plan_id = p.plan_id
GROUP BY p.plan_id, p.plan_name, p.plan_type, r.avg_transaction_amount, r.total_revenue;
