<<<<<<< HEAD
# 🔎 Autonomous Research Assistant

**Live Demo:** [🚀 outskill-c5-g2-attempt1.streamlit.app](https://outskill-c5-g2-attempt1.streamlit.app/)

**Recorded Demo:** [🎥 Watch the Video](https://drive.google.com/file/d/1kRIWI1gYfkmCpJd0hfzkjy29lE_CCpw6/view?usp=sharing)

**LangSmith Agent Trace Dashboard:** [📊 View Live Multi-Agent Trace](https://smith.langchain.com/o/61e19ebd-9d92-4671-9643-91e677fcf228/dashboards/projects/abbe4f82-712c-4a96-a849-09515d63eb98)

An autonomous research system that searches the web, academic papers, and local documents, evaluates sources, and synthesizes long, multi-step answers. It produces comprehensive, cited reports with a professional UI.

Unlike simple RAG implementations, this agentic system uses **real external APIs** to search the live web and academic databases, and makes dynamic routing decisions to process multi-hop investigations efficiently.

## 🚀 Streamlit Interface

The project features a modern, real-time tracking interface for interactive research sessions.

### Specialized Agents:
The system orchestrates **5 specialized agents** within a LangGraph Directed Acyclic Graph (DAG):
- **Research Planner**: Decomposes complex queries into manageable sub-questions and sets the dynamic tool routing strategy based on the query type.
- **Dynamic Retriever**: Executes parallel tool calls across the Web (Tavily), Academic sources (ArXiv), and Local Knowledge Base (ChromaDB).
- **Critical Analyst**: Filters noise, validates facts, flags contradictions between sources, and structures raw findings.
- **Insight Generator**: Generates chain-of-thought reasoning, identifies hypotheses, and draws strategic actionable insights.
- **Report Builder**: Compiles all insights and filtered facts into a structured, cite-rich final Markdown report.

### UI Capabilities:
- **Real-Time Agent Status**: Real-time feedback showing which specialized agent is currently working and its intermediate outputs.
- **🗺️ Routing Map**: Transparency into why the Planner chose specific tools for every sub-query.
- **Interactive Document Viewer**: View the raw document chunks retrieved, filterable by their source (Web, ArXiv, or Local).
- **Knowledge Base Ingestion**: An upload widget to ingest PDFs directly into a local ChromaDB instance without any cloud embedding costs.
- **🤖 Model Selection**: Choose from various Free/Paid LLMs via OpenRouter dynamically.
- **⏱️ Research Timing**: Displays the exact duration taken to generate the report and metrics on chunks processed.

---

## 💻 Deployment

### Local Deployment
To run the application locally on your machine:

1. **Prerequisites**: Ensure you have Python 3.11+ and [uv](https://docs.astral.sh/uv/) installed.
2. **Install Dependencies**:
   ```bash
   uv sync
   ```
3. **Configure Environment**: Create a `.env` file in the root directory (see [Configuration](#configuration)).
4. **Launch the App**:
   ```bash
   uv run streamlit run app.py
   ```
   The app will be available at `http://localhost:8501`.

### Running Tests
To run the automated validation suite locally:
```bash
uv run pytest tests/ -v
```
See our [Testing Guide](tests/TESTS.md) for complete details on UI and system integration coverage.

### Streamlit Community Cloud (Deployment)
To deploy this agent to the **Streamlit Community Cloud**:

1. **Push to GitHub**: Ensure your `app.py`, `pyproject.toml`, `uv.lock` and `.streamlit` config are committed to your repository.
2. **Connect to Streamlit**:
   - Go to [share.streamlit.io](https://share.streamlit.io/).
   - Click **"New App"** and select your repository and branch.
   - Set the Main file path to `app.py`.
3. **Secrets Management**:
   - In the Streamlit deployment settings, go to **"Secrets"**.
   - Copy the contents of your `.env` file into the secrets box (Streamlit will automatically map these to environment variables).
4. **Deploy**: Click **"Deploy!"**.

---

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# Required: OpenRouter API key for LLM access
OPENROUTER_API_KEY=your_openrouter_key_here

# Required: Tavily API key for live web search
TAVILY_API_KEY=your_tavily_key_here

# Optional: Override the default model
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

**Free API Keys:**
- OpenRouter: [https://openrouter.ai/](https://openrouter.ai/)
- Tavily: [https://tavily.com/](https://tavily.com/) (1000 free searches/month)

*(Note: ChromaDB and FastEmbed run completely locally and do not require API keys).*

---

## 🛠️ Project Structure

```
.
├── app.py                     # Streamlit UI entry point & Pipeline integration
├── core/                      # LangGraph DAG compilation and State schema
├── agents/                    # Multi-agent nodes (Planner, Retriever, etc.)
├── tools/                     # Web, ArXiv, and Local ChromaDB tool abstractions
├── llm/                       # OpenRouter configurations and model factory
├── chroma_db/                 # Local directory for Vector Store (auto-generated)
├── pyproject.toml             # uv dependencies definition
├── .env                       # API keys (DO NOT COMMIT)
└── .gitignore                 # Excludes .env, .venv, chroma_db, etc.
```

---

## 📚 Documentation

For a deeper dive into the system's design, patterns, and logic, please refer to the following guides:

**1. Requirements & Scope**
- [Product Requirements Document](PRD.md) — Core requirements mapped to agent implementations and additional platform features.
- [Features Guide](FEATURES.md) — Detailed list of tool features, integrations, and customization options.

**2. Architecture & Design**
- [System Architecture](ARCHITECTURE.md) — High-level system design, security, and deployment workflows.
- [Agents Guide](agents/Agents.md) — Topology, responsibilities, and visual flows for all specialized agents.

**3. Implementation Details**
- [Code Guide](CODE.md) — LangGraph orchestration patterns, state design, and tool integrations.
- [Core Logic Component](core/CORE.md) — Core application execution mechanics.
- [LLM Integrations](llm/LLM.md) — AI model configurations and routing.
- [Tools Configuration](tools/TOOLS.md) — Tool abstractions for the Retrieval system.

**4. Testing & Validation**
- [Testing Guide](tests/TESTS.md) — Overview of the automated testing suite and methodologies.

---

## 👥 Credits

### Developers
Developed by **Outskills Batch C5 Group 2**:
1. Arojeet Sengupta
2. Ravikant Badghaiya
3. Jayanth P
4. Abhinav Upadhyay
5. Mohammed Jameel
6. Shreya Gupta
7. Raajesh Kumar

### Mentors and Instructors
1. Ishan Dutta
2. King Sidharth
3. Paras Madan
4. Srishti Gureja
5. Dileep Karri
6. Antaripa Saha
7. Divij Bajaj
8. Akhil Alampally
9. Karthik Mehra
10. Sham Kulkarni

### Tools and Platforms
Built using:
- LangGraph
- LangChain
- OpenRouter
- tavily.com
- LangSmith
- Streamlit.io
- Antigravity
- Claude Code
=======
# 🔎 Autonomous Research Assistant

**Live Demo:** [🚀 outskill-c5-g2-attempt1.streamlit.app](https://outskill-c5-g2-attempt1.streamlit.app/)

**LangSmith Agent Trace Dashboard:** [📊 View Live Multi-Agent Trace](https://smith.langchain.com/o/61e19ebd-9d92-4671-9643-91e677fcf228/dashboards/projects/abbe4f82-712c-4a96-a849-09515d63eb98)

An autonomous research system that searches the web, academic papers, and local documents, evaluates sources, and synthesizes long, multi-step answers. It produces comprehensive, cited reports with a professional UI.

Unlike simple RAG implementations, this agentic system uses **real external APIs** to search the live web and academic databases, and makes dynamic routing decisions to process multi-hop investigations efficiently.

## 🚀 Streamlit Interface

The project features a modern, real-time tracking interface for interactive research sessions.

### Specialized Agents:
The system orchestrates **5 specialized agents** within a LangGraph Directed Acyclic Graph (DAG):
- **Research Planner**: Decomposes complex queries into manageable sub-questions and sets the dynamic tool routing strategy based on the query type.
- **Dynamic Retriever**: Executes parallel tool calls across the Web (Tavily), Academic sources (ArXiv), and Local Knowledge Base (ChromaDB).
- **Critical Analyst**: Filters noise, validates facts, flags contradictions between sources, and structures raw findings.
- **Insight Generator**: Generates chain-of-thought reasoning, identifies hypotheses, and draws strategic actionable insights.
- **Report Builder**: Compiles all insights and filtered facts into a structured, cite-rich final Markdown report.

### UI Capabilities:
- **Real-Time Agent Status**: Real-time feedback showing which specialized agent is currently working and its intermediate outputs.
- **🗺️ Routing Map**: Transparency into why the Planner chose specific tools for every sub-query.
- **Interactive Document Viewer**: View the raw document chunks retrieved, filterable by their source (Web, ArXiv, or Local).
- **Knowledge Base Ingestion**: An upload widget to ingest PDFs directly into a local ChromaDB instance without any cloud embedding costs.
- **🤖 Model Selection**: Choose from various Free/Paid LLMs via OpenRouter dynamically.
- **⏱️ Research Timing**: Displays the exact duration taken to generate the report and metrics on chunks processed.

---

## 💻 Deployment

### Local Deployment
To run the application locally on your machine:

1. **Prerequisites**: Ensure you have Python 3.11+ and [uv](https://docs.astral.sh/uv/) installed.
2. **Install Dependencies**:
   ```bash
   uv sync
   ```
3. **Configure Environment**: Create a `.env` file in the root directory (see [Configuration](#configuration)).
4. **Launch the App**:
   ```bash
   uv run streamlit run app.py
   ```
   The app will be available at `http://localhost:8501`.

### Running Tests
To run the automated validation suite locally:
```bash
uv run pytest tests/ -v
```
See our [Testing Guide](tests/TESTS.md) for complete details on UI and system integration coverage.

### Streamlit Community Cloud (Deployment)
To deploy this agent to the **Streamlit Community Cloud**:

1. **Push to GitHub**: Ensure your `app.py`, `pyproject.toml`, `uv.lock` and `.streamlit` config are committed to your repository.
2. **Connect to Streamlit**:
   - Go to [share.streamlit.io](https://share.streamlit.io/).
   - Click **"New App"** and select your repository and branch.
   - Set the Main file path to `app.py`.
3. **Secrets Management**:
   - In the Streamlit deployment settings, go to **"Secrets"**.
   - Copy the contents of your `.env` file into the secrets box (Streamlit will automatically map these to environment variables).
4. **Deploy**: Click **"Deploy!"**.

---

## ⚙️ Configuration

Create a `.env` file in the root directory:

```env
# Required: OpenRouter API key for LLM access
OPENROUTER_API_KEY=your_openrouter_key_here

# Required: Tavily API key for live web search
TAVILY_API_KEY=your_tavily_key_here

# Optional: Override the default model
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

**Free API Keys:**
- OpenRouter: [https://openrouter.ai/](https://openrouter.ai/)
- Tavily: [https://tavily.com/](https://tavily.com/) (1000 free searches/month)

*(Note: ChromaDB and FastEmbed run completely locally and do not require API keys).*

---

## 🛠️ Project Structure

```
.
├── app.py                     # Streamlit UI entry point & Pipeline integration
├── core/                      # LangGraph DAG compilation and State schema
├── agents/                    # Multi-agent nodes (Planner, Retriever, etc.)
├── tools/                     # Web, ArXiv, and Local ChromaDB tool abstractions
├── llm/                       # OpenRouter configurations and model factory
├── chroma_db/                 # Local directory for Vector Store (auto-generated)
├── pyproject.toml             # uv dependencies definition
├── .env                       # API keys (DO NOT COMMIT)
└── .gitignore                 # Excludes .env, .venv, chroma_db, etc.
```

---

## 📚 Documentation

For a deeper dive into the system's design, patterns, and logic, please refer to the following guides:

**1. Requirements & Scope**
- [Product Requirements Document](PRD.md) — Core requirements mapped to agent implementations and additional platform features.
- [Features Guide](FEATURES.md) — Detailed list of tool features, integrations, and customization options.

**2. Architecture & Design**
- [System Architecture](ARCHITECTURE.md) — High-level system design, security, and deployment workflows.
- [Agents Guide](agents/Agents.md) — Topology, responsibilities, and visual flows for all specialized agents.

**3. Implementation Details**
- [Code Guide](CODE.md) — LangGraph orchestration patterns, state design, and tool integrations.
- [Core Logic Component](core/CORE.md) — Core application execution mechanics.
- [LLM Integrations](llm/LLM.md) — AI model configurations and routing.
- [Tools Configuration](tools/TOOLS.md) — Tool abstractions for the Retrieval system.

**4. Testing & Validation**
- [Testing Guide](tests/TESTS.md) — Overview of the automated testing suite and methodologies.

---

## 👥 Credits

### Developers
Developed by **Outskills Batch C5 Group 2**:
1. Arojeet Sengupta
2. Ravikant Badghaiya
3. Jayanth P
4. Abhinav Upadhyay
5. Mohammed Jameel
6. Shreya Gupta
7. Raajesh Kumar

### Mentors and Instructors
1. Ishan Dutta
2. King Sidharth
3. Paras Madan
4. Srishti Gureja
5. Dileep Karri
6. Antaripa Saha
7. Divij Bajaj
8. Akhil Alampally
9. Karthik Mehra
10. Sham Kulkarni

### Tools and Platforms
Built using:
- LangGraph
- LangChain
- OpenRouter
- tavily.com
- LangSmith
- Streamlit.io
- Antigravity
- Claude Code
>>>>>>> ef86026 (Group_10:Hackathon submission)
