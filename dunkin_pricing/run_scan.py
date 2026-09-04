"""
Run the Pricing Scanner Agent over the competitors in competitors.py and update
data/competitor_prices.csv with whatever prices it can find.

Rows marked verified=True (i.e. you've manually confirmed a price - by visiting the
store, checking a receipt, or using the ordering app) are never overwritten by a rerun.
"""

import logging
import sys
import pandas as pd
from competitors import COMPETITORS
from agents.pricing_scanner_agent import PricingScannerAgent

CSV_PATH = "data/competitor_prices.csv"


def init_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))
    root.addHandler(handler)


def main():
    init_logging()
    df = pd.read_csv(CSV_PATH, dtype=str)
    df = df.set_index("vendor")

    agent = PricingScannerAgent()
    rows = agent.scan(COMPETITORS)

    for row in rows:
        vendor = row["vendor"]
        if vendor not in df.index:
            continue
        if str(df.loc[vendor, "verified"]).strip().lower() == "true":
            logging.info(f"Skipping '{vendor}' - already manually verified")
            continue
        for field in ["hot_coffee_price", "hot_coffee_size", "latte_price", "latte_size", "found", "notes"]:
            if field in row and row[field] is not None:
                df.loc[vendor, field] = row[field]

    df = df.reset_index()
    df.to_csv(CSV_PATH, index=False)
    logging.info(f"Updated {CSV_PATH}")
    logging.info(
        "Now open the CSV and fill in any row with found=False by hand "
        "(store visit, receipt, or ordering app), then set verified=True."
    )


if __name__ == "__main__":
    main()
