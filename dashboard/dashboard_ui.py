"""
dashboard/app.py
────────────────────────────────────────────
Main Streamlit dashboard for AOIP.
"""

# ───────── IMPORTS ─────────
import sys
from pathlib import Path
import streamlit as st

# Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Local project imports
from insight_agent import InsightAgent
from rca_agent import RCAAgent
from report_agent import ReportAgent
from data_loader import load_raw_datasets
from monitoring.logger import start_metrics_server

# ───────── PAGE CONFIG ─────────
st.set_page_config(
    page_title="AOIP Dashboard",
    page_icon="🧠",
    layout="wide"
)

# Start Prometheus endpoint
start_metrics_server()

st.title("🧠 Agentic Operational Intelligence Platform")
st.markdown("Unified KPI analytics, RCA intelligence, AI reasoning, and reporting")

# ───────── INIT AGENTS ─────────
@st.cache_resource
def init_agents():
    tickets, sla, feedback, rca, links = load_raw_datasets()

    insight = InsightAgent(sla)
    rca_agent = RCAAgent(rca, links)
    report = ReportAgent(insight, rca_agent)

    return insight, rca_agent, report


insight_agent, rca_agent, report_agent = init_agents()

# ───────── SIDEBAR KPI SNAPSHOT ─────────
st.sidebar.header("📊 KPI Snapshot")

summary = insight_agent.summary_report()
for k, v in summary.items():
    st.sidebar.metric(label=k, value=v)

if st.sidebar.button("📈 View Trends"):
    st.sidebar.plotly_chart(
        insight_agent.plot_trends(),
        use_container_width=True
    )

# ───────── MAIN TABS ─────────
tab1, tab2, tab3 = st.tabs([
    "💬 AI Query",
    "🧩 RCA Lookup",
    "📄 Generate Report"
])

# ───────── TAB 1: AI QUERY ─────────
with tab1:
    st.subheader("💬 Ask AI about operations")

    query = st.text_area(
        "Ask a question",
        "Why were SLA breaches higher in August 2024?"
    )

    if st.button("Run Analysis"):
        with st.spinner("Running RAG analysis..."):
            # Lazy import prevents circular import
            from rag_pipeline import query_rag
            result = query_rag(query)

        st.success("Analysis complete")
        st.write(result)

# ───────── TAB 2: RCA LOOKUP ─────────
with tab2:
    st.subheader("🧩 Root Cause Lookup")

    ticket_id = st.text_input(
        "Enter Ticket ID",
        "TCK00025"
    )

    if st.button("Get Root Cause"):
        result = rca_agent.get_root_cause(ticket_id)

        st.json(result)

        st.plotly_chart(
            rca_agent.plot_severity_distribution(),
            use_container_width=True
        )

# ───────── TAB 3: REPORT GENERATION ─────────
with tab3:
    st.subheader("📄 Generate Operational Report")

    report_ticket = st.text_input(
        "Ticket ID for report spotlight",
        "TCK00025"
    )

    if st.button("Generate Report"):
        html_path = report_agent.save_html(report_ticket)
        pdf_path = report_agent.export_pdf(report_ticket)

        st.success("✅ Report generated successfully")
        st.write(f"📄 HTML Report: {html_path}")
        st.write(f"📕 PDF Report: {pdf_path}")

# ───────── FOOTER ─────────
st.markdown("---")
st.caption("AOIP • KPI + RCA + RAG + Reporting")