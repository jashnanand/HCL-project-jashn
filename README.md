# Sales Performance Dashboard — HCL Career Shaper Project 1

Retail and e-commerce analytics project using the Kaggle Sample - Superstore dataset.

## Dataset
Source: [Kaggle Superstore Dataset Final](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)

The supplied CSV contains 9,994 rows and 21 columns. Order dates parsed from the file span 2014-01-03 through 2017-12-30. The raw dataset is not committed here; download `Sample - Superstore.csv` from Kaggle and place it in `data/`.

## Verified Python results
Python was run against the supplied CSV:
- Source rows: 9,994; cleaned rows: 9,994
- Total sales: $2,297,200.86
- Total profit: $286,397.02
- Distinct orders: 5,009
- Units sold: 37,873
- Average order value: $458.61
- Profit margin: 12.47%

These are Python results only. Oracle and Power BI cross-tool reconciliation is still pending.

## Requirements
- Python/pandas cleaning and quality checks
- Oracle table, data load, GROUP BY, window functions and view
- Power BI dashboard with at least 5 KPIs, 3 slicers and product drill-through
- Top 10 products and monthly trend verified
- Sales reconciliation within 0.1%
- Data-quality report, insights, README and demo video

## Run Python
```bash
py -m pip install -r requirements.txt
py python/sales_analysis.py --input "data/Sample - Superstore.csv"
```

## Power BI
Install [Power BI Desktop](https://www.microsoft.com/en-us/download/details.aspx?id=58494), import the CSV, create measures from `powerbi/DAX_Measures.txt`, build the report and save `Sales_Performance_Dashboard.pbix`. Export a PDF preview for the HCL submission; PDF is static and does not replace PBIX.

## Oracle
Run `sql/sales_analysis_oracle.sql` after creating the table. See `sql/LOAD_INSTRUCTIONS.md` for CSV loading guidance. SQL has been prepared but not yet executed against Oracle.

## Current status
- Python script: executed successfully on the provided 9,994-row source.
- SQL: prepared; Oracle execution pending.
- Power BI: build instructions and DAX prepared; PBIX pending.
- GitHub repository: this repository.
- Demo video: storyboard pending recording.

See `docs/EXECUTION_STATUS.txt` for the honest task status.