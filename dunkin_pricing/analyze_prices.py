"""
Build the competitor pricing comparison chart and summary table for the 9/24
preliminary market analysis presentation, from data/competitor_prices.csv.

Run after run_scan.py and after filling in any manual entries:
    uv run python analyze_prices.py
"""

import pandas as pd
import plotly.graph_objects as go

CSV_PATH = "data/competitor_prices.csv"
OUTPUT_HTML = "data/competitor_pricing_chart.html"


def load_priced_rows() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    priced = df[df["hot_coffee_price"].notna() | df["latte_price"].notna()].copy()
    missing = df[df["hot_coffee_price"].isna() & df["latte_price"].isna()]
    if not missing.empty:
        print("Still missing a price (needs manual entry before the chart is complete):")
        for vendor in missing["vendor"]:
            print(f"  - {vendor}")
        print()
    return priced


def chart(df: pd.DataFrame):
    df = df.sort_values("hot_coffee_price")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=df["vendor"], y=df["hot_coffee_price"], name="Hot Coffee", marker_color="firebrick")
    )
    fig.add_trace(go.Bar(x=df["vendor"], y=df["latte_price"], name="Latte", marker_color="deepskyblue"))
    fig.update_layout(
        title="Coffee Pricing Comparison - Rochester Campus Area",
        xaxis_title="Vendor",
        yaxis_title="Price ($)",
        barmode="group",
        template="plotly_white",
        width=1000,
        height=600,
    )
    fig.write_html(OUTPUT_HTML)
    print(f"Chart saved to {OUTPUT_HTML} - open it in a browser and screenshot for slides")
    fig.show()


def summary(df: pd.DataFrame):
    print("Summary by category:")
    print(df.groupby("category")[["hot_coffee_price", "latte_price"]].mean().round(2))
    print()
    print("Summary by campus:")
    print(df.groupby("campus")[["hot_coffee_price", "latte_price"]].mean().round(2))

    dunkin_row = df[df["vendor"].str.contains("Dunkin", case=False)]
    if not dunkin_row.empty and pd.notna(dunkin_row.iloc[0]["hot_coffee_price"]):
        dunkin_price = dunkin_row.iloc[0]["hot_coffee_price"]
        print(f"\nHot coffee price gap vs Dunkin' (${dunkin_price:.2f}):")
        gap = df.copy()
        gap["gap_vs_dunkin"] = gap["hot_coffee_price"] - dunkin_price
        print(gap[["vendor", "hot_coffee_price", "gap_vs_dunkin"]].dropna().to_string(index=False))


def main():
    df = load_priced_rows()
    if df.empty:
        print("No prices available yet - run run_scan.py and/or fill in manual entries first.")
        return
    summary(df)
    chart(df)


if __name__ == "__main__":
    main()
