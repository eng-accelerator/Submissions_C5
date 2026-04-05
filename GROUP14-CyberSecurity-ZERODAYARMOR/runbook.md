# 🛡️ ZeroDay Armor - Operational Runbook & Testing Guide

Welcome to ZeroDay Armor! This runbook provides step-by-step instructions for interacting with and specifically testing every major capability, governance feature, and AI agent loaded within the dashboard environment. 

---

## 🛠️ Global Settings & Setup

Before evaluating any feature natively:
1. Ensure your local virtual environment is active (`source venv/bin/activate`).
2. Run the application: `streamlit run app.py`
3. When the **Login Matrix UI** appears, enter a valid API Key. 
   > *Note*: If you provide a strict OpenRouter Token (e.g. `sk-or-x`), the system natively intercepts mapping OpenRouter models directly! Otherwise, it defaults locally to generic `ChatOpenAI` endpoints.

---

## 🎭 Step-by-Step Feature Testing Guide

### 1. Data Privacy Integration (PII Scrubber)
**Objective:** Verify that sensitive Personal Identifiable Information evaluates and successfully scrubs offline *before* making external API calls natively.
- **Set Up:** Navigate to **"Tab 1: 🔍 Log Monitor"**.
- **Action:** Under "Manual Ingestion", paste the following mock text:
  ```
  [21:00:30] Severe Brute_Force failure initiated by root@company.com explicitly routing payloads via 192.168.10.50 testing CC 4111 2222 3333 4444.
  ```
- **Execution:** Click `"Run Log Analysis"`. 
- **Verification:** Look specifically inside the generated Playbooks, or check LangSmith (see Section 7) to inspect the API traces directly. You will see that the IP Address string format natively resolves to `[REDACTED_IPV4]`, the email to `[REDACTED_EMAIL]`, and credit cards to `[REDACTED_CREDIT_CARD]` mapping fully locally securely.

### 2. Governance Role-Based Access Controls (RBAC)
**Objective:** Validate Zero-Trust Streamlit restrictions successfully limiting lower-level operational personas.
- **Set Up:** Look to the far-left Sidebar natively.
- **Action:** Locate the **"Active Role:"** dropdown selector inside the Governance Profile block.
- **Execution:** Change your role from `"Admin (Full Access)"` down to `"L1 Analyst"`.
- **Verification:** Navigate dynamically specifically to **"Tab 3: 🔬 Vuln Scanner"**. The entire code inference framework will be completely hidden natively, resolving instead to a red error prompt reading: `Admin Privileges Required: L1 Analysts are not permitted...` proving authorization routing executes perfectly!

### 3. Vulnerability Code Execution (SAST Scanner)
**Objective:** Let the AI search arbitrary code blocks detecting injection risks.
- **Set Up:** Make sure your Active Role is `Admin`! Navigate securely to **"Tab 3: 🔬 Vuln Scanner"**.
- **Execution:** Click `"Scan Target"`. By default, it runs against the loaded `insecure_app.py` payload natively utilizing local embedding clusters!
- **Verification:** A formal `Risk Score` will execute highlighting Explicit CWE IDs mapping fix recommendations clearly natively generating patching instructions locally.

### 4. Incident Generation & SOAR Automation Maps
**Objective:** Verify automated mitigations securely generate Playbooks and executable Ticket Webhooks formally.
- **Set Up:** Load **"Tab 4: ⚡ Incident Response"**.
- **Action:** Paste a custom arbitrary security breach (e.g. `"The MongoDB instances suffered a destructive Ransomware Outbreak deleting tables."`) and hit Generate.
- **Verification:** You will see a detailed Action Playbook with estimated resolution clocks natively mapping Mitigation Steps. 
- **Verifying SOAR Webhooks:** Explicitly click the `"Generate Jira Ticket Webhook"` buttons natively generating the stream `st.toast` success hooks mocking dynamic webhooks effortlessly.

### 5. Policy Checking & Formal Audit Extraction
**Objective:** Ensure compliance logic works and data structures extract smoothly into deployable compliance evidence packages.
- **Set Up:** Access **"Tab 5: 📋 Policy Checker"**.
- **Execution:** Click `"Check Compliance"` natively evaluating the generic AWS Config payloads visually mapping Risk Gauges!
- **Verification (Export Artifact):** Scroll strictly to the bottom of the artifact page. Click the exact `"📩 Download Formal Compliance Audit Report"` hook locally intercepting standard JSON artifacts mapping directly to your File System bypassing backend restrictions.

### 6. Multi-Modal Vision Email Scanners
**Objective:** Test the Multi-Modal image analysis mappings effortlessly scaling dynamic phishing screens.
- **Set Up:** Note that Streamlit natively evaluates these dynamically via the core CLI/Tests, but backend capabilities are proven entirely automatically via the terminal!
- **Execution:** In terminal, execute `make test`. Ensure that a valid API key exists securely inside your OS variables (`OPENAI_API_KEY`).
- **Verification:** You will notice specific Pytest suites correctly evaluating `.png/.jpeg` files from `data/phishing_imgs` against zero-day logic returning robust detection properties natively locally avoiding external token bloat!

### 7. LangSmith Tracing & Telemetry (Observability)
**Objective:** Evaluate native API LLM token parsing streams monitoring costs, hallucinations, or data masking limits directly globally.
- **Set Up:** Jump strictly back to your Streamlit Sidebar natively. 
- **Action:** Explicitly toggle **`LangSmith Observability`** cleanly to `[ON]`.
- **Execution:** Move directly over to **"Tab 6: 📊 LangSmith Tracing"**.
- **Verification:** A direct IFrame will load `smith.langchain.com` seamlessly allowing deep internal trace evaluation cleanly over any generated context loops inside the previous Tabs globally. 

---

## 📖 Essential Glossary
- **SOC (Security Operations Center)**: Centralized internal tracking mapping organizational security vectors natively.
- **PII (Personally Identifiable Information)**: Any data mapping structural identity (Emails, IPs, SSNs). ZeroDay explicitly scrubs this strictly offline avoiding cloud ingestion completely.
- **SOAR (Security Orchestration, Automation, and Response)**: Technologies simulating mapped pipeline logic gracefully (e.g. our interactive Jira/CrowdStrike hook buttons natively).
- **RAG (Retrieval-Augmented Generation)**: The act of fetching static vector knowledge (NVD CVE records/NIST Compliance rules) merging cleanly into AI logic paths evaluating boundaries actively.
- **MITRE ATT&CK**: A globally-accessible adversary framework mapping complex cyber mapping techniques dynamically.
