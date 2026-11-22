"""Sales Performance Dashboard ETL and analysis.
Run: py python/sales_analysis.py --input "data/Sample - Superstore.csv"
Install: py -m pip install -r requirements.txt
"""
from pathlib import Path
import argparse
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

def clean_data(df):
    required = ["Row ID","Order ID","Order Date","Ship Date","Region","Category",
                "Sub-Category","Product Name","Sales","Quantity","Discount","Profit"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    checks = [
        ("Rows before cleaning", len(df)),
        ("Duplicate Row ID", int(df.duplicated("Row ID").sum())),
        ("Missing values (all cells)", int(df.isna().sum().sum()))
    ]
    x = df.copy()
    x["Order Date"] = pd.to_datetime(x["Order Date"], errors="coerce")
    x["Ship Date"] = pd.to_datetime(x["Ship Date"], errors="coerce")
    for c in ["Sales","Profit","Quantity","Discount"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    checks += [
        ("Invalid Order Date", int(x["Order Date"].isna().sum())),
        ("Negative Sales rows", int((x["Sales"] < 0).sum()))
    ]
    x = x.drop_duplicates("Row ID", keep="first")
    x = x.dropna(subset=["Order Date","Sales","Profit","Quantity"])
    for c in ["Region","Category","Sub-Category"]:
        x[c] = x[c].fillna("Unknown")
    x["Order Year"] = x["Order Date"].dt.year
    x["Order Month"] = x["Order Date"].dt.to_period("M").astype(str)
    x["Order Quarter"] = x["Order Date"].dt.to_period("Q").astype(str)
    x["Shipping Days"] = (x["Ship Date"] - x["Order Date"]).dt.days
    checks.append(("Rows after cleaning", len(x)))
    return x, pd.DataFrame(checks, columns=["Check","Count"])

def analyze(df, out):
    out.mkdir(parents=True, exist_ok=True)
    orders = df["Order ID"].nunique()
    sales, profit = df["Sales"].sum(), df["Profit"].sum()
    kpis = pd.DataFrame([
        ["Total Sales", sales, "SUM(Sales)"],
        ["Total Profit", profit, "SUM(Profit)"],
        ["Total Orders", orders, "DISTINCTCOUNT(Order ID)"],
        ["Units Sold", df["Quantity"].sum(), "SUM(Quantity)"],
        ["Average Order Value", sales/orders if orders else 0, "Sales / distinct orders"],
        ["Profit Margin", profit/sales if sales else 0, "Profit / Sales"]
    ], columns=["KPI","Value","Definition"])
    monthly = df.groupby("Order Month", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
    region = df.groupby("Region", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
    products = df.groupby(["Product Name","Category","Sub-Category"], as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum")).sort_values("Sales", ascending=False)
    category = df.groupby("Category", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum"))
    segment = df.groupby("Segment", as_index=False).agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order ID","nunique"))
    tables = {"KPI_Summary":kpis,"Monthly_Sales":monthly,"Regional_Sales":region,
              "Top_Products":products,"Category_Summary":category,"Segment_Summary":segment}
    for name, table in tables.items():
        table.to_csv(out/f"{name}.csv", index=False)
    with pd.ExcelWriter(out/"Sales_Analysis_Output.xlsx", engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)
        for name, table in tables.items():
            table.to_excel(writer, sheet_name=name[:31], index=False)
    return kpis, monthly, region, products

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=str(ROOT/"data"/"Sample - Superstore.csv"))
    p.add_argument("--output", default=str(ROOT/"outputs"))
    a = p.parse_args()
    source = Path(a.input)
    if not source.exists():
        raise FileNotFoundError(f"Dataset not found: {source}. Download Sample - Superstore.csv from Kaggle.")
    raw = pd.read_csv(source, encoding="latin-1")
    cleaned, quality = clean_data(raw)
    Path(a.output).mkdir(parents=True, exist_ok=True)
    quality.to_csv(Path(a.output)/"Data_Quality_Report.csv", index=False)
    kpis, monthly, region, products = analyze(cleaned, Path(a.output))
    print(f"Rows: {len(raw)} -> {len(cleaned)}")
    print(kpis.to_string(index=False))
    print(f"Top product: {products.iloc[0]['Product Name']}")
if __name__ == "__main__":
    main()