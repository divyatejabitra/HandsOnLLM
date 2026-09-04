"""
Run the Pricing Scenario Agent + Recommendation Agent to produce a provisional
pricing recommendation for a hypothetical Dunkin' campus store, from the
verified rows in data/competitor_prices.csv.

This is a hypothesis-generation tool for the 9/24 preliminary market analysis -
NOT a real elasticity estimate. Once survey data lands (after 10/19), this
should be replaced or checked against actual regression results.

Usage:
    uv run python run_recommendation.py
"""

import logging
import sys
import pandas as pd
from agents.pricing_scenario_agent import PricingScenarioAgent
from agents.recommendation_agent import RecommendationAgent

CSV_PATH = "data/competitor_prices.csv"
OUTPUT_PATH = "data/pricing_recommendation.md"

PERKS = [
    "Prior Simon research already found high consumer utility (4.2/5 on a Likert scale) for a campus Dunkin' - "
    "validated demand before committing capital.",
    "Dunkin's off-campus reference prices are cheaper than the on-campus Starbucks incumbent, so Dunkin' can win "
    "price-sensitive students without even discounting, and has room to test a 25-cent cut.",
    "River Campus concentrates a large, walkable population with predictable daily traffic (class changes, morning "
    "commute, finals-week study sessions) - lower customer acquisition cost than an off-campus location.",
    "Brand loyalty transfer: students from Dunkin'-heavy home regions already have the habit, no need to build "
    "awareness from zero.",
    "Daypart differentiation: Dunkin's speed/value/donut-and-coffee identity is a different niche than Starbucks' "
    "'third place' study-lounge positioning - could capture the 'grab and go between classes' segment.",
    "Being the only quick-service (non-espresso-bar) coffee chain on campus, rather than a second sit-down cafe.",
]

RISKS = [
    "Exclusive dining contracts: universities often have long-term exclusive foodservice agreements that could block "
    "Dunkin' from operating on campus at all, or restrict which payment systems it can accept - check this first.",
    "Meal-plan/campus-cash lock-in: if Dunkin' can't accept the university's dining dollars the way Starbucks/Peet's/"
    "Brew already do, students may default to whichever cafe is inside their prepaid plan regardless of price.",
    "Crowded competitive set: three incumbents (Starbucks, Peet's, Brew) already split the on-campus coffee wallet - "
    "a fourth entrant fights for share of a fixed population, not new demand.",
    "Campus retail space is typically leased through the university at a premium or on revenue-share terms that "
    "erode Dunkin's normally thin margins.",
    "Franchisee economics: a college calendar means several 'dead' months a year (breaks, summer) unlike a standard "
    "retail location - the unit economics need to work despite that.",
    "Cannibalization vs. incrementality is unproven: a lower campus price might just steal share from Starbucks/"
    "Peet's/Brew at lower margin per cup, rather than growing total coffee occasions.",
    "Brand-fit/perception risk is exactly what the original Simon research and this survey need to quantify - it's "
    "not yet known how Dunkin's identity is perceived relative to Starbucks in this specific student population.",
]


def init_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))
    root.addHandler(handler)


def load_inputs():
    df = pd.read_csv(CSV_PATH)
    dunkin = df[df["vendor"].str.contains("Dunkin", case=False)].iloc[0]
    if pd.isna(dunkin["hot_coffee_price"]) or pd.isna(dunkin["latte_price"]):
        raise ValueError("Dunkin' off-campus reference prices are missing from the CSV - fill those in first.")

    on_campus = df[(df["campus"] == "on-campus") & df["hot_coffee_price"].notna() & df["latte_price"].notna()]
    if on_campus.empty:
        raise ValueError(
            "No on-campus competitor prices are filled in yet - add at least one (Starbucks, Peet's, or Brew) "
            "to data/competitor_prices.csv before running this."
        )
    competitor_context = "\n".join(
        f"- {row.vendor}: hot coffee ${row.hot_coffee_price:.2f}, latte ${row.latte_price:.2f}"
        for row in on_campus.itertuples()
    )
    return dunkin["hot_coffee_price"], dunkin["latte_price"], competitor_context


def write_report(assessments, recommendation):
    lines = ["# Dunkin' Campus Pricing Recommendation (Provisional)", ""]
    lines.append(
        "_Hypothesis-generation tool for the 9/24 preliminary market analysis - not a measured elasticity "
        "estimate. Re-run or validate against real regression results once survey data lands after 10/19._"
    )
    lines.append("")
    lines.append("## Scenarios considered")
    for a in assessments:
        lines.append(f"### {a.label}")
        lines.append(f"- Hot coffee: ${a.hot_coffee_price:.2f} | Latte: ${a.latte_price:.2f}")
        lines.append(f"- Expected relative appeal: **{a.expected_relative_appeal}**")
        lines.append(f"- Rationale: {a.rationale}")
        lines.append(f"- Survey must confirm: {a.key_assumption_to_validate}")
        lines.append("")
    lines.append(f"## Recommendation: {recommendation.recommended_scenario}")
    lines.append(recommendation.summary)
    lines.append("")
    lines.append("**Supporting points:**")
    for p in recommendation.supporting_points:
        lines.append(f"- {p}")
    lines.append("")
    lines.append("**Risks to watch:**")
    for r in recommendation.risks_to_watch:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("**What the survey must confirm:**")
    for s in recommendation.what_the_survey_must_confirm:
        lines.append(f"- {s}")

    with open(OUTPUT_PATH, "w") as f:
        f.write("\n".join(lines))
    logging.info(f"Report saved to {OUTPUT_PATH}")


def main():
    init_logging()
    off_campus_hot_coffee, off_campus_latte, competitor_context = load_inputs()
    business_context = (
        "Prior Simon research found 4.2/5 Likert-scale utility for a campus Dunkin'. Key open question: "
        "whether Dunkin' can accept campus dining-dollar/meal-plan payment like the incumbents already do."
    )

    scenario_agent = PricingScenarioAgent()
    assessments = scenario_agent.run(off_campus_hot_coffee, off_campus_latte, competitor_context, business_context)

    recommendation_agent = RecommendationAgent()
    recommendation = recommendation_agent.recommend(assessments, PERKS, RISKS)

    write_report(assessments, recommendation)

    print("\n=== RECOMMENDATION ===")
    print(f"{recommendation.recommended_scenario}\n")
    print(recommendation.summary)


if __name__ == "__main__":
    main()
