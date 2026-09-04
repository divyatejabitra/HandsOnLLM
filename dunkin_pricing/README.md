# Dunkin' Campus Pricing Analysis

Competitor pricing tool for the MKT465 Dunkin' capstone project (see the 9/24 preliminary
market analysis deliverable: current price structure at Dunkin' and its competitors in the
Rochester area, for regular hot coffee and lattes).

## What this does, and what it doesn't

Official chain sites (Dunkin', Starbucks) and the campus dining page do **not** publish
location-specific prices - confirmed by hand before building this. So this tool is a hybrid,
not a pure scraper:

- `agents/pricing_scanner_agent.py` fetches a page and asks an LLM to extract a hot-coffee
  and latte price, **only if a dollar amount is explicitly on the page** - it's instructed to
  never guess or round, and returns `found=False` rather than invent a number. It got the
  Starbucks Tall coffee/latte prices from a third-party menu-aggregator, but that page looks
  stale (its $1.75/$2.75 figures don't match current pricing) - **do not use scraped numbers
  in a presentation without verifying them against a receipt, the ordering app, or an in-store
  visit.**
- Everything else (on-campus Starbucks/Peet's, and every independent shop near River Campus)
  has no public price page at all - those rows need to be filled in by hand.

## Workflow

1. `uv run python run_scan.py` - fills in whatever prices are explicitly published online.
2. Open `data/competitor_prices.csv`. For every row with `found=False`, add the real price
   (visit the store, check a receipt, or check the vendor's ordering app), then set
   `verified=True` so future reruns of step 1 don't touch it.
3. `uv run python analyze_prices.py` - prints a summary (chain vs. independent, on- vs.
   off-campus averages, and the price gap vs. Dunkin') and writes
   `data/competitor_pricing_chart.html`, a grouped bar chart ready to screenshot into slides.

## Files

- `competitors.py` - the seed list of vendors and any known URL. Add more competitors here.
- `agents/pricing_scanner_agent.py` - the extraction agent.
- `data/competitor_prices.csv` - the working dataset (scraped + manual entries).
- `run_scan.py` - runs the scanner and updates the CSV.
- `analyze_prices.py` - builds the comparison chart and summary stats.

## Next: the elasticity phase (after 10/19)

This tool only covers the competitor-benchmarking deliverable. Once survey data comes back
(price-sensitivity responses by segment: undergrad / grad / employee / off-campus), that's a
separate, simpler analysis (regression on purchase likelihood vs. price by segment) - it
doesn't need this scraping/agent machinery, just the survey CSV and pandas/statsmodels.
