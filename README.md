# ⚡ IncidentIQ — Agentic AI Incident Investigation System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-green.svg)](https://github.com/langchain-ai/langgraph)
[![MCP](https://img.shields.io/badge/Protocol-Model_Context_Protocol_(FastMCP)-cyan.svg)](https://modelcontextprotocol.io/)
[![Qdrant Cloud](https://img.shields.io/badge/Vector_DB-Qdrant_Cloud-purple.svg)](https://cloud.qdrant.io/)
[![Supabase](https://img.shields.io/badge/Database-Supabase_PostgreSQL-emerald.svg)](https://supabase.com/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google_Gemini-blue.svg)](https://ai.google.dev/)

**IncidentIQ** is a production-style, agentic Site Reliability Engineering (SRE) incident investigation system. It automatically investigates software outages and performance regressions by synthesizing **live structured operational telemetry** (via FastMCP tools querying Supabase PostgreSQL) with **unstructured historical operational knowledge** (via Vector RAG querying Qdrant Cloud) using **LangGraph** orchestration and **Google Gemini** reasoning.

---

## 🎯 Target Architecture

```mermaid
flowchart TD
    User([User / SRE Engineer]) -->|Select Incident & Query| UI[Streamlit UI Dashboard]
    UI -->|Trigger Workflow| Agent[LangGraph Incident Agent]
    
    subgraph Agentic Orchestration Layer
        Agent -->|1. Fetch Live Telemetry| MCP[FastMCP Tool Client]
        Agent -->|2. Semantic Search| RAG[Qdrant Cloud Vector RAG]
        Agent -->|3. Multi-Evidence Reasoning| LLM[Google Gemini LLM]
    end
    
    subgraph Operational Data Layer
        MCP -->|Query SQL Data| PG[(Supabase PostgreSQL)]
        PG --> Logs[(Logs Table)]
        PG --> Metrics[(Metrics Timeseries)]
        PG --> Incidents[(Incidents Table)]
        PG --> Topology[(Services Topology)]
    end
    
    subgraph Operational Knowledge Base
        RAG -->|Cosine Similarity Search| Qdrant[(Qdrant Cloud)]
        Qdrant --> Runbooks[Runbooks & SOPs]
        Qdrant --> Postmortems[Historical Postmortems]
        Qdrant --> ServiceDocs[Service Architecture Docs]
    end

    LLM -->|Synthesize RCA| Report[Evidence-Backed Root Cause Analysis + Remediation Plan]
    Report --> UI
```

---

## ✨ Key Features

- 🤖 **LangGraph Orchestration**: Dynamic, stateful agent workflow managing the investigation lifecycle from telemetry gathering to knowledge retrieval and final synthesis.
- ⚡ **FastMCP Tool Interface**: Adheres to the Model Context Protocol (MCP) specification to query live telemetry (`get_incident`, `get_logs`, `get_metrics`, `get_service_health`, `get_incident_history`) over hosted Supabase PostgreSQL.
- 🧠 **Qdrant Cloud Vector RAG**: Real semantic vector search with `gemini-embedding-001` over modular runbooks, historical postmortems, and architecture specs.
- 🎯 **Evidence-Driven Root Cause Analysis (RCA)**: Correlates deployment commits, error spikes, and saturation thresholds with past incident signatures (e.g. Incident #817) to provide high-confidence mitigation steps.
- 🖥️ **Interactive Streamlit UI**: Real-time investigation timeline, metric timeseries graphs, color-coded error log stream, and interactive knowledge snippet explorer.
- ☁️ **Single Architecture for Local & Cloud**: Identical hosted services (Qdrant Cloud, Supabase PostgreSQL, Gemini API) work locally and on **Streamlit Community Cloud** with zero code modifications.

---

## 📂 Project Structure

```
IncidentIQ/
├── .gitignore                      # Strictly excludes secrets (.env, curl.txt)
├── requirements.txt                # Python 3.12+ production dependencies
├── README.md                       # Architecture & Documentation
├── app.py                          # Streamlit UI Dashboard
│
├── knowledge/                      # Operational Knowledge Base (RAG)
│   ├── runbooks/                   # Database connection pool, high latency, payment failure
│   ├── postmortems/                # Historical incidents (INC-817, INC-402, INC-510)
│   └── services/                   # Service topology & dependency documentation
│
└── src/
    ├── config.py                   # Centralized secrets & connection configuration
    ├── db/
    │   ├── postgres.py             # Supabase PostgreSQL client & query helpers
    │   ├── schema.sql              # PostgreSQL DDL for operational telemetry
    │   └── seed_data.py            # Idempotent DB seeder for synthetic incident telemetry
    ├── rag/
    │   ├── indexer.py              # Operational doc chunker & Qdrant Cloud indexer
    │   └── retriever.py            # Semantic similarity search with score ranking
    ├── mcp_tools/
    │   ├── server.py               # FastMCP tool server querying PostgreSQL
    │   └── client.py               # MCP client interface for LangGraph
    └── agent/
        ├── state.py                # LangGraph typed state schema
        └── incident_agent.py       # LangGraph agent workflow & Gemini multi-model synthesis
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/<your-username>/IncidentIQ.git
cd IncidentIQ

# Create & activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Credentials (`.env`)
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
DATABASE_URL=postgresql://postgres:your_password@db.your_ref.supabase.co:5432/postgres
```

### 3. Initialize Database & Vector Store
```bash
# Seed Supabase PostgreSQL with operational telemetry
python -m src.db.seed_data

# Index knowledge base into Qdrant Cloud
python -m src.rag.indexer
```

### 4. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---
