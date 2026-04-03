BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

# ─────────────── INSIGHT AGENT ──────────
class InsightAgent:
    """
    Performs quantitative analysis on SLA logs.
    Designed for agents, dashboards, and APIs.
    """

    def __init__(self, df: pd.DataFrame | None = None):
        self.df = df if df is not None else self._load_sla()
        self._prepare()

    # ───────── INTERNAL UTILITIES ─────────
    def _load_sla(self) -> pd.DataFrame:
        path = DATA_DIR / "sla_clean.parquet"

        if not path.exists():
            raise FileNotFoundError(f"❌ Missing SLA parquet: {path}")

        print(f"📥 Loading SLA dataset from {path}")
        return pd.read_parquet(path)

    def _prepare(self):
        """
        Standardize dates and create derived time columns.
        """
        self.df["Date"] = pd.to_datetime(self.df["Date"], errors="coerce")
        self.df = self.df.dropna(subset=["Date"])

        self.df["Month"] = self.df["Date"].dt.to_period("M").astype(str)
        self.df["Week"] = self.df["Date"].dt.isocalendar().week.astype(int)

    # ───────── KPI CALCULATIONS ───────────
    def breach_rate(self) -> float:
        total_closed = self.df["Tickets_Closed"].sum()
        total_breaches = self.df["SLA_Breaches"].sum()

        if total_closed == 0:
            return 0.0

        rate = round((total_breaches / total_closed) * 100, 2)
        print(f"📊 Breach Rate = {rate}% ({total_breaches}/{total_closed})")
        return rate

    def avg_resolution_time(self) -> float:
        return round(self.df["Avg_Resolution_Hrs"].mean(), 2)

    def avg_csat(self) -> float:
        return round(self.df["CSAT_Avg"].mean(), 2)

    def monthly_summary(self) -> pd.DataFrame:
        month_df = (
            self.df.groupby("Month")
            .agg({
                "Avg_Resolution_Hrs": "mean",
                "CSAT_Avg": "mean",
                "SLA_Breaches": "sum",
                "Tickets_Closed": "sum"
            })
            .reset_index()
        )

        month_df["Breach_Rate_%"] = (
            month_df["SLA_Breaches"] /
            month_df["Tickets_Closed"] * 100
        ).round(2)

        return month_df

    def anomaly_periods(self, threshold: float = 10.0) -> pd.DataFrame:
        """
        Detect months where breach rate exceeds threshold.
        """
        monthly = self.monthly_summary()
        return monthly[monthly["Breach_Rate_%"] > threshold]

    @monitor("KPIReport")
    def summary_report(self) -> dict:
        return {
            "Breach_Rate(%)": self.breach_rate(),
            "Avg_Resolution_Hrs": self.avg_resolution_time(),
            "Avg_CSAT": self.avg_csat(),
        }

    # ───────── VISUALIZATION ──────────────
    def plot_trends(self):
        fig = px.line(
            self.df,
            x="Date",
            y=["Avg_Resolution_Hrs", "CSAT_Avg"],
            labels={"value": "Metric Value", "variable": "Metric"},
            title="📈 SLA Resolution & CSAT Trends"
        )

        fig.update_layout(
            template="plotly_white",
            legend=dict(x=0.05, y=1.1)
        )

        return fig


# ─────────────── TEST RUN ───────────────
if __name__ == "__main__":
    agent = InsightAgent()

    print("\n🔹 KPI SUMMARY")
    report = agent.summary_report()
    for k, v in report.items():
        print(f"{k:<25}: {v}")

    anomalies = agent.anomaly_periods(threshold=8.0)

    if not anomalies.empty:
        print("\n⚠️ Anomaly Months (>8% breach)")
        print(anomalies[["Month", "Breach_Rate_%"]])

    try:
        agent.plot_trends().show()
    except Exception:
        print("📉 Plot skipped (non-interactive terminal)")
