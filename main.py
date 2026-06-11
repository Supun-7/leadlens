from dotenv import load_dotenv
from core.lead import Lead
from core.scorer import AIScorer, RuleBasedScorer
from core.email_writer import AIEmailWriter, TemplateEmailWriter

load_dotenv()


def run_leadlens(
    niche: str,
    location: str,
    sender_name: str,
    product: str,
    use_ai: bool = True
):
    """
    The main LeadLens pipeline — runs end to end.

    Parameters explain themselves because we named them well.
    This is called SELF-DOCUMENTING CODE — a clean code principle.
    You shouldn't need comments to understand what the parameters do.

    use_ai=True  → uses Groq AI for scoring and emails (smart, slower)
    use_ai=False → uses rules + template (fast, free, good for testing)
    """

    print(f"\nLeadLens starting...")
    print(f"Target: {niche} in {location}\n")

    # ── Step 1: Create sample leads ──────────────────────────────
    # In the next phase we'll replace this with real web scraping.
    # For now, hardcoded leads let us test the full pipeline works.
    # This is called a STUB — a placeholder that mimics real data.
    leads = [
        Lead("Sarah Chen",  "TechCorp",  "SaaS",   role="CEO",     website="techcorp.com"),
        Lead("Rohan Silva", "RetailCo",  "Retail",  role="Manager", website=""),
        Lead("Priya Nair",  "StartupX",  "Tech",    role="Founder", website="startupx.io"),
        Lead("Amal Perera", "CloudBase", "SaaS",    role="CTO",     website="cloudbase.io"),
        Lead("Nadia Khan",  "ShopFast",  "eCommerce", role="CEO",   website="shopfast.lk"),
    ]

    print(f"Found {len(leads)} leads. Scoring now...")

    # ── Step 2: Score leads ───────────────────────────────────────
    # Notice how we choose scorer based on use_ai flag.
    # Both scorers have the same interface — score_all(leads).
    # This is polymorphism in production use.
    if use_ai:
        scorer = AIScorer(
            target_description=f"{niche} companies in {location}"
        )
    else:
        scorer = RuleBasedScorer(
            target_industries=["SaaS", "Tech"],
            target_roles=["CEO", "Founder", "CTO"]
        )

    ranked = scorer.score_all(leads)

    # ── Step 3: Write outreach emails ────────────────────────────
    print("Writing personalised emails for qualified leads...\n")

    if use_ai:
        writer = AIEmailWriter(
            sender_name=sender_name,
            product=product
        )
    else:
        writer = TemplateEmailWriter(
            sender_name=sender_name,
            product=product
        )

    writer.write_all(ranked)

    # ── Step 4: Display results ───────────────────────────────────
    qualified = [l for l in ranked if l.is_qualified()]
    not_qualified = [l for l in ranked if not l.is_qualified()]

    print(f"RESULTS — {len(qualified)} qualified, {len(not_qualified)} not qualified")
    print("=" * 60)

    for lead in qualified:
        print(f"\n{lead}")
        print(f"\n{lead.outreach_email}")
        print("-" * 60)

    if not_qualified:
        print(f"\nSkipped (low score):")
        for lead in not_qualified:
            print(f"  {lead}")

    return ranked


# ── Entry point ───────────────────────────────────────────────────
# This pattern — if __name__ == "__main__" — is fundamental Python.
# It means: only run this block if you're running THIS file directly.
# If another file imports main.py, this block is skipped.
#
# Java equivalent: public static void main(String[] args) { }
# Exact same concept — the entry point of the program.

if __name__ == "__main__":
    run_leadlens(
        niche="SaaS startups",
        location="Sri Lanka",
        sender_name="Supun",
        product="AI-powered lead generation that finds and qualifies buyers automatically",
        use_ai=True
    )