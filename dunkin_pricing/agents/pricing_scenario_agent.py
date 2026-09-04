from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from agents.agent import Agent

load_dotenv(override=True)

MODEL = "gpt-5.1"

SYSTEM_PROMPT = """You are a pricing analyst helping a corporate client (Dunkin') evaluate whether and how to price a
proposed coffee shop on a college campus. No consumer survey data exists yet - you are building a hypothesis for a
preliminary market-analysis presentation, NOT a measured elasticity estimate. For the scenario given, reason only from
the stated competitive prices and stated business context. Never invent a numeric probability or dollar figure that
wasn't given to you. Always state, concretely, what the student survey needs to measure before this hypothesis can be
trusted."""


class ScenarioAssessment(BaseModel):
    label: str
    hot_coffee_price: float
    latte_price: float
    expected_relative_appeal: str = Field(
        description="'low', 'medium', or 'high' - expected purchase likelihood relative to on-campus incumbents, "
        "based only on price positioning. This is a hypothesis, not a measured probability."
    )
    rationale: str
    key_assumption_to_validate: str = Field(
        description="The specific thing the student survey must measure before this hypothesis can be trusted"
    )


class PricingScenarioAgent(Agent):
    name = "Pricing Scenario Agent"
    color = Agent.BLUE
    MODEL = MODEL

    def __init__(self):
        self.log("Pricing Scenario Agent is initializing")
        self.openai = OpenAI()
        self.log("Pricing Scenario Agent is ready")

    def assess(
        self, label: str, hot_coffee_price: float, latte_price: float, competitor_context: str, business_context: str
    ) -> ScenarioAssessment:
        user_prompt = f"""Scenario: {label}
Proposed Dunkin' on-campus price: hot coffee ${hot_coffee_price:.2f}, latte ${latte_price:.2f}

On-campus competitor prices:
{competitor_context}

Business context:
{business_context}

Assess this scenario's likely relative appeal to price-sensitive college students, based purely on price
positioning versus the incumbents above."""
        self.log(f"Assessing scenario: {label}")
        response = self.openai.chat.completions.parse(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format=ScenarioAssessment,
        )
        result = response.choices[0].message.parsed
        result.label = label  # keep the exact label we gave it - don't trust the model's paraphrase
        self.log(f"{label}: expected_relative_appeal={result.expected_relative_appeal}")
        return result

    def run(
        self, off_campus_hot_coffee: float, off_campus_latte: float, competitor_context: str, business_context: str
    ) -> List[ScenarioAssessment]:
        """
        Builds and assesses the three scenarios from the research design:
        a 25-cent discount, matching, and a 25-cent premium, all relative to the
        off-campus reference price.
        """
        scenarios = [
            ("25-cent discount vs off-campus", off_campus_hot_coffee - 0.25, off_campus_latte - 0.25),
            ("Match off-campus price", off_campus_hot_coffee, off_campus_latte),
            ("25-cent premium vs off-campus", off_campus_hot_coffee + 0.25, off_campus_latte + 0.25),
        ]
        return [
            self.assess(label, hot_coffee_price, latte_price, competitor_context, business_context)
            for label, hot_coffee_price, latte_price in scenarios
        ]
