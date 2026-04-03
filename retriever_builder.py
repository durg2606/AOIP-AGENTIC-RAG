
from sentence_transformers import SentenceTransformer
import pandas as pd
import numpy as np
import faiss                           # Facebook AI Similarity Search
from pathlib import Path
import pickle
import time

# ─────────────── CONFIGS ───────────────
# Project root = folder where current script exists
BASE_DIR = Path(__file__).resolve().parent

# Standard project paths
DATA_PATH = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "faiss_index"

# Create index folder safely
INDEX_DIR.mkdir(parents=True, exist_ok=True)

print(f"📂 BASE_DIR   : {BASE_DIR}")
print(f"📁 DATA_PATH  : {DATA_PATH}")
print(f"🧠 INDEX_DIR  : {INDEX_DIR}")
# choose an encoder – can swap to "all-mpnet-base-v2" for higher quality
MODEL_NAME = "all-MiniLM-L6-v2"


# ─────────────── CORE FUNCTIONS ─────────

def load_text_corpus() -> pd.DataFrame:
    """
    Loads the cleaned tickets parquet file and extracts the textual corpus
    used for semantic embeddings (description + tags).
    """
    path = DATA_PATH / "tickets_clean.parquet"
    df = pd.read_parquet(path)
    print(f"✅ Loaded {len(df)} ticket records.")
    df["text_corpus"] = (
        df["Description"].astype(str) + " " +
        df["Tags"].astype(str)
    ).fillna("")
    return df[["Ticket_ID", "text_corpus", "Category", "Region", "Tower"]]


def build_embeddings(texts: list[str], batch_size: int = 64):
    """
    Generates normalized vector embeddings for provided texts.
    """
    model = SentenceTransformer(MODEL_NAME)
    print(f"🔧 Generating embeddings with {MODEL_NAME} ...")
    start = time.time()
    vectors = model.encode(
        texts, normalize_embeddings=True,
        batch_size=batch_size, show_progress_bar=True
    )
    print(f"⏱  Completed in {time.time() - start:.2f}s for {len(texts)} entries.")
    return model, np.array(vectors, dtype="float32")


def build_faiss_index(embeddings: np.ndarray):
    """
    Initializes a FAISS index using cosine similarity (IP on normalized vecs).
    """
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    print(f"📦 Index built with {index.ntotal} vectors of dim {dimension}")
    return index


def save_index(index, ids, model_name):
    """
    Persist FAISS index and additional metadata for retrieval mapping.
    """
    index_path = INDEX_DIR / "ticket_index.faiss"
    meta_path = INDEX_DIR / "ticket_index.pkl"
    faiss.write_index(index, str(index_path))
    meta = {"MODEL": model_name, "IDS": ids}
    with open(meta_path, "wb") as f:
        pickle.dump(meta, f)
    print(f"✅ Saved FAISS index at {index_path}")
    print(f"✅ Saved metadata at {meta_path}")


def semantic_search(query: str, model, index, df, top_k=5):
    """
    Performs a similarity search and returns top-k matching tickets.
    """
    q_vec = model.encode([query], normalize_embeddings=True)
    D, I = index.search(np.array(q_vec, dtype="float32"), k=top_k)
    results = df.iloc[I[0]].copy()
    results["Score"] = D[0]
    return results[["Ticket_ID", "Category", "Region", "Tower", "Score", "text_corpus"]]


# ─────────────── MAIN EXECUTION ─────────

if __name__ == "__main__":
    # 1️⃣ Load data
    df = load_text_corpus()

    # 2️⃣ Build embeddings
    model, vectors = build_embeddings(df["text_corpus"].tolist())

    # 3️⃣ Build FAISS index
    index = build_faiss_index(vectors)

    # 4️⃣ Save for later use (RAG pipeline)
    save_index(index, df["Ticket_ID"].tolist(), MODEL_NAME)

    # 5️⃣ Test search
    q = "network latency issue in Pune tower"
    print(f"\n🔍  TEST QUERY: {q}")
    result_df = semantic_search(q, model, index, df)
    print(result_df.head(5))
