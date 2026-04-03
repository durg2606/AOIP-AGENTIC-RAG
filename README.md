🧠 Agentic Operational Intelligence Platform (AOIP)
An enterprise‑grade multi‑agent Retrieval‑Augmented Generation (RAG) system that automates KPI analytics, root‑cause diagnostics, and stakeholder reporting for IT Operations using LangChain, FAISS, and EURI GPT‑4.1‑nano.

🚀 Overview
AOIP turns raw operational data (tickets, SLA logs, feedback) into real‑time, intelligent insights.
It uses model‑driven RAG retrieval, analytical agents, and automated reporting to deliver explainable, actionable intelligence.



User Query 
   → RAG Retriever (FAISS + MiniLM)
   → KPI Insight Agent
   → RCA Agent
   → Report Agent (HTML / PDF)
   → Outputs + Metrics + Dashboards
🧩 Core Components
Module	Responsibility
data_loader.py	ETL – loads and cleans CSV datasets; saves Parquet versions.
retriever_builder.py	Builds Sentence‑Transformer embeddings and FAISS index.
rag_pipeline.py	Retrieval → Prompt → Query to EURI GPT‑4.1‑nano → Response.
insight_agent.py	SLA & KPI metrics analysis and trend visualization.
rca_agent.py	Root cause lookup and severity distribution analysis.
report_agent.py	Combines KPI + RCA into HTML and PDF reports (Jinja2 + ReportLab).
monitoring/logger.py	Prometheus metrics & LangFuse trace integration via @monitor decorator.
app/chat_utils.py	Connects to EURI API (GPT‑4.1‑nano) with temperature = 0.7.
dashboard/dashboard_ui.py	Streamlit‑ready frontend (dashboard & reports).
⚙️ Language Model Configuration
Parameter	Setting	Description
Model	gpt-4.1-nano	Lightweight GPT‑4 variant hosted via EURI API for low latency.
Temperature	 0.7	Moderate creativity for balanced trend and insight generation.
API Endpoint	 [api.euri.ai](https://api.euri.ai/v1/chat/completions)	Invoked through get_chat_model() and ask_chat_model() in app/chat_utils.py.
All RAG requests go through these functions, ensuring secure and traceable API calls.

🧱 Project Structure


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
│   ├── tickets.csv / .parquet
│   ├── sla_logs.csv / .parquet
│   ├── root_cause.csv / .parquet
│   ├── feedback.csv / .parquet
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
├── observability/prometheus.yml
├── reports/                 # auto‑generated HTML & PDF reports
│
├── data_loader.py
├── retriever_builder.py
├── rag_pipeline.py
├── insight_agent.py
├── rca_agent.py
├── report_agent.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
⚗️ Core Workflow
1. Data Ingestion → CSV ➡ clean ➡ Parquet
2. Embedding Builder → MiniLM Sentence‑Transformers ➡ FAISS index
3. RAG Pipeline → retrieve context + prompt ➡ gpt‑4.1‑nano
4. Insight Agent → KPI calculations (breach %, resolution time, CSAT)
5. RCA Agent → root‑cause mapping and severity plots
6. Report Agent → HTML & PDF reports (Jinja2 + ReportLab)
7. Monitoring → Prometheus metrics and LangFuse traces.

🧠 Prompt Template (Excerpt)
text


You are an expert Ops Analyst AI specializing in enterprise ticket intelligence.  
Use only the provided ticket evidence to answer.
Ticket Context:
{context}
Question:
{question}
Provide:
1. Root cause
2. Trend insight
3. Recommended mitigation
4. Business impact
🔐 Environment Variables (.env)
Create .env at project root and store private keys:

env


EURI_API_KEY=your_euri_key_here
OPENAI_API_KEY=optional_fallback
.env is ignored via .gitignore, keeping keys safe when pushing to GitHub.

🧰 Requirements Summary


pandas               numpy
faiss-cpu            sentence-transformers
langchain-core       jinja2
reportlab            plotly
python-dotenv        prometheus-client
langfuse             requests
▶️ Run Locally
1. Set up the environment
bash


pip install -r requirements.txt
2. Prepare cleaned data
bash


python data_loader.py
3. Generate sentence embeddings + index
bash


python retriever_builder.py
4. Run RAG query
bash


python rag_pipeline.py
5. Generate Report
bash


python report_agent.py
6. (Option) Run Dashboard
bash


streamlit run dashboard/dashboard_ui.py
💾 Docker Usage
bash


docker build -t aoip .
docker run -p 8501:8501 -p 9100:9100 --env-file .env aoip
Access:

Streamlit UI → [localhost](http://localhost:8501)
Prometheus metrics → [localhost](http://localhost:9100/metrics)
📊 Monitoring Metrics
Metric	Description
aoip_requests_total	total RAG/Agent calls processed
aoip_request_latency_seconds	latency (histogram, per component)
status (trace)	success / error via LangFuse
🧩 Design Choices & Trade‑offs
Decision	Rationale
MiniLM‑L6‑v2 Embeddings	Fast CPU embedding – best balance between semantic quality and speed.
FAISS IndexFlatIP	Simple and deterministic; upgrade to IVF/HNSW for scale.
EURI GPT‑4.1‑nano	Cost‑efficient GPT‑4 variant with low latency.
Temperature = 0.7	Balances creativity with factual reporting.
Jinja2 + ReportLab	Offline generation of print‑ready reports.
Prometheus + LangFuse	Full observability and traceability for production.
🧾 Sample Output


📦 Loaded FAISS index with 2000 vectors
🔍 Retrieved 5 relevant tickets
📊 Breach Rate = 7.35% (189/2572)
✅ HTML report saved → reports/Report_TCK00025.html
📄 PDF report created → reports/Report_TCK00025.pdf

👤 Author
Durga Charan Mishra
🎓 IIT Jodhpur MBA  |  AI & Analytics Professional