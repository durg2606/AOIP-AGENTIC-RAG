from pathlib import Path
import pandas as pd
import plotly.express as px
from monitoring.logger import monitor


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

class RCAAgent:
    """
    Handles root-cause lookup, RCA analytics,
    severity trends, and mitigation retrieval.
    """

    def __init__(self, rca_df=None, link_df=None):
        if rca_df is None or link_df is None:
            self.rca_df, self.link_df = self._load_data()
        else:
            self.rca_df, self.link_df = rca_df, link_df

        self._normalize_columns()

    # ───────── DATA LOADING ─────────
    def _load_data(self):
        root_path = DATA_DIR / "root_cause_clean.parquet"
        link_path = DATA_DIR / "links_clean.parquet"

        if not root_path.exists():
            raise FileNotFoundError(f"❌ Missing RCA parquet: {root_path}")

        if not link_path.exists():
            raise FileNotFoundError(f"❌ Missing links parquet: {link_path}")

        print("📥 Loading RCA and ticket-link datasets...")
        return pd.read_parquet(root_path), pd.read_parquet(link_path)

    def _normalize_columns(self):
        self.rca_df.columns = [
            c.strip().title().replace(" ", "_")
            for c in self.rca_df.columns
        ]
        self.link_df.columns = [
            c.strip().title().replace(" ", "_")
            for c in self.link_df.columns
        ]

    # ───────── RCA LOOKUP ─────────
    @monitor("RCALookup")
    def get_root_cause(self, ticket_id: str) -> dict:
        ticket_col = "Ticket_Id" if "Ticket_Id" in self.link_df.columns else "Ticket_ID"
        rca_col = "Rca_Id" if "Rca_Id" in self.link_df.columns else "RCA_ID"

        record = self.link_df[self.link_df[ticket_col] == ticket_id]

        if record.empty:
            return {
                "Ticket_ID": ticket_id,
                "Message": "No linked RCA found."
            }

        rca_id = record.iloc[0][rca_col]

        rca_key = "Rca_Id" if "Rca_Id" in self.rca_df.columns else "RCA_ID"
        rca_row = self.rca_df[self.rca_df[rca_key] == rca_id]

        if rca_row.empty:
            return {
                "Ticket_ID": ticket_id,
                "Message": "RCA ID reference missing."
            }

        r = rca_row.iloc[0]

        return {
            "Ticket_ID": ticket_id,
            "RCA_ID": rca_id,
            "Category": r.get("Category", ""),
            "Root_Cause": r.get("Root_Cause", ""),
            "Mitigation": r.get("Mitigation", ""),
            "Severity": r.get("Severity", ""),
            "Last_Occurrence": str(r.get("Last_Occurrence", "")),
        }

    # ───────── ANALYTICS ─────────
    def distribution_by_category(self):
        return (
            self.rca_df.groupby(["Category", "Severity"])
            .size()
            .reset_index(name="Count")
        )

    def top_root_causes(self, n: int = 10):
        top = (
            self.rca_df["Root_Cause"]
            .value_counts()
            .head(n)
            .reset_index()
        )
        top.columns = ["Root_Cause", "Occurrences"]
        return top

    def category_summary(self):
        if "Avg_Resolution_Hrs" in self.rca_df.columns:
            return (
                self.rca_df.groupby("Category")[["Avg_Resolution_Hrs"]]
                .mean()
                .reset_index()
            )

        return (
            self.rca_df.groupby("Category")
            .size()
            .reset_index(name="Count")
        )

    # ───────── VISUALS ─────────
    def plot_severity_distribution(self):
        dist = self.distribution_by_category()

        fig = px.bar(
            dist,
            x="Category",
            y="Count",
            color="Severity",
            title="🧩 RCA Severity Distribution",
            barmode="stack",
        )

        fig.update_layout(template="plotly_white")
        return fig

    def plot_top_root_causes(self):
        top = self.top_root_causes()

        fig = px.bar(
            top,
            x="Root_Cause",
            y="Occurrences",
            title="🏷 Top Root Causes",
        )

        fig.update_layout(template="plotly_white", xaxis_tickangle=45)
        return fig


# ─────────────── TEST RUN ───────────────
if __name__ == "__main__":
    agent = RCAAgent()

    sample_id = "TCK00025"
    print(f"\n🔍 RCA lookup for {sample_id}")
    result = agent.get_root_cause(sample_id)

    for k, v in result.items():
        print(f"{k:<18}: {v}")

    print("\n📊 Top root causes")
    print(agent.top_root_causes())

    try:
        agent.plot_severity_distribution().show()
        agent.plot_top_root_causes().show()
    except Exception:
        print("📉 Plot skipped in terminal")
