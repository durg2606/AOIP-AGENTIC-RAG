import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import PromptTemplate

from app.chat_utils import get_chat_model, ask_chat_model
from app.config import EURI_API_KEY
from monitoring.logger import monitor


# ─────────────── CONFIGURATION ──────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "faiss_index"

INDEX_PATH = INDEX_DIR / "ticket_index.faiss"
META_PATH = INDEX_DIR / "ticket_index.pkl"

MODEL_DEFAULT = "all-MiniLM-L6-v2"


# ─────────────── LOAD INDEX ─────────────
def load_faiss_index():
    """
    Loads saved FAISS index + metadata + ticket corpus.
    """
    if not INDEX_PATH.exists():
        raise FileNotFoundError(f"❌ FAISS index missing: {INDEX_PATH}")

    if not META_PATH.exists():
        raise FileNotFoundError(f"❌ Metadata file missing: {META_PATH}")

    with open(META_PATH, "rb") as f:
        meta = pickle.load(f)

    model_name = meta.get("MODEL", MODEL_DEFAULT)

    model = SentenceTransformer(model_name)
    index = faiss.read_index(str(INDEX_PATH))

    parquet_path = DATA_DIR / "tickets_clean.parquet"
    if not parquet_path.exists():
        raise FileNotFoundError(f"❌ Missing parquet file: {parquet_path}")

    df = pd.read_parquet(parquet_path)

    print(f"📦 Loaded FAISS index with {index.ntotal} vectors")
    print(f"🧠 Embedding model: {model_name}")

    return index, model, df


# ─────────────── RETRIEVAL ──────────────
def retrieve_context(query: str, model, index, df, top_k: int = 5) -> str:
    """
    Retrieves top-k similar tickets from FAISS.
    """
    q_vec = model.encode([query], normalize_embeddings=True)
    q_vec = np.array(q_vec, dtype="float32")

    distances, indices = index.search(q_vec, k=top_k)

    retrieved_rows = df.iloc[indices[0]][
        ["Ticket_ID", "Description", "Category", "Region", "Tower"]
    ]

    context_lines = []
    for _, row in retrieved_rows.iterrows():
        line = (
            f"[{row['Ticket_ID']}] "
            f"{row['Description']} "
            f"({row['Category']} · {row['Region']} · {row['Tower']})"
        )
        context_lines.append(line)

    print(f"🔍 Retrieved {len(context_lines)} relevant tickets")

    return "\n".join(context_lines)


# ─────────────── PROMPT ─────────────────
QA_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=(
        "You are an expert Ops Analyst AI specializing in enterprise ticket intelligence.\n\n"
        "Use ONLY the provided ticket evidence to answer.\n\n"
        "Ticket Context:\n{context}\n\n"
        "Question:\n{question}\n\n"
        "Provide:\n"
        "1. Root cause\n"
        "2. Trend insight\n"
        "3. Recommended mitigation\n"
        "4. Business impact\n\n"
        "Answer in concise, operationally actionable language."
    ),
)


def build_rag_prompt(context: str, question: str) -> str:
    """
    Builds final prompt string.
    """
    return QA_PROMPT.format(
        context=context,
        question=question
    )


# ─────────────── MAIN RAG ───────────────
@monitor("RAGQuery")
def query_rag(question: str) -> str:
    """
    Full RAG pipeline:
    retrieval → prompt → EURI LLM response
    """
    # Load retrieval assets
    index, model, df = load_faiss_index()

    # Retrieve relevant evidence
    context = retrieve_context(question, model, index, df)

    # Build final prompt
    prompt = build_rag_prompt(context, question)

    # Initialize EURI chat model
    chat_model = get_chat_model(EURI_API_KEY)

    # Query model
    answer = ask_chat_model(chat_model, prompt)

    return answer


# ─────────────── TEST RUN ───────────────
if __name__ == "__main__":
    print("🚀 Starting AOIP RAG test...")

    sample_q = "What were common issues in Mumbai Infrastructure tickets?"

    response = query_rag(sample_q)

    print("\n🧠 QUESTION:")
    print(sample_q)
    print("─" * 60)
    print("📌 ANSWER:")
    print(response)
