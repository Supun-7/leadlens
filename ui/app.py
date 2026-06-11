import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from core.researcher import Researcher
from core.scorer import AIScorer, RuleBasedScorer
from core.email_writer import AIEmailWriter, TemplateEmailWriter

load_dotenv()

st.set_page_config(
    page_title="LeadLens",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 LeadLens")
st.caption("AI-powered lead generation — find and qualify your ideal buyers automatically")
st.divider()

with st.sidebar:
    st.header("Campaign setup")

    niche = st.text_input("Target niche", value="SaaS startups")
    location = st.text_input("Location", value="Sri Lanka")
    sender_name = st.text_input("Your name", value="Supun")
    product = st.text_area(
        "What you offer",
        value="AI-powered lead generation that finds and qualifies buyers automatically",
        height=100
    )

    st.divider()

    use_ai = st.toggle("Use AI scoring", value=True)
    score_threshold = st.slider("Qualification threshold", 0, 100, 60)

    st.divider()

    run_button = st.button("Find leads", type="primary", use_container_width=True)

if "results" not in st.session_state:
    st.session_state.results = None

if run_button:
    if not niche or not sender_name or not product:
        st.error("Please fill in all fields before running.")
    else:
        with st.status("LeadLens is working...", expanded=True) as status:

            st.write("Searching the web for leads...")
            researcher = Researcher()
            leads = researcher.find_leads(niche, location, num_results=10)

            if not leads:
                st.error("No leads found. Try a different niche or location.")
                st.stop()

            st.write(f"Found {len(leads)} leads. Scoring now...")

            if use_ai:
                scorer = AIScorer(target_description=f"{niche} in {location}")
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

            st.session_state.results = ranked
            status.update(label="Done!", state="complete")

if st.session_state.results:
    results = st.session_state.results
    qualified = [l for l in results if l.score >= score_threshold]
    not_qualified = [l for l in results if l.score < score_threshold]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total leads", len(results))
    col2.metric("Qualified", len(qualified))
    col3.metric("Avg score", round(sum(l.score for l in results) / len(results)))

    st.divider()

    tab1, tab2 = st.tabs([
        f"Qualified leads ({len(qualified)})",
        f"Not qualified ({len(not_qualified)})"
    ])

    with tab1:
        if not qualified:
            st.info("No leads met the threshold. Try lowering the slider.")
        for lead in qualified:
            with st.expander(f"**{lead.name}** — {lead.company} | Score: {lead.score}/100"):
                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown("**Lead details**")
                    st.write(f"Company: {lead.company}")
                    st.write(f"Industry: {lead.industry}")
                    st.write(f"Role: {lead.role or 'Unknown'}")
                    st.write(f"Website: {lead.website or 'N/A'}")
                    st.write(f"Score: {lead.score}/100")
                    if lead.notes:
                        st.write(f"Notes: {lead.notes[0]}")

                with col_b:
                    st.markdown("**Outreach email**")
                    if lead.outreach_email:
                        st.code(lead.outreach_email, language=None)
                    else:
                        st.caption("No email generated")

    with tab2:
        for lead in not_qualified:
            st.write(f"❌ {lead.name} @ {lead.company} — Score: {lead.score}/100")