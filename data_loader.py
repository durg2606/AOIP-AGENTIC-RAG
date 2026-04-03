"""
data_loader.py
────────────────────────────────────────────
Handles loading, validating, and cleaning all raw operational datasets
for the Agentic Operational Intelligence Platform (AOIP).

Outputs:
    - Clean pandas DataFrames
    - Optional Parquet serialization for faster downstream use
"""

# ─────────────── IMPORTS ────────────────
import pandas as pd
from pathlib import Path


# ─────────────── CONFIGURATION ──────────
# Centralised data directory; adapt to your local repo path
# ─────────────── CONFIGURATION ──────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

print(f"📂 DATA_DIR = {DATA_DIR}")


# ─────────────── CORE FUNCTIONS ─────────

def load_raw_datasets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Reads all CSVs generated earlier (tickets, SLA logs, feedback, root cause, and linkage).
    Performs lightweight sanity checks — confirms files exist and prints their shapes.
    """
    files = {
        "tickets": "tickets.csv",
        "sla_logs": "sla_logs.csv",
        "feedback": "feedback.csv",
        "root_cause": "root_cause.csv",
        "links": "ticket_rootcause_links.csv",
    }

    datasets = {}
    for name, fname in files.items():
        fpath = DATA_DIR / fname
        if not fpath.exists():
            raise FileNotFoundError(f"❌ Missing file: {fpath}")
        df = pd.read_csv(fpath)
        print(f"Loaded {fname:28} -> rows: {len(df):5d} , cols: {len(df.columns):2d}")
        datasets[name] = df

    return (
        datasets["tickets"],
        datasets["sla_logs"],
        datasets["feedback"],
        datasets["root_cause"],
        datasets["links"],
    )


def basic_summary(df: pd.DataFrame, name: str = "") -> None:
    """
    Prints quick overview: null counts, duplicate rows, and example records.
    Helps visually verify data generation quality.
    """
    print("\n" + "=" * 60)
    print(f"SUMMARY :: {name.upper()}")
    print("=" * 60)
    print(df.info(memory_usage='deep'))
    print("\nMissing values per column:\n", df.isna().sum())
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print("\nSample records:")
    print(df.sample(3, random_state=42))
    print("-" * 60)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    1. Removes duplicates.
    2. Trims whitespace around strings.
    3. Fills NaNs with blanks for text columns.
    4. Enforces consistent case on categorical values (e.g., Region, Tower).
    5. Optionally converts date columns when detected.
    """
    df = df.drop_duplicates()

    # Strip surrounding spaces on all string columns
    object_cols = df.select_dtypes(include=["object"]).columns
    for col in object_cols:
        df[col] = df[col].astype(str).str.strip()

    # Fill remaining NaNs (to prevent tokenizer errors downstream)
    df = df.fillna("")

    # Auto‑detect and parse date columns by name pattern
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass

    # Normalise some specific categorical columns
    for c in df.columns:
        if c.lower() in ["region", "tower", "status", "category"]:
            df[c] = df[c].astype(str).str.title()

    return df


def save_as_parquet(df: pd.DataFrame, name: str) -> None:
    """
    Writes DataFrame to Parquet for faster downstream loading.
    """
    out_path = DATA_DIR / f"{name}.parquet"
    df.to_parquet(out_path, index=False)
    print(f"✅ Saved cleaned {name} → {out_path}")


# ─────────────── MAIN EXECUTION ─────────

if __name__ == "__main__":
    print("🚀 Loading raw datasets ...")
    tickets, sla, feedback, rca, links = load_raw_datasets()

    # Display brief summaries for manual inspection
    basic_summary(tickets, "tickets")
    basic_summary(sla, "sla_logs")
    basic_summary(feedback, "feedback")

    print("🧹 Cleaning datasets ...")
    tickets_clean = clean_dataframe(tickets)
    sla_clean = clean_dataframe(sla)
    feedback_clean = clean_dataframe(feedback)
    rca_clean = clean_dataframe(rca)
    links_clean = clean_dataframe(links)

    print("💾 Saving cleaned data to Parquet ...")
    save_as_parquet(tickets_clean, "tickets_clean")
    save_as_parquet(sla_clean, "sla_clean")
    save_as_parquet(feedback_clean, "feedback_clean")
    save_as_parquet(rca_clean, "root_cause_clean")
    save_as_parquet(links_clean, "links_clean")

    print("\n🎉 Data ingestion & cleaning completed successfully!")
