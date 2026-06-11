from serpapi import GoogleSearch
from dotenv import load_dotenv
from core.lead import Lead
import os
import re

load_dotenv()


class Researcher:
    """
    Finds real leads from the internet using Google Search.

    SOLID — Single Responsibility: this class only finds leads.
    It doesn't score them, doesn't write emails. Just finds.

    No abstract base class here — there's only one way to
    research leads right now. We'll add abstraction later
    if we add LinkedIn or other sources. Don't over-engineer
    before you need to. This is called YAGNI:
    You Ain't Gonna Need It.
    """

    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY')

    def find_leads(self, niche: str, location: str, num_results: int = 10) -> list:
        """
        Searches Google for companies matching the niche and location.
        Returns a list of Lead objects.

        How it works:
        1. Build a smart search query
        2. Send it to Google via SerpAPI
        3. Parse each result into a Lead object
        4. Return the list
        """

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

            # organic_results is the list of normal Google results
            # (not ads). Each result is a dictionary with keys:
            # 'title', 'link', 'snippet'
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
        """
        Converts one Google search result into a Lead object.

        The underscore prefix _parse_result signals this is a
        PRIVATE method — only used internally by this class.
        Python convention, not enforced. Same idea as Java's private.

        We extract what we can from the title and snippet.
        It won't be perfect — real scraping never is.
        That's why we have the AI scorer to evaluate quality.
        """
        try:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")

            # Skip results that are clearly not companies
            # (directories, Wikipedia, news articles)
            skip_domains = ["wikipedia", "linkedin.com/jobs", "indeed", "glassdoor", "yelp"]
            if any(skip in link.lower() for skip in skip_domains):
                return None

            # Extract company name from title
            # Google titles often look like "CompanyName - Product | Tagline"
            # We take the part before the first dash or pipe
            company_name = re.split(r'[-|]', title)[0].strip()

            if not company_name:
                return None

            # Build the lead with what we have
            lead = Lead(
                name=f"Decision maker at {company_name}",
                company=company_name,
                industry=niche,
                website=link
            )

            # Add the snippet as a note — useful context for the AI scorer
            if snippet:
                lead.add_note(snippet[:200])

            return lead

        except Exception:
            return None