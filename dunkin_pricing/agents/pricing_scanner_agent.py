from typing import Optional, List, Dict
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import OpenAI
from agents.agent import Agent

load_dotenv(override=True)

MODEL = "gpt-5.1"

SYSTEM_PROMPT = """You extract coffee prices from webpage text for a market research project.
Only report a price if it is EXPLICITLY stated as a dollar amount in the text for that specific drink.
Never guess, estimate, round, or infer a price from unrelated numbers on the page.
If no clear price is stated for a drink, leave that field null.
Look specifically for two things: (1) a standard hot brewed coffee (any size - report the size you found),
and (2) a standard hot latte (any size - report the size you found). Ignore iced, flavored, or seasonal
variants unless no plain version is listed."""


class CoffeePricing(BaseModel):
    hot_coffee_price: Optional[float] = Field(
        default=None, description="Price in USD of a hot brewed coffee, or null if not explicitly stated"
    )
    hot_coffee_size: Optional[str] = Field(
        default=None, description="Size described for the hot coffee price, e.g. 'medium', '12oz'"
    )
    latte_price: Optional[float] = Field(
        default=None, description="Price in USD of a hot latte, or null if not explicitly stated"
    )
    latte_size: Optional[str] = Field(
        default=None, description="Size described for the latte price, e.g. 'medium', '12oz'"
    )
    found: bool = Field(description="True only if at least one price was explicitly found in the text")
    notes: Optional[str] = Field(default=None, description="Anything notable, e.g. 'menu has no prices listed'")


class PricingScannerAgent(Agent):
    name = "Pricing Scanner Agent"
    color = Agent.CYAN
    MODEL = MODEL

    def __init__(self):
        self.log("Pricing Scanner Agent is initializing")
        self.openai = OpenAI()
        self.log("Pricing Scanner Agent is ready")

    def fetch_text(self, url: str) -> Optional[str]:
        """
        Fetch a page and return its visible text, or None if it couldn't be fetched.
        """
        try:
            response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
        except requests.RequestException as e:
            self.log(f"Could not fetch {url}: {e}")
            return None
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:8000]

    def extract(self, vendor: str, url: str) -> CoffeePricing:
        """
        Fetch a vendor's page and ask the model to extract hot coffee / latte prices,
        with instructions to never guess a price that isn't explicitly on the page.
        """
        text = self.fetch_text(url)
        if not text:
            return CoffeePricing(found=False, notes="Page could not be fetched")
        self.log(f"Extracting prices for {vendor} from {url}")
        response = self.openai.chat.completions.parse(
            model=self.MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Vendor: {vendor}\n\nWebpage text:\n{text}"},
            ],
            response_format=CoffeePricing,
        )
        result = response.choices[0].message.parsed
        self.log(
            f"{vendor}: found={result.found} hot_coffee={result.hot_coffee_price} latte={result.latte_price}"
        )
        return result

    def scan(self, vendors: Dict[str, Optional[str]]) -> List[dict]:
        """
        vendors: dict of {vendor_name: url_or_None}
        Returns a list of row dicts ready to merge into the pricing CSV.
        Vendors with no URL are returned as a row flagged for manual entry.
        """
        rows = []
        for vendor, url in vendors.items():
            if not url:
                rows.append(
                    {"vendor": vendor, "url": None, "found": False, "notes": "No URL - needs manual entry"}
                )
                continue
            result = self.extract(vendor, url)
            rows.append({"vendor": vendor, "url": url, **result.model_dump()})
        return rows
