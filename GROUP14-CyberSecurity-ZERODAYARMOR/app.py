import streamlit as st
import os
import os
from dotenv import load_dotenv

# Load root env natively before any Langchain hooks cache state bounds
load_dotenv(override=True)

import json
import pandas as pd
import plotly.graph_objects as go
import uuid

# --- Page Config ---
st.set_page_config(
    page_title="ZeroDay Armor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Light / Dark Mode Apple-style Toggle ---
top_c1, top_c2 = st.columns([9, 1])
with top_c2:
    theme_light = st.toggle("Appearance", key="theme_tgl")

hide_sidebar = (
    """[data-testid="stSidebar"] { display: none !important; }"""
    if not st.session_state.get("authenticated", False)
    else ""
)

if theme_light:
    # --- TRUE APPLE UX LIGHT MODE ---
    st.markdown(
        f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        {hide_sidebar}
        
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }}
        
        .stApp {{
            background-color: #f5f5f7 !important;
            background-image: none !important;
            color: #1d1d1f !important;
        }}
        
        h1, h2, h3, h4, .stMarkdown p {{
            color: #1d1d1f !important;
            text-shadow: none !important;
        }}
        
        /* Metric Cards */
        div[data-testid="metric-container"] {{
            background: #ffffff;
            border: 1px solid #d2d2d7;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }}
        
        /* Login Wrapper */
        .login-wrap {{ max-width: 420px; margin: 15vh auto; padding: 40px; background: rgba(255,255,255,0.8); backdrop-filter: blur(20px); border: 1px solid #d2d2d7; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        
        /* Input Boxes */
        .stTextInput div[data-baseweb="input"] {{
            background-color: #ffffff !important;
            border: 1px solid #d2d2d7 !important;
            border-radius: 8px !important;
            padding: 2px 10px !important;
            transition: all 0.2s ease;
        }}
        .stTextInput div[data-baseweb="base-input"] {{
            background-color: transparent !important;
        }}
        
        .matrix-label {{
            font-family: 'Inter', -apple-system, sans-serif !important;
            font-size: 14px !important;
            color: #86868b !important;
            text-shadow: none !important;
            text-align: left;
            margin-bottom: 5px;
            letter-spacing: normal !important;
            font-weight: 500;
            margin-top: 10px;
        }}
        
        .stTextInput input {{
            background-color: transparent !important;
            border: none !important;
            color: #1d1d1f !important;
            font-family: 'Inter', -apple-system, sans-serif !important;
            font-size: 16px !important;
            padding: 8px 5px !important;
            letter-spacing: normal !important;
            box-shadow: none !important;
        }}
        
        .stTextInput div[data-baseweb="input"]:focus-within {{
            box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.3) !important;
            border-color: #0071e3 !important;
        }}
        
        .matrix-btn button {{
            background-color: #0071e3 !important;
            color: #ffffff !important;
            border-radius: 10px !important;
            border: none !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            margin-top: 20px !important;
            letter-spacing: normal !important;
            padding: 12px !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 10px rgba(0, 113, 227, 0.3) !important;
        }}
        .matrix-btn button:hover {{
            background-color: #0077ED !important;
            transform: scale(1.02);
            color: #ffffff !important;
        }}
    </style>
    """,
        unsafe_allow_html=True,
    )
else:
    # --- MATRIX SOC DARK MODE ---
    st.markdown(
        f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
        
        {hide_sidebar}
        
        html, body, [class*="css"] {{
            font-family: 'Share Tech Mono', monospace !important;
        }}
        
        .stApp {{
            background-color: #0b1f3d !important;
            background-image: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(255, 255, 255, 0.03) 3px, rgba(255, 255, 255, 0.03) 6px) !important;
            color: #ffffff !important;
        }}
        
        h1, h2, h3, h4, .stMarkdown p {{
            color: #ffffff !important;
        }}
        h1, h2 {{
            color: #00ffff !important;
            text-shadow: 0 0 10px rgba(0,255,255, 0.7);
        }}
        
        /* Metric Cards */
        div[data-testid="metric-container"] {{
            background: transparent;
            border: 2px solid #00ffff;
            border-radius: 4px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,255,255, 0.2);
        }}
        
        /* Login Wrapper */
        .login-wrap {{ max-width: 500px; margin: 15vh auto; padding: 20px; }}
        
        /* Input Boxes */
        .stTextInput div[data-baseweb="input"] {{
            background-color: transparent !important;
            border: 3px solid #ffffff !important;
            border-radius: 0px !important;
            padding: 2px 8px !important;
            transition: all 0.2s ease;
        }}
        .stTextInput div[data-baseweb="base-input"] {{
            background-color: transparent !important;
        }}
        
        .matrix-label {{
            font-family: 'Share Tech Mono', monospace !important;
            font-size: 20px !important;
            color: #00ffff !important;
            text-shadow: 0 0 10px rgba(0,255,255,0.8);
            text-align: left;
            margin-bottom: 5px;
            letter-spacing: 2px;
            font-weight: bold;
            margin-top: 15px;
        }}
        
        .stTextInput input {{
            background-color: transparent !important;
            border: none !important;
            color: #ffffff !important;
            font-family: 'Share Tech Mono', monospace !important;
            font-size: 22px !important;
            padding: 10px 10px !important;
            letter-spacing: 4px !important;
            box-shadow: none !important;
            height: auto !important;
        }}
        
        .stTextInput div[data-baseweb="input"]:focus-within {{
            box-shadow: 0 0 15px #ffffff !important;
            background-color: rgba(0,0,0,0.4) !important;
        }}
        
        .matrix-btn button {{
            background-color: #ffffff !important;
            color: #0b1f3d !important;
            border-radius: 0px !important;
            border: 3px solid #ffffff !important;
            font-size: 24px !important;
            font-weight: bold !important;
            margin-top: 35px !important;
            letter-spacing: 3px !important;
            padding: 8px !important;
            transition: all 0.2s ease !important;
        }}
        .matrix-btn button:hover {{
            background-color: transparent !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px #ffffff;
        }}
    </style>
    </style>
    """,
        unsafe_allow_html=True,
    )

def validate_key(key):
    try:
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(api_key=key, model="gpt-4o-mini", max_tokens=1)
        if key.startswith("sk-or"):
            llm = ChatOpenAI(
                api_key=key,
                base_url="https://openrouter.ai/api/v1",
                model="openai/gpt-4o-mini",
                max_tokens=1,
            )
        llm.invoke("test")
        return True
    except Exception as e:
        return False


@st.dialog("ZERODAY ARMOR ACCESS", width="small")
def login_modal():
    st.markdown("<h1 style='font-size: 32px; letter-spacing: 4px; text-align: center; margin-bottom: 0px;'>AUTHENTICATION</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 14px; letter-spacing: 2px; text-align: center; margin-top: 0px;'>SMART PROACTIVE GEN AI ALERT BOT</p><br>", unsafe_allow_html=True)

    st.markdown("<div class='matrix-label'> USERNAME :</div>", unsafe_allow_html=True)
    username = st.text_input("Username", label_visibility="collapsed", placeholder="USER_01")

    st.markdown("<br><div class='matrix-label'> PASSWORD :</div>", unsafe_allow_html=True)
    api_key = st.text_input("API Key", type="password", label_visibility="collapsed", placeholder="••••••••••••")

    def matrix_error(msg):
        st.markdown(
            f"<div style='border: 2px solid #ff3333; background-color: rgba(255, 0, 0, 0.2); padding: 10px; color: #ffcccc; font-size: 14px; text-align: center; margin-top: 15px; box-shadow: 0 0 10px rgba(255,0,0,0.5);'>[!] {msg}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='matrix-btn'>", unsafe_allow_html=True)
    if st.button("CONNECT", use_container_width=True):
        if not username or not api_key:
            matrix_error("ACCESS DENIED: MISSING CREDENTIALS")
        else:
            with st.spinner("VERIFYING HANDSHAKE..."):
                if validate_key(api_key):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    if api_key.startswith("sk-or"):
                        os.environ["OPENROUTER_API_KEY"] = api_key
                    else:
                        os.environ["OPENAI_API_KEY"] = api_key
                    st.rerun()
                else:
                    matrix_error("ACCESS DENIED: INVALID KEY / EXPIRED TOKEN")
    st.markdown("</div>", unsafe_allow_html=True)


# --- Landing Page & Authentication Loop ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.authenticated:
    c1, c2, c3 = st.columns([1, 8, 1])
    with c2:
        st.image("/Users/skdasi/.gemini/antigravity/brain/5b179bf8-6fcd-446e-8145-9dd754567133/media__1775386953737.png", use_container_width=True)
        btn_c1, btn_c2, btn_c3 = st.columns([3, 2, 3])
        with btn_c2:
            st.markdown("<div class='matrix-btn'>", unsafe_allow_html=True)
            if st.button("REQUEST DEMO", use_container_width=True):
                login_modal()
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# Import graph here so it doesn't fail on missing API keys before login
from orchestrator import build_graph

# --- Sidebar ---
with st.sidebar:
    st.title("🛡️ 'ZeroDay Armor -  AI secure agent bot")
    st.caption(
        "Next-Gen AI Security ROBO BOT Proactive, Predictive, and Preventive bot "
    )

    st.markdown(f"**👤 User:** {st.session_state.username}")
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.graph = None
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if "OPENROUTER_API_KEY" in os.environ:
            del os.environ["OPENROUTER_API_KEY"]
        st.rerun()

    st.markdown("---")
    st.subheader("Governance Profile")
    st.session_state.current_role = st.selectbox(
        "Active Role:",
        options=["Admin (Full Access)", "L1 Analyst", "Compliance Auditor"],
    )

    tracing_default = "LANGCHAIN_API_KEY" in os.environ
    enable_tracing = st.toggle("LangSmith Observability", value=tracing_default)
    if enable_tracing:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = "https://eu.api.smith.langchain.com"
        os.environ["LANGCHAIN_PROJECT"] = "ZeroDayArmor_Local"
    else:
        os.environ.pop("LANGCHAIN_TRACING_V2", None)

    st.markdown("---")
    st.subheader("System Health")
    c1, c2 = st.columns(2)
    c1.metric("Agents", "5/5", "Online")
    c2.metric("Vectors", "50", "Loaded")

    st.markdown("---")
    # Initialize Graph
    if "graph" not in st.session_state or st.session_state.graph is None:
        with st.spinner("Initializing Agents..."):
            st.session_state.graph = build_graph()
            st.success("Connected")
    else:
        st.success("Connected")

# --- Main UI ---
st.title("🛡️ Security Operations Dashboard")

tab0, tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📉 Dashboard",
        "🔍 Log Monitor",
        "🌐 Threat Intel",
        "🔬 Vuln Scanner",
        "⚡ Incident Response",
        "📋 Policy Checker",
        "📊 LangSmith Tracing",
    ]
)


def run_agent(input_type, input_data):
    from agents.pii_scrubber import PIIScrubber

    # Proactively scrub string-based PII text contexts before allocating to LLMs natively
    if isinstance(input_data, str):
        input_data = PIIScrubber.redact(input_data)

    state = {
        "input_type": input_type,
        "input_data": input_data,
        "log_alerts": [],
        "threat_reports": [],
        "scan_results": [],
        "playbooks": [],
        "compliance_reports": [],
        "severity_level": "LOW",
    }
    try:
        return st.session_state.graph.invoke(state)
    except Exception as e:
        err_details = str(e)
        if "402" in err_details:
            msg = "QUOTA EXCEEDED (HTTP 402): API Key has insufficient funds or limits."
        else:
            msg = f"SYSTEM COMPONENT FAILURE: {err_details}"

        st.markdown(
            f"""
        <div style='background-color: #1a0000; border: 2px solid #ff3333; border-radius: 6px; padding: 15px; margin-top: 10px;'>
            <h3 style='color: #ff4444; margin-top: 0; font-family: "Courier New", monospace;'>🚨 CRITICAL AGENT FAULT</h3>
            <p style='color: #ffaaaa; font-family: "Courier New", monospace;'>{msg}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        return state  # Return base state to prevent UI crashing


# --- Tab 0: Dashboard ---
with tab0:
    st.header("📡 Live Threat Dashboard")
    st.markdown("Simulated real-time security operations dashboard. New threats arrive every 4 seconds. Approve or reject critical auto-heal actions. Monitor the self-heal loop in action.")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Threats detected", "28")
    c2.metric("Auto-healed", "14")
    c3.metric("Pending approval", "1")
    c4.metric("Critical active", "14")
    c5.metric("Monitor loops", "42")

    st.markdown("<br>", unsafe_allow_html=True)
    
    feed_col, log_col = st.columns(2)
    with feed_col:
        with st.container(border=True):
            st.markdown("### Live Threat Feed &nbsp;&nbsp;&nbsp;&nbsp; 🟢 `MONITORING`")
            st.markdown("""
🔴 **CRITICAL | RCE ATTEMPT — 45.33.32.156**  
`23:12:02 · log4j/app · T1190 · JNDI injection -> /bin/bash spawned`
<hr style='margin: 0.5em 0'>

🔵 **MEDIUM | PORT SCAN — 10.0.0.201**  
`23:11:59 · network · T1046 · 28 ports scanned in 4 seconds`
<hr style='margin: 0.5em 0'>

🔴 **CRITICAL | SQLI — 203.0.113.77**  
`23:11:52 · nginx/api · T1190 · UNION SELECT — 512KB response exfiltrated`
<hr style='margin: 0.5em 0'>

🟠 **HIGH | BRUTE FORCE — 185.220.101.45**  
`23:11:49 · sshd · T1110.001 · 12 failed SSH attempts in 30s`
<hr style='margin: 0.5em 0'>

🔴 **CRITICAL | PRIV ESCALATION — 185.220.101.88**  
`23:11:42 · sudo · T1078.002 · Admin login from TOR + sudo useradd backdoor`
<hr style='margin: 0.5em 0'>

⚪ **LOW | ANOMALY — 192.168.1.50**  
`23:11:27 · unusual hours login`
            """, unsafe_allow_html=True)

    with log_col:
        with st.container(border=True):
            st.markdown("### Self-Heal Action Log")
            st.code('''Verify: confirmed — loop restart #41
$ iptables -A INPUT -s 10.0.0.201 -j DROP
23:12:00 ✓ AUTO-HEALED: port_scan (10.0.0.201)
Verify: confirmed — loop restart #38
$ fail2ban-client set sshd banip 185.220.101.45
$ iptables -A INPUT -s 185.220.101.45 -j DROP
23:11:50 ✓ AUTO-HEALED: brute_force (185.220.101.45)
Verify: confirmed — loop restart #35
$ Log entry created — monitoring
23:11:39 ✓ AUTO-HEALED: anomaly (192.168.1.50)
Verify: confirmed — loop restart #32
$ kubectl apply -f mining-block-netpol.yaml
$ kubectl delete pod web-backend-7d9f4 --force
23:11:27 ✓ AUTO-HEALED: cryptomining (10.0.5.12)
Verify: confirmed — loop restart #29
$ iptables -A INPUT -s 10.0.0.201 -j DROP''', language="bash")

# --- Tab 1: Log Monitor ---
with tab1:
    st.header("🔍 Security Log Analysis")

    ingest_mode = st.radio(
        "Log Ingestion Method:",
        ["Manual Upload", "Live Stream (Kafka/Redis)"],
        horizontal=True,
    )
    st.markdown("---")

    if ingest_mode == "Manual Upload":
        log_sample = ""
        base_path = os.path.dirname(__file__)
        sample_path = os.path.join(base_path, "data/sample_logs/auth_brute_force.log")
        if os.path.exists(sample_path):
            with open(sample_path) as f:
                log_sample = f.read()

        if "log_input_val" not in st.session_state:
            st.session_state.log_input_val = log_sample

        def load_pii_log():
            st.session_state.log_input_val = "We detected a severe ransomware payload downloaded by \njohn.doe@example.com routing through suspicious IPv4 node 192.168.45.101. The attacker exploited a domain matching CC number 4111 2222 3333 4444."

        st.button("🧪 Load PII Test Scenario", on_click=load_pii_log, key="btn_pii_log")
        log_input = st.text_area("Paste Logs here:", key="log_input_val", height=200)

        if st.button("Run Log Analysis"):
            with st.spinner("Analyzing logs..."):
                result = run_agent("log", log_input)
                st.subheader("Analysis Results")
                alerts = result.get("log_alerts", [])

                if alerts:
                    # Summary Metrics
                    col1, col2 = st.columns(2)
                    col1.metric("Total Alerts Detected", len(alerts))
                    max_sev = max(
                        [a.get("severity", "LOW") for a in alerts],
                        key=lambda x: ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(x),
                    )
                    col2.metric("Highest Severity", max_sev)

                    # Alerts DataFrame
                    df_alerts = pd.DataFrame(alerts)
                    display_cols = [
                        "alert_type",
                        "severity",
                        "affected_user",
                        "source_ip",
                        "affected_service",
                        "mitre_technique",
                    ]
                    # Keep only valid columns
                    display_cols = [c for c in display_cols if c in df_alerts.columns]

                    st.dataframe(
                        df_alerts[display_cols],
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.subheader("Evidence Dumps")
                    for i, row in df_alerts.iterrows():
                        with st.expander(
                            f"Alert #{i+1} : {row.get('alert_type', 'Unknown')} Modal Evidence"
                        ):
                            st.json(row.to_dict())

    elif ingest_mode == "Live Stream (Kafka/Redis)":
        from streaming.stream_client import MockStreamClient
        import time

        # State init
        if "stream_client" not in st.session_state:
            st.session_state.stream_client = MockStreamClient()
        if "stream_active" not in st.session_state:
            st.session_state.stream_active = False
        if "stream_buffer" not in st.session_state:
            st.session_state.stream_buffer = []
        if "live_alerts" not in st.session_state:
            st.session_state.live_alerts = []

        c1, c2, c3 = st.columns(3)
        c1.selectbox("Broker Type", ["Kafka Cluster", "Redis Pub/Sub"])
        c2.text_input(
            "Broker Address",
            value="localhost:9092",
            disabled=st.session_state.stream_active,
        )
        c3.text_input(
            "Topic/Channel",
            value="auth-events-production",
            disabled=st.session_state.stream_active,
        )

        btn_col, stat_col = st.columns([1, 3])

        if not st.session_state.stream_active:
            if btn_col.button(
                "🔴 Start Live Stream", type="primary", use_container_width=True
            ):
                st.session_state.stream_active = True
                st.session_state.stream_client.start()
                st.rerun()
        else:
            if btn_col.button("⏹ Stop Stream", use_container_width=True):
                st.session_state.stream_active = False
                st.session_state.stream_client.stop()
                st.rerun()

        stat_col.metric(
            "Pending Queue Buffer",
            f"{len(st.session_state.stream_buffer)} / 5 (AI Batch Limit)",
        )

        st.subheader("LiveData Tail")
        tail_view = st.empty()

        st.subheader("Real-Time Triage Results")
        res_view = st.empty()

        # Render historical live alerts
        if st.session_state.live_alerts:
            df_live = pd.DataFrame(st.session_state.live_alerts)
            cols = [
                c
                for c in ["alert_type", "severity", "confidence_score", "source_ip"]
                if c in df_live.columns
            ]
            res_view.dataframe(df_live[cols], use_container_width=True, hide_index=True)

        # Background Polling TICK
        if st.session_state.stream_active:
            new_logs = st.session_state.stream_client.get_logs()
            if new_logs:
                st.session_state.stream_buffer.extend(new_logs)

            display_logs = (
                "\n".join(st.session_state.stream_buffer[-12:])
                if st.session_state.stream_buffer
                else "Listening for events..."
            )
            tail_view.code(display_logs, language="bash")

            # Batch Trigger
            if len(st.session_state.stream_buffer) >= 5:
                batch = "\n".join(st.session_state.stream_buffer[:5])
                st.session_state.stream_buffer = st.session_state.stream_buffer[
                    5:
                ]  # cycle

                with st.spinner("AI evaluating batch limit hit..."):
                    res = run_agent("log", batch)
                    log_alerts = res.get("log_alerts", [])
                    if log_alerts:
                        st.session_state.live_alerts = (
                            log_alerts + st.session_state.live_alerts
                        )  # Prepend so newest is top
                        # We don't render here, we wait for next tick to render cleanly

            time.sleep(1)
            st.rerun()

# --- Tab 2: Threat Intel ---
with tab2:
    st.header("🌐 Threat Intelligence Lookup")
    query = st.text_input("Search CVE or Technology (e.g., 'Log4j RCE'):")
    if st.button("Search Intel"):
        with st.spinner("Searching CVE Database..."):
            result = run_agent("cve_query", query)
            reports = result.get("threat_reports", [])

            if reports:
                for report in reports:
                    st.markdown("---")
                    c1, c2, c3 = st.columns([2, 1, 1])
                    with c1:
                        st.subheader(f"CVEs: {', '.join(report.get('cve_ids', []))}")
                        st.markdown(report.get("summary", ""))
                    with c2:
                        cvss = report.get("cvss_score", 0.0)
                        if cvss >= 9.0:
                            st.metric(
                                "CVSS Score",
                                f"{cvss}/10",
                                "Critical",
                                delta_color="inverse",
                            )
                        elif cvss >= 7.0:
                            st.metric(
                                "CVSS Score",
                                f"{cvss}/10",
                                "High",
                                delta_color="inverse",
                            )
                        else:
                            st.metric(
                                "CVSS Score", f"{cvss}/10", "Medium", delta_color="off"
                            )
                    with c3:
                        exploit_status = (
                            "🔴 Available"
                            if report.get("exploit_available")
                            else "🟢 Not Available"
                        )
                        patch_status = (
                            "🟢 Available"
                            if report.get("patch_available")
                            else "🔴 Missing"
                        )
                        st.markdown(f"**Exploit:** {exploit_status}")
                        st.markdown(f"**Patch:** {patch_status}")

                    st.markdown("**Affected Versions:**")
                    st.code("\n".join(report.get("affected_versions", [])))
            else:
                st.info("No threat intelligence found for the query.")

    st.markdown("---")
    st.header("📧 Email Threat & Phishing Scanner")
    st.markdown(
        "Upload a screenshot of a suspicious email to scan for phishing patterns, malicious URLs, and signs of spoofing."
    )

    uploaded_file = st.file_uploader(
        "Upload Suspicious Email Image", type=["png", "jpg", "jpeg"]
    )
    if uploaded_file is not None:
        st.image(
            uploaded_file, caption="Uploaded Email Image", use_container_width=True
        )
        if st.button("Scan Email Image", key="scan_email_btn"):
            with st.spinner("Scanning image with AI Vision API..."):
                try:
                    from agents.phishing_analysis import analyze_suspicious_email_image

                    result = analyze_suspicious_email_image(uploaded_file.getvalue())
                    st.success("Analysis Complete")

                    if "report_data" in result:
                        report = result["report_data"]

                        if "error" in report:
                            st.error(report["error"])
                        else:
                            st.markdown(
                                f"### 🛡️ Risk Analysis Report: {report.get('risk_level', 'UNKNOWN')}"
                            )
                            if report.get("is_phishing"):
                                st.error("🚨 Phishing Detected!")
                            else:
                                st.success("✅ No phishing indicators found.")

                            st.markdown(
                                f"**Analysis Summary:** {report.get('summary_analysis', '')}"
                            )

                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Detected Threats:**")
                                for t in report.get("detected_threats", []):
                                    st.markdown(f"- {t}")
                            with col2:
                                st.markdown("**Social Engineering Tactics:**")
                                for s in report.get("social_engineering_tactics", []):
                                    st.markdown(f"- {s}")

                            if report.get("suspicious_links_or_attachments"):
                                st.warning("**Suspicious Links/Attachments:**")
                                for link in report.get(
                                    "suspicious_links_or_attachments", []
                                ):
                                    st.markdown(f"- {link}")

                            with st.expander("Raw Pydantic JSON Payload"):
                                st.json(report)
                    else:
                        st.markdown("No report generated.")
                except Exception as e:
                    st.error(f"Failed to scan image: {e}")

# --- Tab 3: Vuln Scanner ---
with tab3:
    st.header("🔬 Vulnerability Scanner")
    if st.session_state.get("current_role", "Admin (Full Access)") == "L1 Analyst":
        st.error(
            "Admin Privileges Required: L1 Analysts are not permitted to run dynamic vulnerability execution tests."
        )
    else:
        code_sample = ""
        base_path = os.path.dirname(__file__)
        sample_path = os.path.join(base_path, "data/vuln_samples/insecure_app.py")
        if os.path.exists(sample_path):
            with open(sample_path) as f:
                code_sample = f.read()

        code_input = st.text_area(
            "Paste Code or Dockerfile:", value=code_sample, height=300
        )
        if st.button("Scan Target"):
            with st.spinner("Scanning..."):
                result = run_agent("code", code_input)
                scan_results = result.get("scan_results", [])

                for scan in scan_results:
                    st.markdown("---")
                    col1, col2 = st.columns([1, 4])

                    risk_score = scan.get("risk_score", 0)
                    with col1:
                        st.metric(
                            "Risk Score",
                            f"{risk_score}/100",
                            "High Risk" if risk_score > 70 else "Elevated Risk",
                            delta_color="inverse",
                        )
                        st.caption(f"Target: {scan.get('scan_target')}")

                    with col2:
                        if scan.get("remediation_priority"):
                            st.error(
                                "🚨 **Remediation Priorities:**\n"
                                + "\n".join(
                                    [
                                        f"- {item}"
                                        for item in scan.get("remediation_priority")
                                    ]
                                )
                            )

                    findings = scan.get("findings", [])
                    if findings:
                        st.subheader("Discovered Vulnerabilities")
                        df_findings = pd.DataFrame(findings)
                        display_cols = [
                            "cwe_id",
                            "title",
                            "severity",
                            "file_path",
                            "fix_recommendation",
                        ]
                        display_cols = [
                            c for c in display_cols if c in df_findings.columns
                        ]
                        st.dataframe(
                            df_findings[display_cols], use_container_width=True
                        )
                    else:
                        st.success("No vulnerabilities discovered.")

# --- Tab 4: Incident Response ---
with tab4:
    st.header("⚡ Incident Response Playbook")

    if "inc_input_val" not in st.session_state:
        st.session_state.inc_input_val = ""

    def load_pii_inc():
        st.session_state.inc_input_val = "We detected a severe ransomware payload downloaded by \njohn.doe@example.com routing through suspicious IPv4 node 192.168.45.101. The attacker exploited a domain matching CC number 4111 2222 3333 4444."

    st.button("🧪 Load PII Test Scenario", on_click=load_pii_inc, key="btn_pii_inc")
    incident_desc = st.text_area(
        "Describe the incident:", key="inc_input_val", height=200
    )

    if st.button("Generate Playbook"):
        with st.spinner("Creating Playbook..."):
            result = run_agent("incident", incident_desc)
            playbooks = result.get("playbooks", [])

            for pb in playbooks:
                st.markdown("---")
                col1, col2 = st.columns(2)
                col1.subheader(f"Inc: {pb.get('incident_type', 'UNKNOWN').upper()}")

                eta = f"{pb.get('estimated_resolution_hours', 0)} hrs"
                if pb.get("affected_user"):
                    eta = f"User: {pb.get('affected_user')} | {eta}"

                col2.metric(
                    "Resolution Path",
                    eta,
                )

                st.markdown("### Mitigation Playbook")
                df_playbook = pd.DataFrame(pb.get("playbook", []))
                if not df_playbook.empty:
                    st.table(
                        df_playbook[
                            ["step", "phase", "owner", "priority", "description"]
                        ]
                    )

                st.markdown("### Containment Commands")
                for cmd in pb.get("containment_commands", []):
                    st.code(cmd, language="bash")

                colA, colB = st.columns(2)
                key_prefix = str(pb.get("incident_type", uuid.uuid4()))
                if colA.button(
                    "Generate Jira Ticket Webhook", key=key_prefix + "_jira"
                ):
                    st.toast("WebHook API Fired! Jira board updated.", icon="✅")
                if colB.button("Host Isolate on Crowdstrike", key=key_prefix + "_cs"):
                    st.toast(
                        "Isolation initiated through CrowdStrike Falcon sensor APIs.",
                        icon="🚨",
                    )

                st.markdown("### Escalation/Notification List")
                st.markdown(
                    "\n".join(
                        [f"- {person}" for person in pb.get("notification_list", [])]
                    )
                )

# --- Tab 5: Policy Checker ---
with tab5:
    st.header("📋 Compliance Policy Checker")
    config_sample = ""
    base_path = os.path.dirname(__file__)
    sample_path = os.path.join(base_path, "data/configs/non_compliant_config.json")
    if os.path.exists(sample_path):
        with open(sample_path) as f:
            config_sample = f.read()

    config_input = st.text_area(
        "Paste Configuration (JSON/YAML):", value=config_sample, height=300
    )
    if st.button("Check Compliance"):
        with st.spinner("Checking..."):
            result = run_agent("config", config_input)
            reports = result.get("compliance_reports", [])

            for report in reports:
                st.markdown("---")
                comp_score = report.get("compliance_score", 0)

                # Gauge representation via Plotly
                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=comp_score,
                        domain={"x": [0, 1], "y": [0, 1]},
                        title={"text": "Compliance Score"},
                        gauge={
                            "axis": {"range": [None, 100]},
                            "bar": {"color": "darkblue"},
                            "steps": [
                                {"range": [0, 50], "color": "#f85149"},
                                {"range": [50, 80], "color": "#d29922"},
                                {"range": [80, 100], "color": "#3fb950"},
                            ],
                        },
                    )
                )
                # Adjust size
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig, use_container_width=True)

                gaps = report.get("gaps", [])
                if gaps:
                    st.subheader(
                        f"Compliance Gaps ({report.get('framework', 'Unknown Framework')})"
                    )
                    df_gaps = pd.DataFrame(gaps)
                    display_cols = [
                        "control_id",
                        "status",
                        "control_title",
                        "remediation",
                    ]
                    display_cols = [c for c in display_cols if c in df_gaps.columns]
                    st.dataframe(df_gaps[display_cols], use_container_width=True)

                    if report.get("priority_fixes"):
                        st.info(
                            "💡 **Priority Actions:**\n"
                            + "\n".join(
                                [f"- {fix}" for fix in report.get("priority_fixes")]
                            )
                        )
                else:
                    st.success("Fully Compliant.")

                # Reporting Export Simulation Artifact
                st.download_button(
                    "📩 Download Formal Compliance Audit Report",
                    data=json.dumps(report, indent=4),
                    file_name="compliance_audit.json",
                    mime="application/json",
                )

# --- Tab 6: LangSmith ---
with tab6:
    st.header("📊 LangSmith Observability & Native Tracing")
    if os.environ.get("LANGCHAIN_TRACING_V2") == "true":
        st.success(
            "🟢 Active internal traces are currently mapping all LLM inferences natively. Expand deep insights below!"
        )
        st.info("⚠️ **Note:** Strict Google OAuth SSO security policies actively prohibit rendering the LangSmith authentication dashboard via nested Iframes to prevent clickjacking.")
        st.markdown("<br>", unsafe_allow_html=True)
        st.link_button("🌐 Open External LangSmith Dashboard (EU)", "https://eu.smith.langchain.com/", type="primary", use_container_width=True)
    else:
        st.error(
            "🔴 LangSmith Tracing is offline. Please toggle 'LangSmith Observability' in the Access Governance sidebar to boot internal metrics."
        )
