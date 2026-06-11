from serpapi import GoogleSearch
from dotenv import load_dotenv
from groq import Groq
from core.lead import Lead
import os
import re
import json

load_dotenv()


class Researcher:

    def __init__(self):
        self.api_key = os.getenv('SERPAPI_KEY')
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))

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
            organic = results.get("organic_results", [])

            # Pass ALL results to AI at once — one API call
            # instead of one per result. Faster and cheaper.
            leads = self._extract_companies_with_ai(organic, niche, location)

            print(f"Found {len(leads)} leads from search")
            return leads

        except Exception as e:
            print(f"Research error: {e}")
            return []

    def _extract_companies_with_ai(self, results: list, niche: str, location: str) -> list:
        """
        Sends all Google results to the AI in one shot.
        Asks it to extract REAL company names, not list titles.

        We ask for JSON back — structured data we can reliably parse.
        This is a common pattern when using LLMs as data extractors.
        """

        # Build a summary of all results for the AI to read
        results_text = ""
        for i, r in enumerate(results):
            results_text += f"""
Result {i+1}:
Title: {r.get('title', '')}
URL: {r.get('link', '')}
Snippet: {r.get('snippet', '')}
"""

        prompt = f"""You are a business researcher. Extract real company names from these Google search results.

I searched for: "{niche} companies in {location}"

Search results:
{results_text}

Instructions:
- Extract only REAL companies (not blog posts, list articles, or directories)
- For list articles like "Top 10 SaaS companies", extract the actual company names mentioned in the snippet
- Return a JSON array of objects with these exact fields: name, company, industry, website, role
- "name" should be the likely decision maker name if mentioned, otherwise "Decision Maker"
- "role" should be CEO, Founder, or CTO if mentioned, otherwise "Decision Maker"  
- "industry" should be the specific industry based on the snippet
- Return ONLY the JSON array, no other text, no markdown, no backticks

Example format:
[{{"name": "John Smith", "company": "TechCorp", "industry": "SaaS", "website": "techcorp.com", "role": "CEO"}}]"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )

            raw = response.choices[0].message.content.strip()

            # Clean up common AI response issues
            # Sometimes the AI wraps JSON in markdown code blocks
            # even when told not to — defensive programming
            raw = re.sub(r'```json|```', '', raw).strip()

            companies = json.loads(raw)

            leads = []
            for c in companies:
                lead = Lead(
                    name=c.get("name", "Decision Maker"),
                    company=c.get("company", "Unknown"),
                    industry=c.get("industry", niche),
                    role=c.get("role", ""),
                    website=c.get("website", ""),
                    location=location
                )
                leads.append(lead)

            return leads

        except json.JSONDecodeError as e:
            print(f"AI returned invalid JSON: {e}")
            print(f"Raw response: {raw[:200]}")
            # Fall back to basic parsing if AI fails
            return self._fallback_parse(results, niche)

        except Exception as e:
            print(f"AI extraction error: {e}")
            return self._fallback_parse(results, niche)

    def _fallback_parse(self, results: list, niche: str) -> list:
        """
        Simple fallback if AI extraction fails.
        Better to return something than nothing.
        This is DEFENSIVE PROGRAMMING — always have a backup plan.
        """
        leads = []
        skip_domains = ["wikipedia", "linkedin.com/jobs", "indeed", "glassdoor"]

        for result in results:
            try:
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")

                if any(skip in link.lower() for skip in skip_domains):
                    continue

                company_name = re.split(r'[-|·]', title)[0].strip()
                if not company_name:
                    continue

                lead = Lead(
                    name="Decision Maker",
                    company=company_name,
                    industry=niche,
                    website=link
                )
                if snippet:
                    lead.add_note(snippet[:200])
                leads.append(lead)

            except Exception:
                continue

        return leads