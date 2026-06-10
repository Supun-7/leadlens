# ============================================================
# core/lead.py
# The Lead class — the central data model of LeadLens
#
# SOLID principle applied here:
#   Single Responsibility — this class has ONE job:
#   represent a lead and its data. Nothing else.
# ============================================================


# ------ WHY WE IMPORT ------
# In Java: import java.util.List;
# In Python: from module import something
# 'datetime' is a built-in Python module for handling dates/times
from datetime import datetime


# ------ THE CLASS ------
# In Java:  public class Lead { ... }
# In Python: class Lead:
#
# No 'public', no 'private' keyword needed at class level.
# Python classes are public by default.

class Lead:
    """
    Represents a single potential buyer found by LeadLens.

    This is called a 'docstring' — Python's built-in documentation system.
    In Java you used Javadoc (/** */). This is the Python equivalent.
    Any class, function, or module can have one.
    """

    # ------ THE CONSTRUCTOR ------
    # In Java:  public Lead(String name, String company) { ... }
    # In Python: def __init__(self, name, company):
    #
    # __init__ is a 'dunder' method (double underscore = dunder).
    # Python calls it automatically when you create a new Lead object.
    # 'self' is exactly Java's 'this' — it refers to the current object instance.
    #
    # TYPE HINTS — notice ': str', ': int', '= 0'
    # Python doesn't ENFORCE types like Java, but we can HINT them.
    # This helps VS Code give you autocomplete and catch mistakes early.
    # The '= None' and '= 0' parts are DEFAULT VALUES —
    # if you don't pass that argument, Python uses the default.

    def __init__(
        self,
        name: str,          # Full name of the person
        company: str,       # Company they work at
        industry: str,      # e.g. "SaaS", "Agency", "E-commerce"
        role: str = "",     # Job title — defaults to empty string if not given
        email: str = "",    # Contact email — optional
        website: str = "",  # Company website — optional
        score: int = 0,     # Fit score 0-100, starts at 0
    ):
        # Assigning constructor arguments to instance variables.
        # In Java: this.name = name;
        # In Python: self.name = name
        # No type declaration needed — Python infers it from the value.

        self.name = name
        self.company = company
        self.industry = industry
        self.role = role
        self.email = email
        self.website = website
        self.score = score

        # This variable is NOT passed in — we generate it automatically.
        # datetime.now() returns the current date and time.
        # This records WHEN this lead was found. Useful for the dashboard later.
        self.found_at = datetime.now()

        # A list to hold notes about why this lead scored well or poorly.
        # We start with an empty list — the scorer will add to this later.
        # In Java: List<String> notes = new ArrayList<>();
        # In Python: self.notes = []
        self.notes: list[str] = []


    # ------ METHODS ------
    # In Java: public void addNote(String note) { ... }
    # In Python: def add_note(self, note: str):
    #
    # Notice Python uses snake_case (add_note) not camelCase (addNote).
    # This is Python's official style convention — PEP 8.
    # Always follow it. Interviewers notice.

    def add_note(self, note: str):
        """Add a scoring note to this lead."""
        self.notes.append(note)  # .append() adds to end of list — like ArrayList.add()


    def is_qualified(self) -> bool:
        """
        Returns True if this lead meets the minimum score threshold.

        '-> bool' is the return type hint. Again, not enforced, but good practice.
        Think of it as documentation that also helps your IDE.
        """
        return self.score >= 60   # A lead needs 60+ to be considered qualified


    # ------ DUNDER METHOD: __str__ ------
    # In Java: public String toString() { return "..."; }
    # In Python: def __str__(self) — same idea, different syntax.
    #
    # Python calls this automatically when you do print(lead)
    # Without it, print(lead) shows something ugly like:
    # <core.lead.Lead object at 0x1045b2d10>

    def __str__(self) -> str:
        """Human-readable string — used when you print() a Lead."""
        qualified_tag = "QUALIFIED" if self.is_qualified() else "not qualified"
        return f"{self.name} @ {self.company} | Score: {self.score} | {qualified_tag}"


    # ------ DUNDER METHOD: __repr__ ------
    # __str__ is for humans. __repr__ is for developers/debugging.
    # When you inspect an object in the Python console, __repr__ is shown.
    # Best practice: make it look like the code that would recreate the object.

    def __repr__(self) -> str:
        return (
            f"Lead(name='{self.name}', company='{self.company}', "
            f"industry='{self.industry}', score={self.score})"
        )


    # ------ DUNDER METHOD: __eq__ ------
    # In Java: @Override public boolean equals(Object obj) { ... }
    # Same concept — defines what "equal" means for two Lead objects.
    #
    # Without this, Python checks if two variables point to the
    # SAME object in memory (like == in Java for objects).
    # With this, we define equality by business logic: same name + company.

    def __eq__(self, other) -> bool:
        """Two leads are equal if they have the same name and company."""
        if not isinstance(other, Lead):  # isinstance() = Java's instanceof
            return False
        return self.name == other.name and self.company == other.company


    # ------ to_dict METHOD ------
    # This converts our Lead object into a Python dictionary.
    # WHY? Because when we save leads to a file (JSON) or send them
    # to a web API, they need to be plain data — not Python objects.
    # This is called SERIALIZATION — converting an object to a storable format.
    # You'll see this concept everywhere in backend development.

    def to_dict(self) -> dict:
        """Serialize this Lead to a dictionary (for JSON storage/API responses)."""
        return {
            "name": self.name,
            "company": self.company,
            "industry": self.industry,
            "role": self.role,
            "email": self.email,
            "website": self.website,
            "score": self.score,
            "notes": self.notes,
            "found_at": self.found_at.isoformat(),  # Convert datetime to a string
        }


    # ------ CLASS METHOD: from_dict ------
    # This is the REVERSE of to_dict — it RECREATES a Lead from a dictionary.
    #
    # Notice '@classmethod' and 'cls' instead of 'self'.
    # This is a CLASS method, not an INSTANCE method.
    #
    # INSTANCE method:  lead.add_note("good fit")   — called on an object
    # CLASS method:     Lead.from_dict(data)         — called on the class itself
    #
    # In Java this would be a static factory method:
    # public static Lead fromDict(Map<String, Object> data) { ... }
    #
    # We use this when loading saved leads back from a JSON file.

    @classmethod
    def from_dict(cls, data: dict) -> "Lead":
        """Recreate a Lead object from a dictionary (e.g. loaded from JSON file)."""
        return cls(
            name=data["name"],
            company=data["company"],
            industry=data["industry"],
            role=data.get("role", ""),      # .get() safely returns "" if key missing
            email=data.get("email", ""),    # safer than data["email"] which crashes
            website=data.get("website", ""),
            score=data.get("score", 0),
        )