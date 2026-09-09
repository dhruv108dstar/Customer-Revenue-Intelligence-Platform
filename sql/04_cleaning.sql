WITH duplicate_customers AS (
    SELECT customer_id
    FROM dim_customer
    GROUP BY customer_id
    HAVING COUNT(*) > 1
)
SELECT * FROM duplicate_customers;

WITH orphan_tx AS (
    SELECT t.transaction_id
    FROM fact_transactions t
    LEFT JOIN dim_customer c ON c.customer_id = t.customer_id
    WHERE c.customer_id IS NULL
)
SELECT * FROM orphan_tx;

SELECT COUNT(*) AS invalid_negative_amounts
FROM fact_transactions
WHERE amount < 0;
