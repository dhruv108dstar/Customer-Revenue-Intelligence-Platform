# Customer & Revenue Intelligence Platform

A production-style telecom analytics platform designed to demonstrate end-to-end data engineering, analytics, and machine learning skills for a customer intelligence / BI consulting portfolio.

## Business Problem

Telecom businesses need to understand revenue quality, customer value, churn risk, and data integrity across millions of customer interactions. This project simulates a realistic telecom analytics workload with synthetic data and a complete analytics pipeline from generation to dashboarding.

## Project Objective

The platform answers questions related to revenue growth, ARPU, customer value, churn, retention prioritization, customer segmentation, and data quality across a synthetic base of 50,000+ customers.

## Architecture

Raw synthetic data -> Python ETL -> validation -> PostgreSQL warehouse -> SQL analytics -> ML models -> Power BI dashboard

## Technology Stack

- Python
- Pandas, NumPy
- PostgreSQL + SQL
- Scikit-learn, XGBoost, SHAP
- Power BI + DAX
- Pytest
- SQLAlchemy / psycopg2

## Dataset Description

The project creates a synthetic telecom dataset with customer, plan, transaction, usage, complaint, and payment histories.

## ETL Process

- Extract from generated source files
- Transform using business rules and validation checks
- Load into PostgreSQL warehouse tables
- Build analytics views for Power BI

## Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
cp .env.example .env
```

## Run the Project

```bash
python generate_data.py
python main.py
python run_ml_pipeline.py
```

`python main.py` always extracts, transforms, validates, and writes cleaned CSVs to `data/processed`. It then loads the PostgreSQL star schema and creates the analytics views. PostgreSQL must be running and the credentials in `.env` must match the local server.

For a local PostgreSQL setup, create the database before running the pipeline:

```sql
CREATE DATABASE customer_revenue_intelligence;
```

Update `DATABASE_PASSWORD` in `.env` with the password configured for `DATABASE_USER`. Never commit `.env`.

The ML step can run from `data/processed` after ETL validation and writes customer scores, model comparison metrics, and a run summary to `reports/model_outputs`.

## Project Structure

```text
customer-revenue-intelligence/
├── data/
├── sql/
├── src/
├── notebooks/
├── powerbi/
├── reports/
├── tests/
├── generate_data.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
```

## Future Improvements

- Add CI/CD automation
- Add dbt transformation layer
- Add automated Power BI deployment
- Extend ML with uplift modeling
- Connect to real telecom datasets


