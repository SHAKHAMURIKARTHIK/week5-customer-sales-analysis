# Week 5: Advanced Data Manipulation with Pandas
## Project: Customer Sales Analysis

A simple, documented Python project for Developer Arena Week 5. It explores customer purchasing patterns and sales performance using Pandas, with a supplementary churn dataset.

### Project deliverables
- `main.py` — runnable end-to-end script
- `customer_analysis.ipynb` — beginner-friendly stepwise notebook
- `data/sales_data.csv` — supplied sales dataset (100 rows)
- `data/customer_churn.csv` — supplied churn dataset (500 rows)
- `outputs/` — aggregated CSV summaries, pivot table, filters, and merge output
- `visualizations/` — product, monthly, region, churn, and pivot charts
- `reports/analysis_report.pdf` — analysis report with insights and visuals
- `requirements.txt` — dependencies

### Install and run (VS Code)
1. Open this folder in VS Code.
2. Select a regular Python interpreter (avoid free-threaded interpreter if packages cannot install).
3. Terminal → New Terminal:
   ```powershell
   python -m pip install -r requirements.txt
   python main.py
   ```
4. View chart PNGs by expanding `visualizations/` in VS Code Explorer and double-clicking a chart.

### Week 5 topics implemented
- `groupby()` with sum, mean, and count aggregations
- AND / OR filtering and `isin`
- `.str.strip()`, `.str.title()`, `.str.replace()` text operations
- `pd.to_datetime()` and `.dt.year`, `.dt.month`, `.dt.day`
- `merge()` using a crosswalk and customer dataset
- `pd.pivot_table()` for Region × Product sales summary

### Data linkage caution
The sales data key format is `CUST###`; churn data key format is `C#####`. They do not share an exact matching customer ID. The project includes a sequence-based crosswalk solely to demonstrate merge/join mechanics. **This is not a verified customer identity match and should not be used for real customer decisions.** The churn rate and churn profile are separately calculated from the churn dataset.

### Current dataset findings
- Sales records analyzed: 100
- Total sales: 12,365,048.00
- Average sales per record: 123,650.48
- Highest sales product: Laptop — 3,889,210.00
- Highest sales region: North — 3,983,635.00
- Highest sales month: 2024-03 — 4,485,006.00
- Churn dataset churn rate: 10.60%

### Limitations
Sales data contains 100 distinct customer IDs with one sales row each; this dataset alone cannot establish repeat purchases or customer retention. The churn data is a separate synthetic/practice dataset. Sales value is not profit because cost and returns are unavailable.
