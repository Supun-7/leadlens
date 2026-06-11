from dotenv import load_dotenv
from core.researcher import Researcher
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
    print(f"\nLeadLens starting...")
    print(f"Target: {niche} in {location}\n")

    researcher = Researcher()
    leads = researcher.find_leads(niche, location, num_results=10)

    if not leads:
        print("No leads found. Try a different niche or location.")
        return []

    print(f"Found {len(leads)} leads. Scoring now...")

    if use_ai:
        scorer = AIScorer(target_description=f"{niche} in {location}")
    else:
        scorer = RuleBasedScorer(
            target_industries=["SaaS", "Tech"],
            target_roles=["CEO", "Founder", "CTO"]
        )

    ranked = scorer.score_all(leads)

    print("Writing personalised emails for qualified leads...\n")

    if use_ai:
        writer = AIEmailWriter(sender_name=sender_name, product=product)
    else:
        writer = TemplateEmailWriter(sender_name=sender_name, product=product)

    writer.write_all(ranked)

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


if __name__ == "__main__":
    run_leadlens(
        niche="SaaS startups",
        location="Sri Lanka",
        sender_name="Supun",
        product="AI-powered lead generation that finds and qualifies buyers automatically",
        use_ai=True
    )