import base64
import os
import sys

import httpx
import streamlit as st
import streamlit.components.v1 as components

# ui/export.py lives alongside app.py — ensure its directory is on the path
sys.path.insert(0, os.path.dirname(__file__))
from export import generate_blueprint_docx

API_BASE = os.getenv("UI_API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="AI Implementation Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand styles — aligned to zaigo.ai visual identity ───────────────────────
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

        /* ── Base ── */
        html, body,
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background-color: #F4F1EC !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #E5E0D8;
        }

        /* ── Typography ── */
        h1 {
            color: #1A1A1A !important;
            font-weight: 900 !important;
            letter-spacing: -0.03em !important;
            line-height: 1.1 !important;
        }
        h2, h3 {
            color: #1A1A1A !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }
        p, li { color: #444444; }
        label { color: #1A1A1A !important; font-weight: 500; }

        /* ── Primary button — red pill (matches Zaigo CTA style) ── */
        .stButton > button,
        [data-testid="stFormSubmitButton"] > button {
            background-color: #E8412E !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.6rem 2rem !important;
            transition: background-color 0.18s ease !important;
        }
        .stButton > button:hover,
        [data-testid="stFormSubmitButton"] > button:hover {
            background-color: #C8301E !important;
            border: none !important;
        }

        /* ── Inputs ── */
        .stTextArea textarea,
        .stTextInput input {
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
            border: 1.5px solid #D5CFC5 !important;
            border-radius: 8px !important;
        }
        .stTextArea textarea:focus,
        .stTextInput input:focus {
            border-color: #E8412E !important;
            box-shadow: 0 0 0 2px rgba(232, 65, 46, 0.15) !important;
        }

        /* ── Selectbox ── */
        [data-testid="stSelectbox"] > div > div {
            background-color: #FFFFFF !important;
            border: 1.5px solid #D5CFC5 !important;
            border-radius: 8px !important;
            color: #1A1A1A !important;
        }

        /* ── Tabs ── */
        .stTabs [data-baseweb="tab"] {
            color: #888888 !important;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            color: #E8412E !important;
            border-bottom-color: #E8412E !important;
            font-weight: 700 !important;
        }

        /* ── Expanders ── */
        [data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E0D8 !important;
            border-radius: 8px !important;
            margin-bottom: 6px;
        }

        /* ── Form card ── */
        [data-testid="stForm"] {
            background-color: #FFFFFF;
            border: 1px solid #E5E0D8;
            border-radius: 12px;
            padding: 1.5rem;
        }

        /* ── Metrics ── */
        [data-testid="stMetricLabel"] { color: #888888 !important; font-weight: 500; }
        [data-testid="stMetricValue"] { color: #1A1A1A !important; font-weight: 800; }

        /* ── Dividers ── */
        hr { border-color: #E5E0D8 !important; }
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


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "zaigo_logo.jfif")
    try:
        st.image(logo_path, use_container_width=True)
    except Exception:
        st.markdown("## Zaigo AI")

    st.markdown(
        """
        <div style="margin: 0.5rem 0 1rem 0;">
            <p style="font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
                      text-transform: uppercase; color: #E8412E; margin-bottom: 0.25rem;">
                AI Implementation Copilot
            </p>
            <p style="font-size: 0.85rem; color: #666666; line-height: 1.5; margin: 0;">
                Paste a messy business problem and receive a structured blueprint in seconds.
            </p>
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

    _photo_b64 = _load_asset_b64(
        os.path.join(os.path.dirname(__file__), "assets", "Alexandretf_perfil_Jan_26.jfif")
    )
    _photo_tag = (
        f'<img src="data:image/jpeg;base64,{_photo_b64}" '
        'style="width:36px;height:36px;border-radius:50%;object-fit:cover;'
        'flex-shrink:0;border:1.5px solid #DDDDDD;">'
        if _photo_b64 else ""
    )
    st.markdown(
        f"""
        <div style="margin-top: 2rem; padding: 0 0.5rem;">
            <div style="display:flex;align-items:center;gap:0.6rem;">
                <div style="flex:1; text-align:left;">
                    <p style="font-size:0.68rem;color:#AAAAAA;line-height:1.6;margin:0;">
                        Developed by <strong style="color:#888888;">Alexandre T. F.</strong><br>
                        <a href="mailto:alexandre@zaigo.ai"
                           style="color:#AAAAAA;text-decoration:none;letter-spacing:0.01em;">
                            alexandre@zaigo.ai
                        </a>
                        &nbsp;<span style="font-size:0.55rem;vertical-align:super;">®</span>
                    </p>
                </div>
                {_photo_tag}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Hero video card ───────────────────────────────────────────────────────────
_assets_dir = os.path.join(os.path.dirname(__file__), "assets")
_video_b64  = _load_asset_b64(os.path.join(_assets_dir, "Sovi_flying.mp4"))
_poster_b64 = _load_asset_b64(os.path.join(_assets_dir, "SOVI_High3_bw_black.jpg"))

if _video_b64:
    _poster_attr = (
        f'poster="data:image/jpeg;base64,{_poster_b64}"' if _poster_b64 else ""
    )
    components.html(
        f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; overflow: hidden;
          font-family: 'Inter', system-ui, -apple-system, sans-serif; }}
  .hero-card {{
    position: relative; width: 100%; height: 360px;
    border-radius: 16px; background: #111; overflow: hidden;
  }}
  .hero-card video {{
    position: absolute; inset: 0; width: 100%; height: 100%;
    object-fit: cover; filter: grayscale(100%) brightness(0.75);
  }}
  .hero-text {{
    position: absolute; bottom: 0; left: 0; padding: 2rem; z-index: 2;
    text-shadow: 0 1px 6px rgba(0,0,0,0.7);
  }}
  .eyebrow {{
    display: block; font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: rgba(255,255,255,0.55); margin-bottom: 0.5rem;
  }}
  .title {{
    font-size: 2rem; font-weight: 900;
    letter-spacing: -0.025em; line-height: 1.15;
    color: #ffffff; margin-bottom: 0.75rem;
  }}
  .highlight {{
    background-color: #E8412E; color: #ffffff;
    padding: 0.03em 0.18em; border-radius: 4px;
  }}
  .subtitle {{
    font-size: 0.875rem; color: rgba(255,255,255,0.65); line-height: 1.5;
  }}
</style>
</head>
<body>
<div class="hero-card">
  <video autoplay muted loop playsinline {_poster_attr}>
    <source src="data:video/mp4;base64,{_video_b64}" type="video/mp4">
  </video>
  <div class="hero-text">
    <span class="eyebrow">AI Implementation Copilot</span>
    <h1 class="title">
      Turn any business problem into<br>
      <span class="highlight">an AI blueprint.</span>
    </h1>
    <p class="subtitle">
      Describe the operational challenge. Receive a structured 13-section<br>
      implementation plan in seconds.
    </p>
  </div>
</div>
</body></html>""",
        height=376,
        scrolling=False,
    )
else:
    # Fallback when video asset is absent (fresh clone, CI)
    st.markdown(
        """
        <div style="margin: 1.5rem 0 2rem 0;">
            <h1 style="font-size: clamp(2rem,4vw,3.2rem); font-weight: 900;
                       line-height: 1.1; color: #1A1A1A; letter-spacing: -0.03em;
                       margin-bottom: 0.75rem;">
                Turn any business problem into<br>
                <span style="background-color: #E8412E; color: #FFFFFF;
                             padding: 0.05em 0.2em; border-radius: 4px;">
                    an AI blueprint.
                </span>
            </h1>
            <p style="color: #666666; font-size: 1.1rem; margin-top: 0.5rem;">
                Describe the operational challenge. Receive a structured
                13-section implementation plan in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.form("blueprint_form"):
    business_problem = st.text_area(
        "Business Problem *",
        height=180,
        placeholder=(
            "Describe the operational challenge in your own words. "
            "Include symptoms, current process, pain points, and impact. "
            "No need to structure it — just be specific."
        ),
    )
    col1, col2 = st.columns(2)
    with col1:
        industry = st.text_input("Industry (optional)", placeholder="e.g. Logistics, Finance, HR")
    with col2:
        company_context = st.text_input(
            "Company Context (optional)",
            placeholder="e.g. ERP system, team size, tech stack",
        )
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

    # ── Tabs for 13 sections ──────────────────────────────────────────────────
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
        st.markdown("### Raw JSON Response")
        st.json(result)
