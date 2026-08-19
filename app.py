# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from src.db.postgres import list_all_incidents
from src.agent.incident_agent import run_investigation


# Page Configuration
st.set_page_config(
    page_title="IncidentIQ — Agentic Incident Investigation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main():
    # Custom CSS for Premium SRE Dashboard Styling
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        
        code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }

        .main-header {
            background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 50%, #030712 100%);
            padding: 24px;
            border-radius: 14px;
            border: 1px solid #312e81;
            margin-bottom: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }
        
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #818cf8, #c084fc, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        
        .subtitle {
            color: #94a3b8;
            font-size: 1.0rem;
            margin-bottom: 16px;
        }

        .badge-container {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .pill-badge {
            display: inline-flex;
            align-items: center;
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        
        .pill-mcp {
            background-color: rgba(6, 182, 212, 0.15);
            color: #22d3ee;
            border: 1px solid rgba(6, 182, 212, 0.4);
        }

        .pill-rag {
            background-color: rgba(168, 85, 247, 0.15);
            color: #c084fc;
            border: 1px solid rgba(168, 85, 247, 0.4);
        }

        .pill-gemini {
            background-color: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
            border: 1px solid rgba(59, 130, 246, 0.4);
        }

        .pill-langgraph {
            background-color: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }

        .rca-card {
            background: linear-gradient(135deg, rgba(30, 27, 75, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
            border: 1px solid #4338ca;
            border-left: 5px solid #818cf8;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .evidence-item {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 12px 16px;
            margin-bottom: 8px;
            font-size: 0.95rem;
        }

        .log-error {
            color: #f87171;
            background: rgba(239, 68, 68, 0.1);
            padding: 6px 10px;
            border-radius: 6px;
            border-left: 3px solid #ef4444;
            margin-bottom: 6px;
            font-size: 0.88rem;
        }

        .log-warn {
            color: #fbbf24;
            background: rgba(245, 158, 11, 0.1);
            padding: 6px 10px;
            border-radius: 6px;
            border-left: 3px solid #f59e0b;
            margin-bottom: 6px;
            font-size: 0.88rem;
        }

        .log-info {
            color: #93c5fd;
            background: rgba(59, 130, 246, 0.1);
            padding: 6px 10px;
            border-radius: 6px;
            border-left: 3px solid #3b82f6;
            margin-bottom: 6px;
            font-size: 0.88rem;
        }

        .knowledge-card {
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 12px;
        }

        .stButton > button {
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            width: 100%;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            opacity: 0.92;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header Section
    st.markdown(
        """
        <div class="main-header">
            <div class="main-title">⚡ IncidentIQ — Agentic Incident Investigation System</div>
            <div class="subtitle">Evidence-Driven Root Cause Analysis correlating Supabase Telemetry via FastMCP with Operational Runbooks via Qdrant Cloud RAG.</div>
            <div class="badge-container">
                <span class="pill-badge pill-langgraph">LangGraph Orchestration</span>
                <span class="pill-badge pill-mcp">FastMCP ➔ Supabase PostgreSQL</span>
                <span class="pill-badge pill-rag">Qdrant Cloud Vector RAG</span>
                <span class="pill-badge pill-gemini">Google Gemini LLM</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Fetch available incidents from Supabase PostgreSQL
    try:
        incidents = list_all_incidents()
    except Exception:
        incidents = [
            {
                "incident_id": "INC-2024-817",
                "title": "Payment API — HTTP 500 Spike & Connection Timeout",
                "service": "payment-service",
                "severity": "critical",
                "status": "active",
                "description": "Spike in HTTP 500 responses on POST /v1/charges. Customers unable to complete checkout.",
                "start_time": datetime.utcnow(),
            },
            {
                "incident_id": "INC-2024-902",
                "title": "Auth Service — High Latency & Token Verification Spike",
                "service": "auth-service",
                "severity": "high",
                "status": "investigating",
                "description": "P99 latency on JWT authentication jumped from 5ms to 900ms.",
                "start_time": datetime.utcnow(),
            },
            {
                "incident_id": "INC-2024-945",
                "title": "Order Service — Cascading Deadlocks on High Concurrency",
                "service": "order-service",
                "severity": "medium",
                "status": "mitigated",
                "description": "Inventory reservation locks causing deadlocks on concurrent flash sale checkout.",
                "start_time": datetime.utcnow(),
            },
            {
                "incident_id": "INC-2024-950",
                "title": "Cache Layer — Stampede causing DB Overload",
                "service": "cache-layer",
                "severity": "high",
                "status": "investigating",
                "description": "Mass cache eviction of product catalog resulted in a cache stampede, overloading the primary database with read queries.",
                "start_time": datetime.utcnow(),
            },
            {
                "incident_id": "INC-2024-960",
                "title": "Gateway Service — 3rd-Party Rate Limiting & 503s",
                "service": "gateway-service",
                "severity": "critical",
                "status": "active",
                "description": "Upstream SMS provider returning 429 Rate Limited, cascading into 503s for all user registration flows.",
                "start_time": datetime.utcnow(),
            },
            {
                "incident_id": "INC-2024-970",
                "title": "Worker Node — Memory Leak & OOMKilled",
                "service": "worker-node",
                "severity": "medium",
                "status": "investigating",
                "description": "Gradual memory bloat in the report generation worker leading to constant OOMKilled pod restarts.",
                "start_time": datetime.utcnow(),
            },
        ]

    incident_map = {f"[{i['severity'].upper()}] {i['incident_id']} — {i['title']}": i["incident_id"] for i in incidents}

    # Sidebar: Incident Selector & Controls
    with st.sidebar:
        st.markdown("### 🔍 Select Incident to Investigate")
        selected_label = st.selectbox(
            "Active Incidents (from Supabase)",
            options=list(incident_map.keys()),
            index=0,
        )
        selected_incident_id = incident_map[selected_label]
        selected_incident = next((i for i in incidents if i["incident_id"] == selected_incident_id), incidents[0])

        st.markdown("---")
        st.markdown("#### 📋 Incident Details")
        st.markdown(f"**ID**: `{selected_incident['incident_id']}`")
        st.markdown(f"**Service**: `{selected_incident['service']}`")
        severity_color = "red" if selected_incident['severity'] == "critical" else "orange"
        st.markdown(f"**Severity**: :{severity_color}[{selected_incident['severity'].upper()}]")
        st.markdown(f"**Status**: `{selected_incident['status'].capitalize()}`")
        st.caption(f"**Description**: {selected_incident['description']}")

        st.markdown("---")
        st.markdown("#### 💬 Investigation Query")
        query_input = st.text_area(
            "Question for Incident Agent",
            value=f"Why did {selected_incident['service']} experience this issue? Correlate logs, metrics, and historical runbooks to identify root cause and recommended actions.",
            height=110,
        )

        investigate_btn = st.button("🚀 Investigate Incident", use_container_width=True)

    # Main Application Body
    if investigate_btn or "investigation_state" in st.session_state:
        if investigate_btn:
            with st.spinner("🤖 Agentic workflow in progress... Gathering telemetry via MCP and querying Qdrant RAG..."):
                result_state = run_investigation(
                    incident_id=selected_incident_id,
                    query=query_input,
                )
                st.session_state["investigation_state"] = result_state
                st.session_state["last_incident_id"] = selected_incident_id

        state = st.session_state.get("investigation_state")

        if state:
            # Agent Execution Trace
            with st.expander("🔄 Agent Orchestration Trace (LangGraph + FastMCP + Qdrant RAG)", expanded=False):
                for step in state.investigation_steps or []:
                    if "MCP Tool" in step:
                        st.markdown(f"🟢 **[MCP ➔ Supabase]** `{step}`")
                    elif "Qdrant RAG" in step:
                        st.markdown(f"🟣 **[Vector RAG ➔ Qdrant]** `{step}`")
                    elif "Gemini" in step:
                        st.markdown(f"🔵 **[LLM Synthesis ➔ Gemini]** `{step}`")
                    else:
                        st.markdown(f"⚙️ `{step}`")

            # Top Executive Summary Card
            st.markdown(
                f"""
                <div class="rca-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 1.3rem; font-weight: 700; color: #f8fafc;">🎯 Root Cause Analysis</span>
                        <span class="pill-badge pill-gemini">Confidence: {state.confidence_score or 'High'}</span>
                    </div>
                    <div style="font-size: 1.15rem; font-weight: 600; color: #e0e7ff; margin-bottom: 14px;">
                        {state.root_cause}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Tabs for Multi-Source Evidence Exploration
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📌 Evidence & Action Plan",
                "📊 MCP Operational Telemetry (PostgreSQL)",
                "📚 Retrieved Knowledge (Qdrant RAG)",
                "🕸️ Service Topology & Health",
                "📄 Raw JSON Payload",
            ])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🔍 Corroborating Evidence")
                    for ev in state.evidence_points or []:
                        st.markdown(f"<div class='evidence-item'>• {ev}</div>", unsafe_allow_html=True)

                with col2:
                    st.markdown("#### 🛠️ Recommended Action Plan")
                    for idx, act in enumerate(state.recommended_actions or [], 1):
                        badge = "Immediate Action" if idx <= 2 else "Long-term Prevention"
                        st.markdown(f"<div class='evidence-item'><b>[{badge}]</b> {act}</div>", unsafe_allow_html=True)

            with tab2:
                st.markdown("#### ⚡ Live Telemetry from Supabase PostgreSQL (via MCP)")
                subtab_metrics, subtab_logs = st.tabs(["Timeseries Metrics", "System Error Logs"])

                with subtab_metrics:
                    metrics = state.telemetry_metrics or []
                    if metrics:
                        df_metrics = pd.DataFrame(metrics)
                        if "timestamp" in df_metrics.columns:
                            df_metrics["timestamp"] = pd.to_datetime(df_metrics["timestamp"])
                            df_metrics = df_metrics.sort_values("timestamp")
                        st.dataframe(df_metrics, use_container_width=True, hide_index=True)
                    else:
                        st.info("No metric timeseries entries found for this service.")

                with subtab_logs:
                    logs = state.telemetry_logs or []
                    if logs:
                        for l in logs:
                            level = l.get("level", "INFO").upper()
                            ts = str(l.get("timestamp", ""))[:19]
                            msg = l.get("message", "")
                            css_class = "log-error" if level == "ERROR" else ("log-warn" if level == "WARN" else "log-info")
                            st.markdown(
                                f"<div class='{css_class}'><b>[{ts}] [{level}]</b> {msg}</div>",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("No recent error logs found.")

            with tab3:
                st.markdown("#### 🧠 Operational Knowledge Retrieved from Qdrant Cloud (Vector RAG)")
                knowledge = state.retrieved_knowledge or []
                if knowledge:
                    for k in knowledge:
                        score = k.get("score", 0.0)
                        doc_type = k.get("doc_type", "doc").upper()
                        title = k.get("title", "")
                        source = k.get("source", "")
                        content = k.get("content", "")

                        st.markdown(
                            f"""
                            <div class="knowledge-card">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span style="font-weight: 600; color: #f1f5f9; font-size: 1.05rem;">{title}</span>
                                    <div>
                                        <span class="pill-badge pill-rag">{doc_type}</span>
                                        <span class="pill-badge pill-langgraph">Cosine: {score}</span>
                                    </div>
                                </div>
                                <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 8px;">Source: <code>{source}</code></div>
                                <div style="color: #cbd5e1; font-size: 0.92rem; white-space: pre-wrap;">{content}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No matching knowledge documents retrieved.")

            with tab4:
                st.markdown("#### 🏗️ Service Topology (from Supabase PostgreSQL)")
                srv = state.service_health or {}
                if srv and "error" not in srv:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Service Name", srv.get("service_name", "N/A"))
                    c2.metric("Service Owner", srv.get("owner", "N/A"))
                    c3.metric("Architecture Tier", srv.get("tier", "N/A").upper())

                    st.markdown(f"**Description**: {srv.get('description', '')}")
                    deps = srv.get("dependencies", [])
                    st.markdown("**Dependencies**:")
                    for d in deps:
                        st.markdown(f"- 🔗 `{d}`")
                else:
                    st.info("Service topology information not available.")

            with tab5:
                st.markdown("#### 📋 Complete Investigation State JSON")
                st.json(state.model_dump(mode="json"))

    else:
        # Empty State Guidance
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px; background: rgba(15, 23, 42, 0.4); border-radius: 14px; border: 1px dashed #334155;">
                <div style="font-size: 3.5rem; margin-bottom: 16px;">⚡</div>
                <h2 style="color: #f8fafc; margin-bottom: 8px;">IncidentIQ is Ready</h2>
                <p style="color: #94a3b8; max-width: 600px; margin: 0 auto 24px auto;">
                    Select an active incident from the sidebar and click <b>Investigate Incident</b>. 
                    The LangGraph agent will query live Supabase telemetry using <b>FastMCP</b>, retrieve runbooks from <b>Qdrant Cloud RAG</b>, and synthesize a root-cause analysis with <b>Google Gemini</b>.
                </p>
                <div style="display: flex; justify-content: center; gap: 16px;">
                    <span class="pill-badge pill-mcp">FastMCP Tools</span>
                    <span class="pill-badge pill-rag">Qdrant Vector DB</span>
                    <span class="pill-badge pill-gemini">Gemini LLM Reasoning</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
