from abc import ABC, abstractmethod
from dotenv import load_dotenv
from groq import Groq
from core.lead import Lead
import os

load_dotenv()


class BaseEmailWriter(ABC):

    @abstractmethod
    def write(self, lead: Lead) -> str:
        pass

    def write_all(self, leads: list) -> list:
        for lead in leads:
            if lead.is_qualified():
                lead.outreach_email = self.write(lead)
        return leads


class TemplateEmailWriter(BaseEmailWriter):

    def __init__(self, sender_name: str, product: str):
        self.sender_name = sender_name
        self.product = product

    def write(self, lead: Lead) -> str:
        first_name = lead.name.split()[0]
        return f"""Hi {first_name},

I came across {lead.company} and noticed you're in the {lead.industry} space.

I'm {self.sender_name} — I work with {lead.industry} companies to help them {self.product}.

Would you be open to a 15-minute call this week to see if there's a fit?

Best,
{self.sender_name}"""


class AIEmailWriter(BaseEmailWriter):

    def __init__(self, sender_name: str, product: str):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.sender_name = sender_name
        self.product = product

    def write(self, lead: Lead) -> str:
        prompt = f"""Write a short, personalised cold outreach email.

Sender: {self.sender_name}
Product/service: {self.product}

About the recipient:
- Name: {lead.name}
- Company: {lead.company}
- Industry: {lead.industry}
- Role: {lead.role or 'decision maker'}
- Score: {lead.score}/100
- Notes: {', '.join(lead.notes) or 'None'}

Rules:
- 3 short paragraphs maximum
- Reference something specific about their company or industry
- End with ONE clear call to action — a 15 min call
- Sound like a smart human, not a robot
- Sign off as {self.sender_name}"""

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Email writing error for {lead.name}: {e}")
            return ""