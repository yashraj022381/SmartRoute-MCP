# 🧭 SmartRoute-MCP
A cost-optimized, MCP-enabled multi-agent AI system with live routing visibility.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-purple.svg)](https://langchain-ai.github.io/langgraph/)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-orange.svg)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C.svg)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800.svg)](https://grafana.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

- SmartRoute-MCP analyzes every incoming query, routes it to the cheapest model capable of handling it well, and orchestrates a Researcher → Writer → Reviewer agent team —       with the Reviewer able to send work back to whichever agent actually needs to fix it, based on whether the problem is factual or stylistic.

- Everything is wired together through the Model Context Protocol (MCP) for tool access, and fully observable through Prometheus and Grafana.


📸 Screenshots

  
   | 1 - Streamlit Chat UI / Main Dashboard |
   |-------------------|
   | ![Streamlit Chat UI](docs/images/ui-chat1.png)  |
   | ![UI in Action - A1](docs/images/ui-chat2.png)  | 
   | ![UI in Action - B1](docs/images/ui-chat3a.png) |
   | ![UI in Action - B2](docs/images/ui-chat3b.png) |
   | ![UI in Action - B3](docs/images/ui-chat3c.png) |
   | ![UI in Action - B4](docs/images/ui-chat3d.png) |
   | ![UI in Action - B5](docs/images/ui-chat3e.png) |
   

  | 2 - Grafana Live Dashboard |
  |------------------------|
  | ![Grafana](docs/images/grafana-dashboard.png) |


  | 3 - Prometheus Targets |
  |--------------------|
  | ![Prometheus - 1](docs/images/prometheus1.png) |
  | ![Prometheus - 2](docs/images/prometheus2.png) |
  | ![Prometheus - 3](docs/images/prometheus3.png) | 
  | ![Prometheus - 4](docs/images/prometheus4.png) | 
  | ![Prometheus - 5](docs/images/prometheus5.png) | 

  | 4 - API DOCS (Swagger) |
  |----------------------|
  | ![Stats](docs/images/api-docs1.png)   |
  | ![Stats](docs/images/api-docs2.png)   |
  | ![Stats](docs/images/api-docs3a.png)  |
  | ![Stats](docs/images/api-docs3b.png)  |
  | ![Stats](docs/images/api-docs4.png)   |
  | ![Stats](docs/images/api-docs5a.png)  |
  | ![Stats](docs/images/api-docs5b.png)  |
  | ![Stats](docs/images/api-docs6.png)   |
  | ![Stats](docs/images/api-docs7.png)   |
  | ![Stats](docs/images/api-docs8.png)   |
  | ![Stats](docs/images/api-docs9.png)   |
  
  
  | 5 - Routing Decision Log |
  |----------------------|
  | ![Stats](docs/images/routing-stats1.png) |
  | ![Stats](docs/images/routing-stats2.png) |


✨ Features

 - Complexity-based routing — a lightweight classifier scores every query and routes it to a cheap local model (Ollama /        Llama 3.2) or a stronger cloud model (Groq), based on the actual topic's complexity — not the length of whatever wrapper     prompt an agent happens to be using internally.
  
 - Combined cost + latency objective — routing also accounts for real observed latency per tier, not cost alone, so a slow      "cheap" tier doesn't quietly become the worse choice.
  
 - Self-correcting agent team — Researcher → Writer → Reviewer via LangGraph. The Reviewer classifies issues as factual         (routed back to the Researcher for fresh information) or stylistic (routed back to the Writer), each with its own            independent one-revision budget so one type of fix never blocks the other.
   
 - Format- and relevance-aware research — trivial topics (e.g. a direct calculation) skip web search and article-length         padding entirely; search results that don't actually relate to the topic are treated as a failed search rather than          trusted blindly.
  
 - MCP tool server — exposes web search, sandboxed Python code execution, and semantic RAG search as standard MCP tools,        callable by any MCP client.
   
 - RAG research cache — Chroma vector store lets the Researcher reuse prior research for similar topics instead of re-          searching from scratch.
   
 - Adaptive threshold calibration — the classifier's weak/strong cutoff nudges itself over time based on real fallback rates.
 
 - Full observability — every routing decision is logged to SQLite and exposed as Prometheus metrics, visualized in Grafana     with live-updating dashboards.
   
 - One-command Docker deployment — API, UI, Prometheus, and Grafana all start together with docker-compose up .

 - Evaluation harness — compares routed cost/quality against an always-strong-model baseline across a batch of test queries

🏗️ Architecture
        User Query
            │
            ▼
   ┌─────────────────┐
   │  Complexity     │  ← Lightweight classifier
   │  Classifier     │
   └────────┬────────┘
            │
    ┌───────┴─────────┐
    │                 │
    Weak Tier  Strong Tier
     (Ollama)    (Groq)
    │                 │
    └────────┬────────┘
             ▼
┌─────────────────────────────┐
│   LangGraph Multi-Agent     │
│  Researcher → Writer →      │
│  Reviewer (self-correcting) │
└────────────┬────────────────┘
             │
             ▼
   Final Answer + Metrics
             │
     ┌───────┴───────┐
     ▼               ▼
Prometheus     Grafana Dashboards


🧰 Tech Stack

   Layer	                           Technology
 ______________________________________________________  
   Agent orchestration	              LangGraph
   API	                              FastAPI
   UI	                               Streamlit
   Local model	                      Ollama (Llama 3.2)
   Cloud model	                      Groq (openai/gpt-oss-120b)
   Tool protocol	                    MCP (Model Context Protocol)
   Vector store	                     ChromaDB
   Performance DB	                   SQLite
   Metrics	                          Prometheus
   Dashboards	                       Grafana
   Containerization	                 Docker + Docker Compose


📁 Project Structure

  smartroute-mcp/
  ├── agents/          # Researcher, Writer, Reviewer nodes + LangGraph wiring
  ├── api/             # FastAPI app
  ├── db/              # SQLite performance database
  ├── eval/            # Evaluation harness (routed vs always-strong)
  ├── mcp_server/      # MCP server (web search, code exec, RAG) + client
  ├── metrics/         # Prometheus metrics instrumentation
  ├── rag/             # Chroma vector store for research caching
  ├── router/          # Classifier, calibration, model registry, cost/latency routing
  ├── ui/              # Streamlit chat interface
  ├── Dockerfile
  ├── docker-compose.yml
  ├── prometheus.yml
  └── requirements.txt



🚀 Getting Started

 - Prerequisites
   . Docker Desktop
   . Ollama installed and running locally, with llama3.2:1b pulled:
  
      ollama pull llama3.2:1b
   
   . A Groq API key for the "strong" tier
     A free Groq API key

 - Configuration

   . Create a .env file in the project root:

    GROQ_API_KEY=your_key_here

 - Running with Docker (recommended)
  
     bash
     docker-compose up --build

 - Then open:

   Service	                 URL
 ___________________________________________________  
   UI (the app itself)	     http://localhost:8501
   API docs	                 http://localhost:8000/docs
   Prometheus	               http://localhost:9090
   Grafana	                 http://localhost:3000 (login: admin / admin)


 - See DOCKER.md for troubleshooting and full details.

   Running locally without Docker
   
   bash
   python -m venv .
   Scripts\activate          # Windows
   pip install -r requirements.txt

   # In one terminal:
   uvicorn api.main:app --reload --port 8000

   # In another terminal:
   streamlit run ui/app.py


📊 Observability: Prometheus & Grafana

 - Every routed query is instrumented and exposed at /metrics in Prometheus format. Once the stack is running:

   (i) Open Grafana at localhost:3000 (admin / admin)
  (ii) Add a Prometheus data source with URL http://prometheus:9090
 (iii) Build panels from these metrics:
      > smartroute_requests_total — request volume, by tier
      > smartroute_cost_usd_total — running cost, by tier
      > smartroute_request_latency_seconds — latency histogram, by tier
      > smartroute_fallbacks_total — how often the weak tier's response was too short and genuinely needed a strong-tier retry
  (iv) Route a few queries through the UI and watch the panels update live

 - Prometheus's own UI at localhost:9090 is also useful for ad-hoc exploration — check Status → Targets to confirm the API is being scraped successfully before building dashboards.

🧪 Evaluation

  - Run the evaluation harness to compare routed cost/quality against always using the strong model:

    bash
    python eval/run_eval.py

  - Results are saved to eval_results/latest_report.json.


🗺️ Roadmap

 - Originally planned future improvements:

   > Combined cost/latency routing objective (not cost alone)
   > Reviewer feedback routed back to the Researcher for factual issues, not only the Writer — with independent revision          budgets per issue type
   > Expanded MCP tool server (code execution, real RAG document store)
   > Real Prometheus + Grafana dashboard with historical graphs

   
📄 License

  MIT — see LICENSE for details.   

🙏 Acknowledgements

  - LangGraph for agent orchestration
  - Model Context Protocol for standardized tool access
  - Ollama & Groq for model inference
  - Prometheus + Grafana for observability
