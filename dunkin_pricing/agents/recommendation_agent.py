from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from agents.agent import Agent
from agents.pricing_scenario_agent import ScenarioAssessment

load_dotenv(override=True)

MODEL = "gpt-5.1"

SYSTEM_PROMPT = """You are advising Dunkin' corporate on whether and how to price a proposed campus coffee shop. You
will be given several pricing scenario assessments (hypotheses, not measured data) plus known business perks and
risks of opening on this campus. Recommend exactly ONE scenario, with concrete business/franchise-economics
reasoning tied to the perks and risks given. Explicitly and clearly flag the recommendation as provisional, pending
real student survey data."""


class Recommendation(BaseModel):
    recommended_scenario: str
    summary: str
    supporting_points: List[str]
    risks_to_watch: List[str]
    what_the_survey_must_confirm: List[str]


class RecommendationAgent(Agent):
    name = "Recommendation Agent"
    color = Agent.GREEN
    MODEL = MODEL

    def __init__(self):
        self.log("Recommendation Agent is initializing")
        self.openai = OpenAI()
        self.log("Recommendation Agent is ready")

    def recommend(
        self, assessments: List[ScenarioAssessment], perks: List[str], risks: List[str]
    ) -> Recommendation:
        scenario_text = "\n\n".join(
            f"- {a.label}: hot coffee ${a.hot_coffee_price:.2f}, latte ${a.latte_price:.2f}\n"
            f"  Expected relative appeal: {a.expected_relative_appeal}\n"
            f"  Rationale: {a.rationale}\n"
            f"  Needs validation: {a.key_assumption_to_validate}"
            for a in assessments
        )
        perks_text = "\n".join(f"- {p}" for p in perks)
        risks_text = "\n".join(f"- {r}" for r in risks)
        user_prompt = f"""Pricing scenarios under consideration:
{scenario_text}

Known perks of opening on campus:
{perks_text}

Known risks of opening on campus:
{risks_text}

Recommend ONE pricing scenario for Dunkin's campus store, and produce a client-ready summary."""
        self.log("Synthesizing recommendation")
        response = self.openai.chat.completions.parse(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=Recommendation,
        )
        result = response.choices[0].message.parsed
        self.log(f"Recommended: {result.recommended_scenario}")
        return result
