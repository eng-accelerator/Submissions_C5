# 🛡️ ZeroDay Armor - Cyber Security AI multi self healing Agent

**1.** **[🎬 ZeroDay Armor in Action Video](https://drive.google.com/file/d/14r1qBhBQRsKTthfB9SvmrQUeg2M4HEQ3/view)**


**2.** **[Reference Architecture](https://github.com/eng-accelerator/Submissions_C5/blob/Group__14/ZeroDayArmor/CYBERSEC_AI_AGENT/architecture/ZeroDayArmor%20%E2%80%94%20Investor%20One-Pager.pdf)**

**3.** **[Techinal Architecture](https://github.com/eng-accelerator/Submissions_C5/blob/Group__14/ZeroDayArmor/CYBERSEC_AI_AGENT/architecture/ZeroDayArmor_pitch_slide.html)**

**4.** **[Tutorial](https://github.com/eng-accelerator/Submissions_C5/blob/Group__14/ZeroDayArmor/CYBERSEC_AI_AGENT/architecture/ZeroArmor.pdf)**

**5.** **[Tutorial](https://github.com/eng-accelerator/Submissions_C5/blob/Group__14/ZeroDayArmor/CYBERSEC_AI_AGENT/architecture/)**

**ZeroDay Armor** is a smart, proactive Generative AI-powered Security Operations Dashboard built specifically to help Threat Intelligence analysts mitigate vulnerabilities, scan for network threats, process incident responses, ensure compliance policies, and automatically analyze advanced phishing payloads through multi-modal Vision capabilities.

## ✨ Features

*   **🔍 Log Monitor:** Evaluate system/auth logs to proactively identify Brute Force anomalies and malicious activities (supports Manual Ingestion and Real-Time Kafka/Redis stream mimicking).
*   **🌐 Threat Intelligence:** Native NLP querying of Live CVEs resolving through NVD APIs, returning actionable contextual vulnerability reports mapped to the MITRE ATT&CK framework.
*   **🔬 Vulnerability Scanner:** Secure code analyzer allowing instantaneous Dockerfile or arbitrary application scanner reports targeting security malpractices.
*   **⚡ Incident Response:** Automatically aggregates indicators of compromise into AI-generated Mitigation Playbooks assigning remediation SLA paths and containment commands dynamically.
*   **📋 Policy Checker:** Scan infrastructure configurations (JSON/YAML) to measure compliance mapping and explicitly outline deviation gap resolutions via graphical gauges.
*   **📧 Email Threat & Phishing Scanner (Vision AI):** Process suspicious email screenshots directly avoiding text extraction complexity. The onboard advanced visual analyst will search for patterns including Quishing, Spear Phishing, Thread Hijacking, BEC, and HTML smuggling—resizing payloads locally on the fly to maximize API latency performance and minimize token spending.

## 🏛 Architecture & Design Principles

The application relies heavily on a multi-agent orchestrated backend (resembling LangGraph's dynamic execution states).
Here are the mandatory infrastructure points:

1. **Multi-Agent Architecture**: A LangGraph `StateGraph` orchestrates 5 highly specialized agents covering distinct responsibilities cleanly abstracted through the Router Agent logic.
2. **RAG + Agent Hybrid Execution**: Integrates FAISS vector clusters caching NIST, ISO 27001, and historical CVEs, bridging deterministic retrievals directly into inference layers.
3. **Real-Time Pipelines**: Enforces sub-5-second alerts tracking raw log anomalies parsing against streaming Python generators cleanly decoupled via priority queues.
4. **100% Free-Tier Tooling**: Built completely free via Bandit, Safety, Trivy, NVD API, and LangChain utilizing HuggingFace embeddings natively!

## 🔐 Enterprise Security & Governance (How to Test)
ZeroDay Armor incorporates standard enterprise-grade SOC guardrails simulating real-life analyst workflows. To evaluate these capabilities, engage with the UI dynamically:
*   **Role-Based Access Control (RBAC)**: Switch your persona dynamically through the Sidebar's `Active Role` dropdown. Change your role to **"L1 Analyst"** to physically verify the "Vulnerability Scanner" locks down administrative environments dynamically natively enforcing Zero-Trust mappings! 
*   **Data Privacy (PII Scrubber)**: Natively protects outgoing payloads by scrubbing IP addresses and e-mails proactively using regex vectors before streaming LLMs locally safely shielding compliance constraints. 
*   **SOAR Automations**: Navigate directly to the `Incident Response` capabilities and invoke dynamic playbooks. The generated responses actively embed Mock API hooks generating **Jira Ticketing Webhooks** alongside **CrowdStrike Host Isolation** capabilities!
*   **Compliance Artifact Exporting**: Once the platform audits your compliance YAML targets across the `Policy Checker` module, interactively utilize the secure `"Download Formal Compliance Audit Report"` stream compiling the evaluation artifacts locally explicitly securely!
*   **LangSmith Observability Tracking**: Toggle the `LangSmith Observability` config parameter within the active Sidebar UI triggering dedicated underlying LangChain instrumentation rendering cleanly natively integrated via `Tab 6`, monitoring API tracing natively!

## 🚀 Getting Started

### Prerequisites

*   `python >= 3.11` (Langchain is highly optimized currently for <= 3.13)
*   Streamlit
*   Pytest (for pipeline verification)
*   An OpenAI or OpenRouter API Key

### Installation

1. Clone this repository locally.
2. Initialize and open your python environment:
   ```bash
   python -m venv venv
   On mac:
     source venv/bin/activate
   On PC:
     .\venv\Scripts\activate
     # If you get error running scripts, run VSC as admin and execute the command 'Set-ExecutionPolicy -ExecutionPolicy RemoteSigned' and reply y.
   ```
3. Install the dependencies exactly.
   ```bash
   pip install -r requirements.txt
   ```

### Running the System

You can run the full visual Security Operations Center (SOC) dashboard using Streamlit directly!

```bash
streamlit run app.py
```

Provide your OpenRouter/OpenAI API key within the visually matrixed UI login prompt. Note that using "sk-or-" keys will automatically instruct the architecture to dynamically target the OpenRouter inference pipelines natively.

## 🧪 Testing framework

We provide robust, mocked, and True-Context E2E unit tests. You can evaluate the architecture confidently using `pytest`:

```bash
pytest tests/
```

> **Note:** The `tests/test_phishing_analysis.py` specifically features live "end to end" visual evaluation scenarios against `.png/.jpeg` files in `data/phishing_imgs` if it explicitly detects an active environment API Key!
