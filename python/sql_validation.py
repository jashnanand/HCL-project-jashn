from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "data" / "Sample - Superstore.csv"
output = ROOT / "outputs"
output.mkdir(exist_ok=True)

data = pd.read_csv(source, encoding="latin-1")
data["Order Date"] = pd.to_datetime(data["Order Date"], errors="coerce")
data["Ship Date"] = pd.to_datetime(data["Ship Date"], errors="coerce")
for col in ["Sales", "Profit", "Quantity", "Discount"]:
    data[col] = pd.to_numeric(data[col], errors="coerce")
data = data.drop_duplicates("Row ID").dropna(
    subset=["Order Date", "Sales", "Profit", "Quantity"]
)

db = sqlite3.connect(":memory:")
data.to_sql("FACT_SALES", db, index=False, if_exists="replace")
db.execute("""
CREATE TABLE DIM_CUSTOMER AS
SELECT "Customer ID" AS CUSTOMER_ID,
       MAX("Customer Name") AS CUSTOMER_NAME,
       MAX(Segment) AS SEGMENT
FROM FACT_SALES GROUP BY "Customer ID"
""")
db.execute("""
CREATE TABLE DIM_PRODUCT AS
SELECT "Product ID" AS PRODUCT_ID,
       MAX("Product Name") AS PRODUCT_NAME,
       MAX(Category) AS CATEGORY,
       MAX("Sub-Category") AS SUB_CATEGORY
FROM FACT_SALES GROUP BY "Product ID"
""")

kpis = pd.read_sql_query("""
SELECT COUNT(*) AS ROWS,
       COUNT(DISTINCT "Order ID") AS ORDERS,
       ROUND(SUM(Sales), 2) AS TOTAL_SALES,
       ROUND(SUM(Profit), 2) AS TOTAL_PROFIT,
       SUM(Quantity) AS UNITS
FROM FACT_SALES
""", db)
monthly = pd.read_sql_query("""
SELECT strftime('%Y-%m', "Order Date") AS SALES_MONTH,
       ROUND(SUM(Sales), 2) AS SALES,
       ROUND(SUM(Profit), 2) AS PROFIT,
       COUNT(DISTINCT "Order ID") AS ORDERS
FROM FACT_SALES
GROUP BY strftime('%Y-%m', "Order Date") ORDER BY SALES_MONTH
""", db)
region = pd.read_sql_query("""
SELECT Region, ROUND(SUM(Sales), 2) AS SALES,
       ROUND(SUM(Profit), 2) AS PROFIT
FROM FACT_SALES GROUP BY Region ORDER BY SALES DESC
""", db)
top10 = pd.read_sql_query("""
SELECT PRODUCT_NAME, CATEGORY, SALES, PROFIT, SALES_RANK
FROM (
  SELECT P.PRODUCT_NAME, P.CATEGORY,
         ROUND(SUM(F.Sales), 2) AS SALES,
         ROUND(SUM(F.Profit), 2) AS PROFIT,
         DENSE_RANK() OVER (ORDER BY SUM(F.Sales) DESC) AS SALES_RANK
  FROM FACT_SALES F
  JOIN DIM_PRODUCT P ON F."Product ID" = P.PRODUCT_ID
  GROUP BY P.PRODUCT_NAME, P.CATEGORY
)
WHERE SALES_RANK <= 10 ORDER BY SALES_RANK
""", db)
joined = pd.read_sql_query("""
SELECT C.SEGMENT, P.CATEGORY,
       ROUND(SUM(F.Sales), 2) AS SALES,
       ROUND(SUM(F.Profit), 2) AS PROFIT
FROM FACT_SALES F
JOIN DIM_CUSTOMER C ON F."Customer ID" = C.CUSTOMER_ID
JOIN DIM_PRODUCT P ON F."Product ID" = P.PRODUCT_ID
GROUP BY C.SEGMENT, P.CATEGORY
ORDER BY C.SEGMENT, SALES DESC
""", db)

for name, frame in {
    "SQL_Validation_KPIs": kpis,
    "SQL_Validation_Monthly": monthly,
    "SQL_Validation_Region": region,
    "SQL_Validation_Top10": top10,
    "SQL_Validation_Segment_Category": joined
}.items():
    frame.to_csv(output / f"{name}.csv", index=False)

r = kpis.iloc[0]
assert int(r["ROWS"]) == 9994
assert int(r["ORDERS"]) == 5009
assert round(r["TOTAL_SALES"], 2) == 2297200.86
assert round(r["TOTAL_PROFIT"], 2) == 286397.02
assert int(r["UNITS"]) == 37873
assert region.iloc[0]["Region"] == "West"
assert top10.iloc[0]["PRODUCT_NAME"] == "Canon imageCLASS 2200 Advanced Copier"

print("SQL checks passed in SQLite.")
print(kpis.to_string(index=False))
print("Customers:", db.execute("SELECT COUNT(*) FROM DIM_CUSTOMER").fetchone()[0])
print("Products:", db.execute("SELECT COUNT(*) FROM DIM_PRODUCT").fetchone()[0])
print("Top product:", top10.iloc[0]["PRODUCT_NAME"])
print("Oracle itself was not run.")
