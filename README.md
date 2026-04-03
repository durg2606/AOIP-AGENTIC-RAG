# 🧠 Agentic Operational Intelligence Platform (AOIP)

**Enterprise-grade multi-agent Retrieval-Augmented Generation (RAG) platform for IT Operations intelligence**

AOIP transforms raw IT operations data—tickets, SLA logs, feedback, and incident metadata—into **real-time KPI insights, root-cause diagnostics, and executive-ready reports**.

Built with **LangChain, FAISS, Sentence Transformers, Prometheus, LangFuse, Streamlit, and GPT-4.1-nano**, the platform combines **RAG retrieval, specialized analytical agents, observability, and automated reporting** into a production-oriented operational intelligence stack.

---

## 🚀 Key Capabilities

* 🔍 **Semantic ticket intelligence** using FAISS + MiniLM embeddings
* 📈 **KPI analytics** for SLA breach %, MTTR, CSAT, and trend drift
* 🧩 **Root Cause Analysis (RCA)** with severity clustering and issue distribution
* 📄 **Automated stakeholder reporting** in HTML + PDF
* 📊 **Interactive Streamlit dashboard** for operational monitoring
* 📡 **Full observability** with Prometheus metrics + LangFuse tracing
* 🐳 **Dockerized deployment** for reproducible enterprise environments

---

## 🏗️ Architecture Overview

```text
User Query
   → RAG Retriever (FAISS + MiniLM)
   → KPI Insight Agent
   → RCA Agent
   → Report Agent (HTML / PDF)
   → Outputs + Metrics + Dashboards
```

### ⚙️ Processing Flow

1. **Data Ingestion** → CSV → cleaned Parquet datasets
2. **Embedding Pipeline** → MiniLM sentence embeddings → FAISS index
3. **RAG Query Engine** → retrieve evidence → prompt → EURI GPT-4.1-nano
4. **Insight Agent** → SLA, MTTR, CSAT, breach analysis
5. **RCA Agent** → issue mapping, severity analysis, trend detection
6. **Report Agent** → Jinja2 HTML + ReportLab PDF generation
7. **Observability Layer** → Prometheus + LangFuse

---

## 📁 Project Structure

```text
AOIP-AGENTIC-RAG/
├── app/
│   ├── __init__.py
│   ├── chat_utils.py
│   └── config.py
│
├── dashboard/
│   └── dashboard_ui.py
│
├── data/
│   ├── tickets.csv
│   ├── sla_logs.csv
│   ├── root_cause.csv
│   ├── feedback.csv
│   ├── *.parquet
│   └── ticket_rootcause_links.csv
│
├── faiss_index/
│   ├── ticket_index.faiss
│   └── ticket_index.pkl
│
├── monitoring/
│   ├── __init__.py
│   └── logger.py
│
├── observability/
│   └── prometheus.yml
│
├── reports/
│   ├── *.html
│   └── *.pdf
│
├── data_loader.py
├── retriever_builder.py
├── rag_pipeline.py
├── insight_agent.py
├── rca_agent.py
├── report_agent.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🧩 Core Modules

| Module                      | Responsibility                                            |
| --------------------------- | --------------------------------------------------------- |
| `data_loader.py`            | ETL pipeline for cleaning CSV files and exporting Parquet |
| `retriever_builder.py`      | Builds MiniLM embeddings and FAISS vector index           |
| `rag_pipeline.py`           | Retrieval → prompting → EURI GPT inference                |
| `insight_agent.py`          | KPI and SLA analytics with trend visualization            |
| `rca_agent.py`              | Root-cause lookup, clustering, severity analysis          |
| `report_agent.py`           | HTML/PDF stakeholder reports                              |
| `monitoring/logger.py`      | Prometheus metrics + LangFuse tracing decorators          |
| `dashboard/dashboard_ui.py` | Streamlit dashboard frontend                              |

---

## 🤖 Language Model Configuration

| Parameter   | Value                                     | Purpose                                      |
| ----------- | ----------------------------------------- | -------------------------------------------- |
| Model       | `gpt-4.1-nano`                            | Low-latency reasoning and reporting          |
| Temperature | `0.7`                                     | Balanced factuality + analytical flexibility |

All LLM requests are routed through:

* `get_chat_model()`
* `ask_chat_model()`

This ensures:

* centralized auth
* retry logic
* traceability
* latency measurement
* secure model abstraction

---

## 🧠 Prompt Engineering Strategy

```text
You are an expert Ops Analyst AI specializing in enterprise ticket intelligence.
Use only the provided ticket evidence to answer.

Ticket Context:
{context}

Question:
{question}

Provide:
1. Root cause
2. Trend insight
3. Recommended mitigation
4. Business impact
```

### 🎯 Why this prompt works

* Restricts hallucination by grounding in retrieved ticket evidence
* Produces structured outputs for downstream reporting
* Aligns naturally with RCA and KPI workflows
* Easy to extend into JSON schema outputs later

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

### Core Dependencies

```text
pandas
numpy
faiss-cpu
sentence-transformers
langchain-core
jinja2
reportlab
plotly
python-dotenv
prometheus-client
langfuse
requests
streamlit
```

---

## ▶️ Local Development Workflow

### 1) Prepare datasets

```bash
python data_loader.py
```

### 2) Build embeddings + FAISS index

```bash
python retriever_builder.py
```

### 3) Run RAG pipeline

```bash
python rag_pipeline.py
```

### 4) Generate stakeholder report

```bash
python report_agent.py
```

### 5) Launch dashboard

```bash
streamlit run dashboard/dashboard_ui.py
```

---

## 🐳 Docker Deployment

### Build image

```bash
docker build -t aoip .
```

### Run container

```bash
docker run -p 8501:8501 aoip
```

### Docker Compose

```bash
docker-compose up --build
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics

| Metric                         | Type      | Description                    |
| ------------------------------ | --------- | ------------------------------ |
| `aoip_requests_total`          | Counter   | Total agent and RAG requests   |
| `aoip_request_latency_seconds` | Histogram | Component latency distribution |
| `aoip_errors_total`            | Counter   | Failed requests                |

### LangFuse Tracing

Tracks:

* prompt lineage
* retrieval context
* token usage
* latency
* failures
* RCA decision flow

This is critical for **production debugging and agent explainability**.

---

## ⚖️ Design Decisions & Trade-offs

| Decision   | Choice                | Trade-off                                            |
| ---------- | --------------------- | ---------------------------------------------------- |
| Embeddings | MiniLM-L6-v2          | Fast CPU inference, moderate semantic depth          |
| Vector DB  | FAISS IndexFlatIP     | Deterministic and fast, less scalable than HNSW      |
| LLM        | GPT-4.1-nano          | Low latency, smaller reasoning depth than full GPT-4 |
| Reporting  | Jinja2 + ReportLab    | Excellent offline exports, more template maintenance |
| Monitoring | Prometheus + LangFuse | Strong observability, extra infra complexity         |

---

## 📌 Example Output

```text
📦 Loaded FAISS index with 2000 vectors
🔍 Retrieved 5 relevant tickets
📊 Breach Rate = 7.35% (189/2572)
📈 MTTR Trend = +11.2% WoW
🚨 Dominant RCA = Database connection timeout
✅ HTML report saved → reports/Report_TCK00025.html
📄 PDF report created → reports/Report_TCK00025.pdf
```


## 👤 Author

**Durga Charan Mishra**

🎓 IIT Jodhpur MBA
📊 AI, Analytics & Operational Intelligence Professional

---

## ⭐ Business Value

AOIP is designed for **enterprise ITSM, SRE, Ops Analytics, and CIO reporting workflows** where explainable AI must connect **ticket evidence → diagnostics → mitigation → stakeholder reporting**.

It is especially effective for:

* IT service desk intelligence
* SLA governance
* recurring incident RCA
* executive ops dashboards
* service quality trend reporting
* operational risk visibility

---
