"""
Seed list of coffee competitors relevant to the MKT465 Dunkin' campus pricing project,
for benchmarking hot coffee / latte prices around University of Rochester's River Campus.

Where a URL is given, the Pricing Scanner Agent will try to extract a real price from it.
Where it's None, no public price page was found (confirmed for on-campus dining and the
independent local shops below) - collect that one manually (in person, a receipt, or the
vendor's ordering app) and enter it directly into data/competitor_prices.csv.

The two "national reference" entries pull from third-party menu-aggregator sites, NOT
Rochester-specific data - treat them as a sanity-check baseline only, and verify against
an actual local receipt before using the number in a presentation.
"""

COMPETITORS = {
    # Off-campus reference point and on-campus incumbents are the core of the pricing
    # research question, and are now filled in with team-verified estimates in the CSV
    # (see data/competitor_prices.csv, verified=True) rather than scraped - the official
    # sites/dining.rochester.edu confirmed to have no public price pages.
    "Dunkin' (off-campus reference)": None,
    "Starbucks - Wilson Commons": None,
    "Peet's Coffee - Wegmans Hall": None,
    "Brew (on-campus)": None,
    # Off campus / near River Campus - no confirmed price page found; verify URL if the
    # shop has one, otherwise collect in person
    "Equal Grounds": None,
    "Java's": None,
    "Ugly Duck Coffee": None,
    "Layali Coffeehouse": None,
    "Winter Swan Coffee": None,
    "Albunn Coffee House": None,
    "Mercury Coffee": None,
}
