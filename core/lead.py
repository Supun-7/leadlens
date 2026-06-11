from datetime import datetime


class Lead:

    def __init__(self, name, company, industry, role="", website="", location="", score=0):
        self.name = name
        self.company = company
        self.industry = industry
        self.role = role
        self.website = website
        self.location = location
        self.score = score
        self.outreach_email = ""
        self.notes = []
        self.found_at = datetime.now().isoformat()

    def add_note(self, note):
        self.notes.append(note)

    def is_qualified(self):
        return self.score >= 60

    def to_dict(self):
        return {
            "name": self.name,
            "company": self.company,
            "industry": self.industry,
            "role": self.role,
            "email": "",
            "website": self.website,
            "score": self.score,
            "notes": self.notes,
            "outreach_email": self.outreach_email,
            "found_at": self.found_at
        }

    def __str__(self):
        status = "QUALIFIED" if self.is_qualified() else "not qualified"
        return f"{self.name} @ {self.company} | Score: {self.score} | {status}"