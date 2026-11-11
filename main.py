from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
CHART_DIR = BASE_DIR / "visualizations"
OUTPUT_DIR.mkdir(exist_ok=True)
CHART_DIR.mkdir(exist_ok=True)

def load_and_clean_sales():
    """Load sales data, normalize strings, parse dates, and filter invalid rows."""
    df = pd.read_csv(DATA_DIR / "sales_data.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for column in ["Product", "Region", "Customer_ID"]:
        df[column] = df[column].astype("string").str.strip()
    df["Product"] = df["Product"].str.title()
    df["Region"] = df["Region"].str.title()
    df["Customer_ID"] = df["Customer_ID"].str.upper()
    for column in ["Quantity", "Price", "Total_Sales"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=["Date", "Product", "Region", "Customer_ID",
                           "Quantity", "Price", "Total_Sales"])
    df = df[(df["Quantity"] > 0) & (df["Price"] >= 0) & (df["Total_Sales"] >= 0)]
    df = df.drop_duplicates()
    # Date parts and cleaned text fields
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df["Month_Label"] = df["Date"].dt.to_period("M").astype(str)
    df["Product_Clean"] = (df["Product"].str.replace(r"[^A-Za-z0-9 ]", "", regex=True)
                           .str.strip())
    return df

def main():
    sales = load_and_clean_sales()
    customers = pd.read_csv(DATA_DIR / "customer_churn.csv")
    customers["CustomerID"] = customers["CustomerID"].astype("string").str.strip().str.upper()

    # Aggregations (sum, mean, count) by product, region, month, and customer
    product_summary = sales.groupby("Product_Clean", as_index=False).agg(
        Total_Sales=("Total_Sales", "sum"),
        Quantity=("Quantity", "sum"),
        Average_Order=("Total_Sales", "mean"),
        Orders=("Customer_ID", "count"))
    region_summary = sales.groupby("Region", as_index=False).agg(
        Total_Sales=("Total_Sales", "sum"),
        Orders=("Customer_ID", "count"),
        Average_Sales=("Total_Sales", "mean"))
    monthly_summary = sales.groupby("Month_Label", as_index=False).agg(
        Monthly_Sales=("Total_Sales", "sum"),
        Orders=("Customer_ID", "count"),
        Quantity=("Quantity", "sum"))
    customer_summary = sales.groupby("Customer_ID", as_index=False).agg(
        Lifetime_Sales=("Total_Sales", "sum"),
        Order_Count=("Total_Sales", "count"),
        Total_Quantity=("Quantity", "sum")).sort_values("Lifetime_Sales", ascending=False)

    # Multiple-condition filters: AND and OR examples
    high_value_north = sales[(sales["Region"] == "North") & (sales["Total_Sales"] >= sales["Total_Sales"].median())]
    selected_products = sales[(sales["Product"].isin(["Laptop", "Phone"])) | (sales["Region"] == "West")]

    # Pivot table for category summary
    sales_pivot = pd.pivot_table(sales, index="Region", columns="Product_Clean",
        values="Total_Sales", aggfunc="sum", fill_value=0, margins=True, margins_name="Grand Total")

    # Dataset IDs do not share the same key pattern (CUST### vs C#####).
    # For this exercise, use a documented sequence crosswalk for a demonstration merge.
    # This is NOT a verified real-world customer identity match.
    sales_ids = sorted(sales["Customer_ID"].unique(),
                       key=lambda value: int("".join(ch for ch in value if ch.isdigit()) or 0))
    churn_ids = customers["CustomerID"].sort_values().reset_index(drop=True)
    count = min(len(sales_ids), len(churn_ids))
    crosswalk = pd.DataFrame({"Customer_ID": sales_ids[:count], "CustomerID": churn_ids.iloc[:count].values})
    merged = sales.merge(crosswalk, on="Customer_ID", how="left").merge(customers, on="CustomerID", how="left")

    churn_summary = customers.groupby("Churn", as_index=False).agg(
        Customers=("CustomerID", "count"),
        Average_Tenure=("Tenure", "mean"),
        Average_Monthly_Charges=("MonthlyCharges", "mean"),
        Total_Charges=("TotalCharges", "sum"))
    churn_rate = customers["Churn"].mean() * 100

    # Export all summary datasets
    exports = {
        "product_sales_summary.csv": product_summary,
        "region_sales_summary.csv": region_summary,
        "monthly_sales_summary.csv": monthly_summary,
        "customer_lifetime_sales.csv": customer_summary,
        "sales_pivot_table.csv": sales_pivot,
        "customer_id_crosswalk.csv": crosswalk,
        "merged_customer_sales.csv": merged,
        "churn_summary.csv": churn_summary,
        "filtered_north_high_value.csv": high_value_north,
        "filtered_laptop_phone_or_west.csv": selected_products,
    }
    for filename, data in exports.items():
        data.to_csv(OUTPUT_DIR / filename, index=True if filename == "sales_pivot_table.csv" else False)

    # Charts
    def save_chart(fig, filename):
        fig.tight_layout()
        fig.savefig(CHART_DIR / filename, dpi=160, bbox_inches="tight")
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(product_summary["Product_Clean"], product_summary["Total_Sales"])
    ax.set(title="Sales by Product", xlabel="Product", ylabel="Total Sales")
    ax.tick_params(axis="x", rotation=20)
    save_chart(fig, "sales_by_product.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(monthly_summary["Month_Label"], monthly_summary["Monthly_Sales"], marker="o")
    ax.set(title="Monthly Sales Trend", xlabel="Month", ylabel="Monthly Sales")
    ax.tick_params(axis="x", rotation=35)
    save_chart(fig, "monthly_sales_trend.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(region_summary["Region"], region_summary["Total_Sales"])
    ax.set(title="Sales by Region", xlabel="Region", ylabel="Total Sales")
    save_chart(fig, "sales_by_region.png")

    churn_counts = customers["Churn"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(["Not Churned (0)", "Churned (1)"],
           [churn_counts.get(0, 0), churn_counts.get(1, 0)])
    ax.set(title=f"Customer Churn Distribution (Rate: {churn_rate:.1f}%)", ylabel="Customers")
    save_chart(fig, "churn_distribution.png")

    pivot_plot = sales.pivot_table(index="Region", columns="Product_Clean",
                                   values="Total_Sales", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(pivot_plot.values, aspect="auto")
    ax.set_xticks(range(len(pivot_plot.columns)), labels=pivot_plot.columns)
    ax.set_yticks(range(len(pivot_plot.index)), labels=pivot_plot.index)
    ax.set_title("Pivot Summary: Sales by Region and Product")
    fig.colorbar(image, ax=ax, label="Total Sales")
    save_chart(fig, "region_product_pivot.png")

    print("\\n========== CUSTOMER SALES ANALYSIS SUMMARY ==========")
    print(f"Valid sales records      : {len(sales):,}")
    print(f"Total revenue            : {sales['Total_Sales'].sum():,.2f}")
    print(f"Average sales per record : {sales['Total_Sales'].mean():,.2f}")
    print(f"Top product              : {product_summary.sort_values('Total_Sales', ascending=False).iloc[0]['Product_Clean']}")
    print(f"Highest-sales region     : {region_summary.sort_values('Total_Sales', ascending=False).iloc[0]['Region']}")
    print(f"Strongest month          : {monthly_summary.sort_values('Monthly_Sales', ascending=False).iloc[0]['Month_Label']}")
    print(f"Top customer by sales    : {customer_summary.iloc[0]['Customer_ID']} ({customer_summary.iloc[0]['Lifetime_Sales']:,.2f})")
    print(f"Churn rate (churn dataset): {churn_rate:.2f}%")
    print("\\nCharts saved in: visualizations/")
    print("Summary CSVs saved in: outputs/")

if __name__ == "__main__":
    main()
