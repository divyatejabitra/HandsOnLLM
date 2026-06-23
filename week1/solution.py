"""
Day 2 challenge: Upgrade the Day 1 website summarizer to use a local Ollama model
instead of the paid OpenAI API.

Usage:
    uv run week1/solution.py <url>
    uv run week1/solution.py  # prompts for URL
"""

import sys
import requests
from openai import OpenAI
from scraper import fetch_website_contents

OLLAMA_BASE_URL = "http://localhost:11434/v1"
MODEL = "llama3.2"

system_prompt = """
You are a snarky assistant that analyzes the contents of a website,
and provides a short, snarky, humorous summary, ignoring text that might be navigation related.
Respond in markdown. Do not wrap the markdown in a code block - respond just with the markdown.
"""

user_prompt_prefix = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.

"""


def check_ollama():
    try:
        resp = requests.get("http://localhost:11434", timeout=3)
        return b"Ollama" in resp.content
    except requests.ConnectionError:
        return False


def messages_for(website_text):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_prefix + website_text},
    ]


def summarize(url):
    ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    website_text = fetch_website_contents(url)
    response = ollama.chat.completions.create(
        model=MODEL,
        messages=messages_for(website_text),
    )
    return response.choices[0].message.content


def main():
    if not check_ollama():
        print("Error: Ollama is not running. Start it with: ollama serve")
        sys.exit(1)

    url = sys.argv[1] if len(sys.argv) > 1 else input("Enter a URL to summarize: ").strip()
    if not url:
        print("Error: no URL provided.")
        sys.exit(1)

    print(f"\nSummarizing {url} using {MODEL} via Ollama...\n")
    print(summarize(url))


if __name__ == "__main__":
    main()
