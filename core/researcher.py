from serpapi import GoogleSearch
from dotenv import load_dotenv
from core.lead import Lead
import os
import re

load_dotenv()


class Researcher:

    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY')

    def find_leads(self, niche: str, location: str, num_results: int = 10) -> list:
        query = f"{niche} companies in {location} contact CEO founder"
        print(f"Searching: {query}")

        params = {
            "engine": "google",
            "q": query,
            "num": num_results,
            "api_key": self.api_key
        }

        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            leads = []
            organic = results.get("organic_results", [])

            for result in organic:
                lead = self._parse_result(result, niche)
                if lead:
                    leads.append(lead)

            print(f"Found {len(leads)} leads from search")
            return leads

        except Exception as e:
            print(f"Research error: {e}")
            return []

    def _parse_result(self, result: dict, niche: str) -> Lead:
        try:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")

            skip_domains = ["wikipedia", "linkedin.com/jobs", "indeed", "glassdoor", "yelp"]
            if any(skip in link.lower() for skip in skip_domains):
                return None

            company_name = re.split(r'[-|]', title)[0].strip()

            if not company_name:
                return None

            lead = Lead(
                name=f"Decision maker at {company_name}",
                company=company_name,
                industry=niche,
                website=link
            )

            if snippet:
                lead.add_note(snippet[:200])

            return lead

        except Exception:
            return None