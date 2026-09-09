# Data Quality Report

## Summary

This project measures completeness, validity, uniqueness, consistency, and referential integrity for the synthetic telecom dataset.

## Key Metrics

- Customers: 50,000
- Transactions: 1,000,000
- Usage records: 1,000,000
- Complaints: 100,000
- Payments: 500,000
- Overall quality score: tracked in the ETL validation layer

Latest local ETL run:

- Customers: 50,000 records, 0% duplicate rate, 0% missing rate
- Plans: 15 records, 0% duplicate rate, 0% missing rate
- Transactions: 1,000,000 records, 0% duplicate rate, 0% missing rate
- Usage: 1,000,000 records, 0% duplicate rate, 0% missing rate
- Complaints: 100,000 records, 0% duplicate rate, 0% missing rate
- Payments: 500,000 records, 0% duplicate rate, 0% missing rate
- Orphan customer references: 0 across all fact datasets

## Validation checks

- Missing values by table
- Duplicate record rate
- Invalid transaction amounts
- Orphan customer references
- Future date checks
- Revenue reconciliation

The PostgreSQL quality summary table is populated during the warehouse load. The latest local run completed extraction, cleaning, and validation before stopping at PostgreSQL authentication.
