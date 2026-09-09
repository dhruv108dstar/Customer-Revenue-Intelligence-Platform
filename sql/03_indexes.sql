CREATE INDEX IF NOT EXISTS idx_dim_customer_region ON dim_customer(region);
CREATE INDEX IF NOT EXISTS idx_dim_customer_plan ON dim_customer(plan_id);
CREATE INDEX IF NOT EXISTS idx_dim_customer_signup ON dim_customer(signup_date);

CREATE INDEX IF NOT EXISTS idx_fact_transactions_customer ON fact_transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_transactions_date ON fact_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_fact_usage_customer ON fact_usage(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_usage_date ON fact_usage(usage_date);
CREATE INDEX IF NOT EXISTS idx_fact_complaints_customer ON fact_complaints(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_complaints_date ON fact_complaints(complaint_date);
CREATE INDEX IF NOT EXISTS idx_fact_payments_customer ON fact_payments(customer_id);
CREATE INDEX IF NOT EXISTS idx_fact_payments_date ON fact_payments(payment_date);
