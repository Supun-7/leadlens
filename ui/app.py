import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from core.lead import Lead
from core.scorer import AIScorer, RuleBasedScorer
from core.email_writer import AIEmailWriter, TemplateEmailWriter

load_dotenv()

# ── Page config ───────────────────────────────────────────────────
# This must be the FIRST streamlit call in the file.
# Sets the browser tab title and layout.
st.set_page_config(
    page_title="LeadLens",
    page_icon="🔍",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────────────
st.title("🔍 LeadLens")
st.caption("AI-powered lead generation — find and qualify your ideal buyers automatically")
st.divider()

# ── Sidebar — user inputs ─────────────────────────────────────────
# st.sidebar puts widgets in the left panel.
# Everything the user configures lives here — clean separation
# between controls and results. Same idea as our code architecture.
with st.sidebar:
    st.header("Campaign setup")

    niche = st.text_input(
        "Target niche",
        placeholder="e.g. SaaS startups, Digital agencies",
        value="SaaS startups"
    )

    location = st.text_input(
        "Location",
        placeholder="e.g. Sri Lanka, Colombo",
        value="Sri Lanka"
    )

    sender_name = st.text_input(
        "Your name",
        placeholder="e.g. Supun",
        value="Supun"
    )

    product = st.text_area(
        "What you offer",
        placeholder="e.g. AI-powered lead generation...",
        value="AI-powered lead generation that finds and qualifies buyers automatically",
        height=100
    )

    st.divider()

    use_ai = st.toggle("Use AI scoring", value=True)
    score_threshold = st.slider("Qualification threshold", 0, 100, 60)

    st.divider()

    run_button = st.button("Find leads", type="primary", use_container_width=True)

# ── Main area — results ───────────────────────────────────────────
# st.session_state is Streamlit's way of remembering data
# between button clicks. Without it, every click resets everything.
# Think of it like a global variable that survives re-runs.
if "results" not in st.session_state:
    st.session_state.results = None

if run_button:
    # Validation — don't run if fields are empty
    if not niche or not sender_name or not product:
        st.error("Please fill in all fields before running.")
    else:
        # ── Pipeline runs here ────────────────────────────────────
        # st.status shows a live progress box while we work.
        # The 'with' block is a CONTEXT MANAGER — Python runs the
        # code inside, then automatically closes the status box.
        # Java equivalent: try-with-resources.
        with st.status("LeadLens is working...", expanded=True) as status:

            st.write("Creating sample leads...")
            leads = [
                Lead("Sarah Chen",  "TechCorp",   "SaaS",      role="CEO",     website="techcorp.com"),
                Lead("Rohan Silva", "RetailCo",   "Retail",    role="Manager", website=""),
                Lead("Priya Nair",  "StartupX",   "Tech",      role="Founder", website="startupx.io"),
                Lead("Amal Perera", "CloudBase",  "SaaS",      role="CTO",     website="cloudbase.io"),
                Lead("Nadia Khan",  "ShopFast",   "eCommerce", role="CEO",     website="shopfast.lk"),
            ]

            st.write(f"Scoring {len(leads)} leads...")
            if use_ai:
                scorer = AIScorer(
                    target_description=f"{niche} in {location}"
                )
            else:
                scorer = RuleBasedScorer(
                    target_industries=["SaaS", "Tech"],
                    target_roles=["CEO", "Founder", "CTO"]
                )
            ranked = scorer.score_all(leads)

            st.write("Writing personalised emails...")
            if use_ai:
                writer = AIEmailWriter(sender_name=sender_name, product=product)
            else:
                writer = TemplateEmailWriter(sender_name=sender_name, product=product)
            writer.write_all(ranked)

            # Apply the custom threshold from the slider
            for lead in ranked:
                lead.score = lead.score

            st.session_state.results = ranked
            status.update(label="Done!", state="complete")

# ── Display results ───────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    qualified = [l for l in results if l.score >= score_threshold]
    not_qualified = [l for l in results if l.score < score_threshold]

    # Metric cards — summary numbers at the top
    col1, col2, col3 = st.columns(3)
    col1.metric("Total leads", len(results))
    col2.metric("Qualified", len(qualified))
    col3.metric("Avg score", round(sum(l.score for l in results) / len(results)))

    st.divider()

    # Tabs — clean way to separate qualified vs skipped
    # st.tabs returns a list of tab objects.
    # The 'with' block writes content into that specific tab.
    tab1, tab2 = st.tabs([f"Qualified leads ({len(qualified)})", f"Not qualified ({len(not_qualified)})"])

    with tab1:
        if not qualified:
            st.info("No leads met the qualification threshold. Try lowering the slider.")
        for lead in qualified:
            # st.expander collapses content under a clickable header
            with st.expander(f"**{lead.name}** — {lead.company} | Score: {lead.score}/100"):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("**Lead details**")
                    st.write(f"Company: {lead.company}")
                    st.write(f"Industry: {lead.industry}")
                    st.write(f"Role: {lead.role}")
                    st.write(f"Website: {lead.website or 'N/A'}")
                    st.write(f"Score: {lead.score}/100")

                with col_b:
                    st.markdown("**Outreach email**")
                    if lead.outreach_email:
                        st.code(lead.outreach_email, language=None)
                    else:
                        st.caption("Score below threshold — no email generated")

    with tab2:
        for lead in not_qualified:
            st.write(f"❌ {lead.name} @ {lead.company} — Score: {lead.score}/100")