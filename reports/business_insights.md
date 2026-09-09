# Business Insights

This report summarizes the current findings from the generated, validated, and locally scored telecom dataset.

## Revenue Insights

- Revenue concentration by plan and region
- Growth trends across months
- ARPU and segment-level performance
- The churn model scored 50,000 customers and estimates approximately $21.6M in monthly revenue at risk.
- Logistic regression was selected over random forest by ROC-AUC: 0.724 versus 0.584.

## Customer Insights

- High-value segments by CLV
- Churn-prone segments and payment behaviour
- Demographic and tenure patterns
- Premium Loyalists: 8,300 customers
- High-Value At Risk: 14,709 customers
- Growth Customers: 10,183 customers
- Budget Customers: 16,808 customers

## Retention Recommendations

- Target customers with high CLV + high churn probability
- Prioritize credit and payment support for late-paying segments
- Review network and support experience in underperforming regions

## Current Model Caveat

The current model is a baseline for portfolio demonstration. The random forest produced weak positive-class recall on this generated dataset, so retention decisions should use the logistic model and be recalibrated after PostgreSQL-backed feature validation.
