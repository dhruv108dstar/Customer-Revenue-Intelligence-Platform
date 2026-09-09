# Power BI Semantic Model

## Data sources

Connect PostgreSQL to the `customer_revenue_intelligence` database and import:

- `dim_customer`
- `dim_plan`
- `dim_date`
- `dim_region`
- `fact_transactions`
- `fact_usage`
- `fact_complaints`
- `fact_payments`
- `analytics.customer_revenue_summary`
- `analytics.customer_usage_summary`
- `analytics.customer_retention_score`
- `analytics.plan_performance`
- `reports/model_outputs/customer_scores.csv` as `customer_scores`

## Relationships

- `dim_customer[customer_id]` 1-to-many `fact_transactions[customer_id]`
- `dim_customer[customer_id]` 1-to-many `fact_usage[customer_id]`
- `dim_customer[customer_id]` 1-to-many `fact_complaints[customer_id]`
- `dim_customer[customer_id]` 1-to-many `fact_payments[customer_id]`
- `dim_customer[customer_id]` 1-to-1 `customer_scores[customer_id]`
- `dim_plan[plan_id]` 1-to-many `dim_customer[plan_id]`
- `dim_date[date_id]` 1-to-many each fact date column
- `dim_region[region_name]` 1-to-many `dim_customer[region]`

Set `dim_date` as the date table using `date_id`.

## Dashboard pages

### 1. Executive Overview

Cards: Total Revenue, Customers, ARPU, Churn Rate, Revenue At Risk.
Charts: monthly revenue trend, revenue by plan type, customers by region.
Slicers: date, region, plan type.

### 2. Customer Intelligence

Charts: customer count by plan, tenure distribution, CLV by plan, usage by region.
Table: customer ID, plan, tenure, revenue, CLV, churn probability.

### 3. Churn and Retention

Cards: high-risk customers, retention-priority customers, churn rate.
Charts: churn by contract type, churn probability distribution, revenue at risk by region.
Table: highest-value customers requiring retention action.

### 4. Revenue Performance

Charts: month-over-month revenue, plan revenue contribution, transaction type mix, ARPU by region.
Table: plan performance with customer count, revenue, average transaction value, tenure.

### 5. Data Quality

Cards: row counts, missing rate, duplicate rate, orphan reference count.
Charts: quality score by table, validation issue category, reconciliation difference.

Use `powerbi/dax_measures.dax` for the measure definitions.
