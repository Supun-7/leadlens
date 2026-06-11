from abc import ABC, abstractmethod
from dotenv import load_dotenv
from groq import Groq
from core.lead import Lead
import os

load_dotenv()


class BaseScorer(ABC):

    @abstractmethod
    def score(self, lead: Lead) -> int:
        pass

    def score_all(self, leads: list) -> list:
        for lead in leads:
            lead.score = self.score(lead)
        return sorted(leads, key=lambda l: l.score, reverse=True)


class RuleBasedScorer(BaseScorer):

    def __init__(self, target_industries: list, target_roles: list):
        self.target_industries = target_industries
        self.target_roles = target_roles

    def score(self, lead: Lead) -> int:
        score = 0
        if lead.industry in self.target_industries:
            score += 40
        if lead.role in self.target_roles:
            score += 35
        if lead.website:
            score += 15
        if lead.notes:
            score += 10
        return min(score, 100)


class AIScorer(BaseScorer):

    def __init__(self, target_description: str):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.target_description = target_description

    def score(self, lead: Lead) -> int:
        prompt = f"""You are a lead qualification expert.

Score this lead from 0 to 100 based on how well they match the ideal customer.

Ideal customer: {self.target_description}

Lead details:
- Name: {lead.name}
- Company: {lead.company}
- Industry: {lead.industry}
- Role: {lead.role or 'Unknown'}
- Website: {lead.website or 'None'}
- Notes: {', '.join(lead.notes) or 'None'}

Reply with a SINGLE number between 0 and 100. Nothing else."""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.1
            )
            raw = response.choices[0].message.content.strip()
            return int(raw)
        except Exception as e:
            print(f"Scoring error for {lead.name}: {e}")
            return 0