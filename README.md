# Sales Performance Dashboard

**HCL Career Shaper - Project 1**

This project looks at sales, profit, orders, products and regions using the Sample Superstore data.

## Dataset

Get the CSV from [Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) and save it in the `data` folder as `Sample - Superstore.csv`.

The file used for the Python analysis had 9,994 rows and 21 columns.

## Python results

- Total sales: $2,297,200.86
- Total profit: $286,397.02
- Orders: 5,009
- Units sold: 37,873
- Average order value: $458.61
- Profit margin: 12.47%

## Run the Python file

```bash
py -m pip install -r requirements.txt
py python/sales_analysis.py --input "data/Sample - Superstore.csv"
```

The results are saved in the `outputs` folder.

## Power BI

Use `powerbi/DAX_Measures.txt` for the measures. Add cards for the main KPIs, a monthly sales chart, a region chart and a Top 10 products chart. Add Year, Region and Category slicers. Save the report as a PBIX file.

## Oracle

Create the table and run the queries in `sql/sales_analysis_oracle.sql`. See `sql/LOAD_INSTRUCTIONS.md` for loading the CSV.

## Current work

Python was run on the dataset. Oracle and the Power BI report still need to be run and checked. The dashboard preview is a picture/PDF, not the interactive PBIX file.