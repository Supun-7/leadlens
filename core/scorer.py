# core/scorer.py
# SOLID — Open/Closed Principle in action:
# The base Scorer defines the contract (what scoring means).
# We can add new scoring strategies (AI, rules, hybrid) without
# touching existing code. Open for extension, closed for modification.

from abc import ABC, abstractmethod
from core.lead import Lead


class BaseScorer(ABC):
    """
    Abstract Base Class — defines WHAT a scorer must do,
    not HOW it does it.

    In Java this would be:
        public abstract class BaseScorer { }
    or an interface:
        public interface Scorer { int score(Lead lead); }

    ABC = Abstract Base Class. It's a contract.
    Any class that extends BaseScorer MUST implement score().
    If it doesn't, Python throws an error at runtime.
    """

    @abstractmethod
    def score(self, lead: Lead) -> int:
        """
        Every scorer must implement this method.
        Takes a Lead, returns a score between 0 and 100.

        The ': Lead' and '-> int' are TYPE HINTS.
        Python doesn't enforce them, but they tell other
        developers (and VS Code) what this method expects.
        Same idea as Java's type declarations.
        """
        pass

    def score_all(self, leads: list) -> list:
        """
        This method IS implemented here — it works for ALL scorers.
        It loops through every lead and calls self.score() on each.

        'self.score()' will call whichever subclass's score() is active.
        This is POLYMORPHISM — same call, different behaviour depending
        on which scorer object you have.
        """
        for lead in leads:
            lead.score = self.score(lead)
        return sorted(leads, key=lambda l: l.score, reverse=True)


class RuleBasedScorer(BaseScorer):
    """
    CONCRETE implementation #1 — scores using simple business rules.
    No AI needed. Fast, predictable, free.

    This EXTENDS BaseScorer (inheritance).
    In Java: public class RuleBasedScorer extends BaseScorer { }
    """

    def __init__(self, target_industries: list, target_roles: list):
        """
        We pass in what we're looking for.
        This makes the scorer CONFIGURABLE — you can create different
        scorers for different niches without changing the class itself.
        """
        self.target_industries = target_industries
        self.target_roles = target_roles

    def score(self, lead: Lead) -> int:
        """
        Implementing the abstract method — this is REQUIRED.
        Uses simple rules to produce a score 0-100.
        """
        score = 0

        # Rule 1: industry match — worth 40 points
        if lead.industry in self.target_industries:
            score += 40

        # Rule 2: role match — worth 35 points
        if hasattr(lead, 'role') and lead.role in self.target_roles:
            score += 35

        # Rule 3: has a website — shows they're established
        if lead.website:
            score += 15

        # Rule 4: has notes — means we found extra signals
        if hasattr(lead, 'notes') and lead.notes:
            score += 10

        return min(score, 100)  # cap at 100


class AIScorer(BaseScorer):
    """
    CONCRETE implementation #2 — scores using an LLM.
    More intelligent, costs API money, slightly slower.

    Notice: we ADD this class without touching BaseScorer or
    RuleBasedScorer at all. That's the Open/Closed Principle.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def score(self, lead: Lead) -> int:
        """
        Placeholder for now — we'll implement the real
        AI API call in the next step when we add the API key.
        """
        # TODO: call OpenAI/Claude API here
        # For now return a placeholder so the app runs
        return 50