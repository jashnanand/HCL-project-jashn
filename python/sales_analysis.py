"""Sales data cleaning and analysis."""
from pathlib import Path
import argparse
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def clean_data(df):
    needed = ["Row ID", "Order ID", "Order Date", "Ship Date", "Region", "Category",
              "Sub-Category", "Product Name", "Sales", "Quantity", "Discount", "Profit"]
    missing = [col for col in needed if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    checks = [
        ("Rows before cleaning", len(df)),
        ("Duplicate Row ID", int(df.duplicated("Row ID").sum())),
        ("Missing values", int(df.isna().sum().sum()))
    ]
    data = df.copy()
    data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
    data["Ship Date"] = pd.to_datetime(data["Ship Date"], errors="coerce")
    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    checks += [
        ("Invalid Order Date", int(data["Order Date"].isna().sum())),
        ("Negative Sales", int((data["Sales"] < 0).sum()))
    ]
    data = data.drop_duplicates("Row ID")
    data = data.dropna(subset=["Order Date", "Sales", "Profit", "Quantity"])
    for col in ["Region", "Category", "Sub-Category"]:
        data[col] = data[col].fillna("Unknown")
    data["Order Year"] = data["Order Date"].dt.year
    data["Order Month"] = data["Order Date"].dt.to_period("M").astype(str)
    data["Order Quarter"] = data["Order Date"].dt.to_period("Q").astype(str)
    data["Shipping Days"] = (data["Ship Date"] - data["Order Date"]).dt.days
    checks.append(("Rows after cleaning", len(data)))
    return data, pd.DataFrame(checks, columns=["Check", "Count"])


def make_reports(data, output):
    output.mkdir(parents=True, exist_ok=True)
    sales = data["Sales"].sum()
    profit = data["Profit"].sum()
    orders = data["Order ID"].nunique()
    kpis = pd.DataFrame([
        ["Total Sales", sales],
        ["Total Profit", profit],
        ["Total Orders", orders],
        ["Units Sold", data["Quantity"].sum()],
        ["Average Order Value", sales / orders if orders else 0],
        ["Profit Margin", profit / sales if sales else 0]
    ], columns=["KPI", "Value"])

    reports = {
        "KPI_Summary": kpis,
        "Monthly_Sales": data.groupby("Order Month", as_index=False).agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")),
        "Regional_Sales": data.groupby("Region", as_index=False).agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique")),
        "Top_Products": data.groupby(["Product Name", "Category", "Sub-Category"], as_index=False).agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum")),
        "Category_Summary": data.groupby("Category", as_index=False).agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum")),
        "Segment_Summary": data.groupby("Segment", as_index=False).agg(
            Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
    }
    reports["Top_Products"] = reports["Top_Products"].sort_values("Sales", ascending=False)
    for name, table in reports.items():
        table.to_csv(output / f"{name}.csv", index=False)

    with pd.ExcelWriter(output / "Sales_Analysis_Output.xlsx", engine="openpyxl") as writer:
        data.to_excel(writer, sheet_name="Cleaned_Data", index=False)
        for name, table in reports.items():
            table.to_excel(writer, sheet_name=name[:31], index=False)
    return reports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(ROOT / "data" / "Sample - Superstore.csv"))
    parser.add_argument("--output", default=str(ROOT / "outputs"))
    args = parser.parse_args()
    source = Path(args.input)
    if not source.exists():
        raise FileNotFoundError(f"Dataset not found: {source}")

    raw = pd.read_csv(source, encoding="latin-1")
    clean, quality = clean_data(raw)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    quality.to_csv(output / "Data_Quality_Report.csv", index=False)
    make_reports(clean, output)
    print(f"Rows: {len(raw)} -> {len(clean)}")
    print(f"Total Sales: {clean['Sales'].sum():,.2f}")
    print(f"Total Profit: {clean['Profit'].sum():,.2f}")
    print(f"Orders: {clean['Order ID'].nunique():,}")
    print(f"Saved to: {output.resolve()}")


if __name__ == "__main__":
    main()