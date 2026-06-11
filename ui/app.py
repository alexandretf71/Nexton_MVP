import base64
import os
import sys

import httpx
import streamlit as st

# ui/export.py lives alongside app.py — ensure its directory is on the path
sys.path.insert(0, os.path.dirname(__file__))
from export import generate_blueprint_docx

# rstrip: a trailing slash in the env var would produce "//health" URLs (404).
API_BASE = os.getenv("UI_API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="AI Implementation Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand styles — aligned to nexton.dev visual identity ─────────────────────
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=K2D:wght@500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        /* ── Base ── */
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background-color: #F9FAFB !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* ── Sidebar — dark hero style, matches nexton.dev nav ── */
        [data-testid="stSidebar"] {
            background-color: #0B0F19 !important;
            border-right: none;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #F9FAFB !important;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] li,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
            color: #C9CED6 !important;
        }
        [data-testid="stSidebar"] hr {
            border-color: #2A3040 !important;
        }

        /* ── Top accent bar — matches nexton.dev blue strip ── */
        [data-testid="stAppViewContainer"] {
            border-top: 6px solid #337BFF;
        }

        /* ── Typography ── */
        h1, h2, h3 {
            font-family: 'K2D', 'Inter', system-ui, sans-serif !important;
            color: #172344 !important;
            letter-spacing: -0.02em !important;
        }
        h1 {
            font-weight: 800 !important;
            line-height: 1.1 !important;
        }
        h2, h3 { font-weight: 700 !important; }
        p, li { color: #444444; }
        label { color: #172344 !important; font-weight: 500; }

        /* ── Primary button — blue (matches Nexton CTA style) ── */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background-color: #337BFF !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.6rem 2rem !important;
            transition: background-color 0.18s ease !important;
        }
        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #0051E5 !important;
            border: none !important;
        }

        /* ── Inputs ── */
        .stTextArea textarea,
        .stTextInput input {
            background-color: #FFFFFF !important;
            color: #172344 !important;
            border: 1.5px solid #D6DEE8 !important;
            border-radius: 8px !important;
        }
        .stTextArea textarea:focus,
        .stTextInput input:focus {
            border-color: #337BFF !important;
            box-shadow: 0 0 0 2px rgba(51, 123, 255, 0.15) !important;
        }

        /* ── Selectbox ── */
        [data-testid="stSelectbox"] > div > div {
            background-color: #FFFFFF !important;
            border: 1.5px solid #D6DEE8 !important;
            border-radius: 8px !important;
            color: #172344 !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab"] {
            color: #888888 !important;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #337BFF !important;
            border-bottom-color: #337BFF !important;
            font-weight: 700 !important;
        }

        /* ── Expanders ── */
        [data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 8px !important;
            margin-bottom: 6px;
        }

        /* ── Form card ── */
        [data-testid="stForm"] {
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 1.5rem;
        }

        /* ── Metrics ── */
        [data-testid="stMetricLabel"] { color: #6B7280 !important; font-weight: 500; }
        [data-testid="stMetricValue"] { color: #172344 !important; font-weight: 800; }

        /* ── Dividers ── */
        hr { border-color: #E5E7EB !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(show_spinner=False)
def _load_asset_b64(path: str) -> str | None:
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    except FileNotFoundError:
        return None


def _build_org_chart_dot(roles: list[dict]) -> str:
    # reports_to values without a matching role become synthesized root nodes,
    # so an LLM that names an external manager still yields a valid chart.
    def _esc(s: str) -> str:
        return s.replace('"', '\\"')

    role_names = {r["role"] for r in roles}
    lines = [
        "digraph org {",
        "  rankdir=TB;",
        '  node [shape=box, style="rounded,filled", fillcolor="#F1F6FF", '
        'color="#337BFF", fontname="Inter", fontsize=11];',
    ]
    for parent in {r["reports_to"] for r in roles} - role_names:
        lines.append(
            f'  "{_esc(parent)}" [fillcolor="#172344", fontcolor="#FFFFFF"];'
        )
    for r in roles:
        label = f"{_esc(r['role'])}\\n×{r['count']} · {_esc(r['seniority'])}"
        lines.append(f'  "{_esc(r["role"])}" [label="{label}"];')
        lines.append(f'  "{_esc(r["reports_to"])}" -> "{_esc(r["role"])}";')
    lines.append("}")
    return "\n".join(lines)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    _logo_b64 = _load_asset_b64(
        os.path.join(os.path.dirname(__file__), "assets", "Nexton Logo_black.png")
    )
    if _logo_b64:
        st.markdown(
            f"""
            <div style="padding:0.5rem 0 0.75rem 0;">
                <img src="data:image/png;base64,{_logo_b64}"
                     style="width:100%;display:block;">
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown("## Nexton")

    _sidebar_photo_b64 = _load_asset_b64(
        os.path.join(os.path.dirname(__file__), "assets", "Alexandretf_perfil_Jan_26.jfif")
    )
    _sidebar_photo_tag = (
        f'<img src="data:image/jpeg;base64,{_sidebar_photo_b64}" '
        'style="width:36px;height:36px;border-radius:50%;object-fit:cover;'
        'flex-shrink:0;border:1.5px solid #DDDDDD;">'
        if _sidebar_photo_b64 else ""
    )
    st.markdown(
        f"""
        <div style="margin: 0.5rem 0 1rem 0;">
            <p style="font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
                      text-transform: uppercase; color: #337BFF; margin-bottom: 0.25rem;">
                AI Implementation Copilot
            </p>
            <div style="display:flex;align-items:center;gap:0.6rem;">
                {_sidebar_photo_tag}
                <p style="font-size:0.68rem;color:#AAAAAA;line-height:1.6;margin:0;">
                    Developed by <strong style="color:#888888;">Alexandre T. F.</strong><br>
                    <a href="mailto:alexandre@nexton.dev"
                       style="color:#AAAAAA;text-decoration:none;letter-spacing:0.01em;">
                        alexandre@nexton.dev
                    </a>
                    &nbsp;<span style="font-size:0.55rem;vertical-align:super;">®</span>
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    # ── LLM Settings ─────────────────────────────────────────────────────────
    st.markdown("### LLM Settings")
    _provider_labels = {
        "mock": "🔧 Mock (demo mode)",
        "anthropic": "🤖 Anthropic Claude",
        "openai": "💚 OpenAI",
    }
    st.selectbox(
        "Provider",
        options=list(_provider_labels.keys()),
        format_func=lambda x: _provider_labels[x],
        key="llm_provider",
    )
    _selected = st.session_state.get("llm_provider", "mock")
    if _selected in ("anthropic", "openai"):
        _placeholder = "sk-ant-..." if _selected == "anthropic" else "sk-..."
        st.text_input(
            "API Key",
            type="password",
            placeholder=_placeholder,
            help=(
                "Stored in this browser session only. "
                "Never saved to disk or committed to version control."
            ),
            key="llm_api_key",
        )
        if not st.session_state.get("llm_api_key"):
            st.caption("⚠️ Enter your API key to generate real blueprints.")
    st.markdown("---")

    # Health check
    try:
        httpx.get(f"{API_BASE}/health", timeout=3).raise_for_status()
        _display = _provider_labels.get(_selected, _selected)
        st.success(f"API online · provider: **{_display}**")
    except Exception:
        st.error("API offline — start the FastAPI server first.")

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="margin:0.5rem 0 1.5rem 0;">
        <h1 style="font-family:'K2D',sans-serif;
                   font-size:clamp(1.8rem,3.2vw,2.6rem); font-weight:800;
                   line-height:1.15; color:#172344; letter-spacing:-0.02em;
                   margin:0 0 0.5rem 0;">
            Nexton AI Division<br>
            <span style="background-color:#337BFF; color:#FFFFFF;
                         padding:0.05em 0.2em; border-radius:6px;">
                Blueprint planner
            </span>
        </h1>
        <p style="color:#666666; font-size:1.05rem; margin:0;">
            Describe the operational challenge. Receive a structured
            14-section implementation plan in seconds.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("blueprint_form"):
    business_problem = st.text_area(
        "Business Needs and Pain Points *",
        height=180,
        placeholder=(
            "Describe the operational challenge in your own words. "
            "Include symptoms, current process, pain points, and impact. "
            "No need to structure it — just be specific."
        ),
    )
    company_context = st.text_area(
        "Company Context (optional)",
        height=180,
        placeholder="e.g. ERP system, team size, tech stack",
    )
    industry = st.text_input("Industry (optional)", placeholder="e.g. Logistics, Finance, HR")
    submitted = st.form_submit_button("Generate Blueprint", use_container_width=True)

# ── Blueprint generation ──────────────────────────────────────────────────────
if submitted:
    if not business_problem or len(business_problem.strip()) < 50:
        st.error("Please describe the problem in at least 50 characters.")
        st.stop()

    payload = {"business_problem": business_problem.strip()}
    if industry.strip():
        payload["industry"] = industry.strip()
    if company_context.strip():
        payload["company_context"] = company_context.strip()

    # Build provider-override headers from sidebar session state.
    # The API key is passed as a header and never stored server-side.
    headers: dict[str, str] = {}
    if st.session_state.get("llm_provider") in ("anthropic", "openai"):
        api_key = st.session_state.get("llm_api_key", "")
        if not api_key:
            provider_name = st.session_state.get("llm_provider", "").capitalize()
            st.error(f"Enter your {provider_name} API key in the sidebar before generating.")
            st.stop()
        headers["X-LLM-Provider"] = st.session_state["llm_provider"]
        headers["X-API-Key"] = api_key

    with st.spinner("Generating blueprint…"):
        try:
            response = httpx.post(
                f"{API_BASE}/generate-blueprint",
                json=payload,
                headers=headers,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
        except httpx.HTTPStatusError as exc:
            st.error(f"API error {exc.response.status_code}: {exc.response.text}")
            st.stop()
        except Exception as exc:
            st.error(f"Could not reach the API: {exc}")
            st.stop()

    if not result.get("success"):
        st.error(f"Blueprint generation failed: {result.get('error', 'unknown error')}")
        st.stop()

    bp = result["data"]

    # ── Metadata bar ─────────────────────────────────────────────────────────
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Solution Type", bp["recommended_solution_type"])
    m2.metric("Provider", bp["provider_used"])
    m3.metric("Generated", bp["generated_at"][:19].replace("T", " ") + " UTC")

    # ── Download ──────────────────────────────────────────────────────────────
    _date_slug = (bp.get("generated_at") or "")[:10]
    st.download_button(
        label="⬇ Download Blueprint (.docx)",
        data=generate_blueprint_docx(bp),
        file_name=f"ai_blueprint_{_date_slug}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    # ── Tabs for 14 sections ──────────────────────────────────────────────────
    tabs = st.tabs([
        "📋 Diagnosis",
        "💢 Pain Points",
        "🎯 Opportunities",
        "🏗 Architecture",
        "🤖 Agentic Flow",
        "🗄 Data",
        "🔌 Integrations",
        "📝 Backlog",
        "⚠️ Risks",
        "🧪 Testing",
        "📣 Exec Summary",
        "📊 Status Report",
        "👥 Delivery Team",
        "🔍 Raw JSON",
    ])

    with tabs[0]:
        st.markdown("### Business Problem Summary")
        st.markdown(bp["business_problem_summary"])

    with tabs[1]:
        st.markdown("### Operational Pain Points")
        for point in bp["operational_pain_points"]:
            st.markdown(f"- {point}")

    with tabs[2]:
        st.markdown("### AI Opportunity Classification")
        for opp in bp["ai_opportunity_classification"]:
            with st.expander(f"**{opp['title']}**  —  Impact: {opp['impact']} · Feasibility: {opp['feasibility']}"):
                st.markdown(opp["description"])

    with tabs[3]:
        st.markdown("### Suggested Architecture")
        st.markdown(bp["suggested_architecture"])

    with tabs[4]:
        st.markdown("### Agentic Workflow")
        for step in bp["agentic_workflow"]:
            with st.expander(f"Step {step['step_number']}: **{step['agent_name']}**"):
                st.markdown(f"**Action:** {step['action']}")
                st.markdown(f"**Input:** {step['input']}")
                st.markdown(f"**Output:** {step['output']}")
                st.markdown(f"**Tools:** {', '.join(step['tools_used'])}")

    with tabs[5]:
        st.markdown("### Data Requirements")
        _avail_badge = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}
        for req in bp["data_requirements"]:
            badge = _avail_badge.get(req["availability"], "⚪")
            with st.expander(f"{badge} **{req['source']}**  —  Availability: {req['availability']}"):
                st.markdown(req["description"])
                if req.get("notes"):
                    st.caption(f"📌 {req['notes']}")

    with tabs[6]:
        st.markdown("### Integration Points")
        _cplx_badge = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        for integ in bp["integration_points"]:
            badge = _cplx_badge.get(integ["complexity"], "⚪")
            with st.expander(f"{badge} **{integ['system']}**  —  {integ['integration_type']} · Complexity: {integ['complexity']}"):
                st.markdown(integ["description"])

    with tabs[7]:
        st.markdown("### Engineering Backlog")
        for ticket in bp["engineering_backlog"]:
            badge = {"P0": "🔴", "P1": "🟠", "P2": "🟡", "P3": "🟢"}.get(ticket["priority"], "⚪")
            with st.expander(f"{badge} [{ticket['id']}] {ticket['title']}  —  {ticket['effort']} · {ticket['phase']}"):
                st.markdown(ticket["description"])

    with tabs[8]:
        st.markdown("### Risks and Assumptions")
        for risk in bp["risks_and_assumptions"]:
            with st.expander(f"**{risk['id']}** [{risk['category']}]  —  Likelihood: {risk['likelihood']} · Impact: {risk['impact']}"):
                st.markdown(f"**Risk:** {risk['description']}")
                st.markdown(f"**Mitigation:** {risk['mitigation']}")

    with tabs[9]:
        st.markdown("### Testing Plan")
        for tc in bp["testing_plan"]:
            with st.expander(f"**{tc['id']}** [{tc['type']}] {tc['description']}"):
                st.markdown(f"**Expected outcome:** {tc['expected_outcome']}")

    with tabs[10]:
        st.markdown("### Executive Summary")
        st.markdown(bp["executive_summary"])

    with tabs[11]:
        st.markdown("### Delivery Status Report")
        for milestone in bp["delivery_status_report"]:
            with st.expander(f"**Week {milestone['week']}: {milestone['title']}**  —  Owner: {milestone['owner']}"):
                for d in milestone["deliverables"]:
                    st.markdown(f"- {d}")

    with tabs[12]:
        st.markdown("### Delivery Team")
        st.info(
            "ℹ️ Team sizing assumes a deliberately reduced team optimized by "
            "AI-assisted coding tools (e.g. Claude Code, GitHub Copilot, Cursor). "
            "Traditional staffing for the same scope would be substantially larger."
        )
        team = bp["delivery_team"]
        for r in team["roles"]:
            _role_title = f"**{r['role']}** ×{r['count']}  —  {r['seniority']} · {r['allocation']}"
            with st.expander(_role_title):
                st.markdown(r["responsibilities"])
                st.caption(f"Reports to: {r['reports_to']}")

        st.markdown("### Org Chart")
        st.graphviz_chart(_build_org_chart_dot(team["roles"]), use_container_width=True)

        st.markdown("### Fulfillment Plan")
        _action_badge = {"HIRE": "🟣", "INTERNAL_ALLOCATION": "🔵", "CONTRACTOR": "🟠"}
        for fa in team["fulfillment_plan"]:
            badge = _action_badge.get(fa["action"], "⚪")
            with st.expander(f"{badge} Week {fa['week']}: **{fa['role']}**  —  {fa['action']}"):
                st.markdown(fa["notes"])

    with tabs[13]:
        st.markdown("### Raw JSON Response")
        st.json(result)
