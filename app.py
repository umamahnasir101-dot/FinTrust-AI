import streamlit as st
from groq import Groq
import os
import json
import re
import time

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="FinTrust AI", page_icon="🛡️", layout="centered")

api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
if not api_key:
    api_key = st.text_input("Paste your Groq API key to run this app:", type="password")
client = Groq(api_key=api_key) if api_key else None

if "page" not in st.session_state:
    st.session_state.page = "home"

def go_to(page):
    st.session_state.page = page
    st.rerun()

# ============================================================
# GLOBAL STYLING
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header {visibility: hidden;}

.stApp {
    background: radial-gradient(circle at 15% -10%, #132540 0%, #060a12 50%, #020409 100%);
    overflow-x: hidden;
}

.bg-particles {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0; overflow: hidden;
}
.particle {
    position: absolute; font-size: 26px; opacity: 0.16;
    animation: floatUp linear infinite;
}
@keyframes floatUp {
    0% { transform: translateY(110vh) translateX(0) rotate(0deg); opacity: 0; }
    10% { opacity: 0.18; }
    90% { opacity: 0.18; }
    100% { transform: translateY(-10vh) translateX(30px) rotate(360deg); opacity: 0; }
}

.logo-wrap { text-align: center; margin-top: 10px; }
.logo-shield {
    width: 92px; height: 92px; margin: 0 auto 14px auto;
    display: flex; align-items: center; justify-content: center;
    border-radius: 24px;
    background: linear-gradient(135deg, #0ee6b7 0%, #0891ff 100%);
    box-shadow: 0 0 40px rgba(14,230,183,0.35), 0 0 80px rgba(8,145,255,0.15);
    font-size: 44px;
    animation: pulseGlow 3s ease-in-out infinite;
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 0 40px rgba(14,230,183,0.35), 0 0 80px rgba(8,145,255,0.15); }
    50% { box-shadow: 0 0 55px rgba(14,230,183,0.55), 0 0 100px rgba(8,145,255,0.3); }
}

.hero-badge {
    display: inline-block; padding: 6px 16px; border-radius: 20px;
    background: linear-gradient(90deg, rgba(0,224,178,0.15), rgba(0,140,255,0.15));
    border: 1px solid rgba(0,224,178,0.35);
    color: #4be3c5; font-size: 12.5px; letter-spacing: 0.6px; font-weight: 600;
    margin-bottom: 16px;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif; font-size: 52px; font-weight: 800;
    margin: 6px 0 8px 0; text-align:center;
    background: linear-gradient(90deg, #ffffff 15%, #7fe9d4 55%, #4facfe 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: #96a2b8; font-size: 16.5px; max-width: 540px; margin: 0 auto; text-align: center; line-height: 1.5; }

.team-strip {
    text-align: center; margin-top: 22px; color: #5b6780; font-size: 13px;
    border-top: 1px solid rgba(255,255,255,0.06); padding-top: 16px;
}
.team-strip b { color: #9fb4c9; }

.feature-card {
    border-radius: 18px; padding: 1.5px; margin-top: 10px;
    background: linear-gradient(135deg, rgba(79,172,254,0.4), rgba(0,224,178,0.15));
}
.feature-card-inner {
    background: #0a1220; border-radius: 17px; padding: 28px 24px; text-align: center; height: 100%;
}
.feature-icon { font-size: 40px; margin-bottom: 10px; }
.feature-title { font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 700; color: #eef3fa; margin-bottom: 6px; }
.feature-desc { color: #8b98ab; font-size: 13.5px; line-height: 1.5; }

.page-header { text-align: center; margin-bottom: 18px; }
.page-header h2 {
    font-family: 'Space Grotesk', sans-serif; font-size: 30px; font-weight: 700; color: #eef3fa;
}
.page-header p { color: #8b98ab; font-size: 14.5px; }

.mode-card {
    border-radius: 16px; padding: 1px; margin: 18px 0;
    background: linear-gradient(135deg, rgba(79,172,254,0.35), rgba(0,224,178,0.15));
}
.mode-card-inner { background: #0b1220; border-radius: 15px; padding: 24px 26px; }

.check-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px; margin: 7px 0; border-radius: 10px;
    background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.06);
    font-size: 14.5px; color: #cdd6e3; animation: slideIn 0.4s ease;
}
@keyframes slideIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }

.verdict-box { padding: 24px; border-radius: 14px; margin-top: 18px; text-align: center; animation: popIn 0.35s ease; }
@keyframes popIn { from {opacity:0; transform: scale(0.96);} to {opacity:1; transform: scale(1);} }
.verdict-scam { background: linear-gradient(135deg, rgba(255,60,60,0.18), rgba(255,60,60,0.05)); border: 1px solid #ff4d4d; }
.verdict-suspicious { background: linear-gradient(135deg, rgba(255,180,0,0.18), rgba(255,180,0,0.05)); border: 1px solid #ffb400; }
.verdict-safe { background: linear-gradient(135deg, rgba(0,224,150,0.18), rgba(0,224,150,0.05)); border: 1px solid #00e096; }
.verdict-invest { background: linear-gradient(135deg, rgba(79,172,254,0.2), rgba(14,230,183,0.08)); border: 1px solid #4facfe; }
.verdict-title { font-family: 'Space Grotesk', sans-serif; font-size: 23px; font-weight: 700; margin-bottom: 4px; }
.verdict-sub { color: #aab4c4; font-size: 14px; }

.stat-grid { display: flex; gap: 14px; margin-top: 16px; }
.stat-box {
    flex: 1; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 14px; text-align: center;
}
.stat-box .val { font-family: 'Space Grotesk', sans-serif; font-size: 21px; font-weight: 700; color: #4be3c5; }
.stat-box .lbl { color: #7d899d; font-size: 12px; margin-top: 3px; }

.advisor-answer {
    background: rgba(79,172,254,0.06); border-left: 3px solid #4facfe;
    padding: 16px 18px; border-radius: 8px; color: #dbe3ee; line-height: 1.6; font-size: 15px;
}

.footer-note { text-align: center; color: #56617a; font-size: 12.5px; margin-top: 40px; }

.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] { background: rgba(255,255,255,0.03); border-radius: 10px 10px 0 0; padding: 10px 20px; font-weight: 600; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, rgba(0,224,178,0.15), rgba(79,172,254,0.15)) !important;
    color: #4be3c5 !important;
}
</style>

<div class="bg-particles">
""" + "".join([
    f'<div class="particle" style="left:{x}%; animation-duration:{d}s; animation-delay:{a}s;">{e}</div>'
    for x, d, a, e in [
        (5, 14, 0, "💵"), (15, 18, 2, "💰"), (25, 12, 4, "📈"), (35, 16, 1, "🪙"),
        (45, 20, 3, "💳"), (55, 13, 5, "💵"), (65, 17, 0.5, "📊"), (75, 15, 2.5, "🪙"),
        (85, 19, 1.5, "💰"), (92, 12, 3.5, "💵"),
    ]
]) + """
</div>
""", unsafe_allow_html=True)

# ============================================================
# KNOWLEDGE BASES
# ============================================================
LITERACY_KB = """
- A loan's "interest rate" is the extra cost of borrowing money, shown yearly (APR).
- "Compound interest" means earning/owing interest on top of interest already added.
- An emergency fund should ideally cover 3-6 months of essential expenses.
- Diversifying investments reduces risk; putting everything in one place increases it.
- Higher promised returns almost always mean higher risk.
- Money loses value over time to inflation, so idle cash sitting still is a hidden loss.
"""

SCAM_CHECK_LIST = [
    ("urgency", "Urgency or threat language ('act now', 'account blocked')"),
    ("otp_request", "Requests OTP, PIN, CNIC, or password"),
    ("too_good", "Too-good-to-be-true offer (prize, guaranteed high return)"),
    ("suspicious_link", "Suspicious or shortened link / fake domain"),
    ("grammar", "Poor grammar or unprofessional tone for an 'official' sender"),
    ("secrecy", "Pressure to act secretly or not tell anyone"),
    ("upfront_payment", "Asks you to pay/send money first to 'unlock' something"),
    ("impersonation", "Impersonates a bank/government body via personal contact"),
]

# ============================================================
# CALCULATION ENGINE (real math, not AI-guessed numbers)
# ============================================================
def project_investment(principal, monthly_contribution, years, expected_annual_return_pct):
    months = int(years * 12)
    monthly_rate = (expected_annual_return_pct / 100) / 12
    balance = principal
    for _ in range(months):
        balance = balance * (1 + monthly_rate) + monthly_contribution
    total_contributed = principal + monthly_contribution * months
    total_growth = balance - total_contributed
    return round(balance, 2), round(total_contributed, 2), round(total_growth, 2)

def assess_investment(principal, monthly_contribution, years, expected_return_pct, risk_tolerance, has_emergency_fund):
    final_value, contributed, growth = project_investment(principal, monthly_contribution, years, expected_return_pct)
    inflation_assumption = 10.0
    real_return = expected_return_pct - inflation_assumption

    flags = []
    if not has_emergency_fund:
        flags.append("No emergency fund in place — investing before this is risky.")
    if expected_return_pct >= 30:
        flags.append(f"Expected return of {expected_return_pct}% is unusually high — treat with caution, verify legitimacy.")
    if real_return < 0:
        flags.append(f"Expected return ({expected_return_pct}%) may not beat estimated inflation (~{inflation_assumption}%) — real value growth could be minimal.")
    if risk_tolerance == "Low" and expected_return_pct > 15:
        flags.append("Your risk tolerance is Low, but this return target implies a higher-risk investment.")

    if not has_emergency_fund or (risk_tolerance == "Low" and expected_return_pct > 20):
        decision = "hold"
    elif flags and expected_return_pct >= 30:
        decision = "caution"
    else:
        decision = "go"

    return {
        "final_value": final_value,
        "contributed": contributed,
        "growth": growth,
        "real_return": round(real_return, 1),
        "flags": flags,
        "decision": decision,
    }

# ============================================================
# LLM CALLS
# ============================================================
def get_investment_reasoning(inputs, calc):
    system = f"""You are FinTrust AI's investment decision agent. You are given REAL calculated numbers (already computed correctly — do not recalculate or invent new numbers, just reason over them).

User inputs: {json.dumps(inputs)}
Calculated results: {json.dumps(calc)}

Write a clear, honest recommendation in plain language:
1. State the decision (Go ahead / Proceed with caution / Hold off) matching calc['decision'] (go/caution/hold).
2. Give 3-4 specific reasons using the actual numbers provided.
3. Mention any flags from calc['flags'] naturally in your reasoning.
4. End with one practical next step.
Keep it to 5-7 sentences, no markdown headers, warm and direct tone."""
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": "Give me your recommendation."}],
                temperature=0.3,
            )
            return resp.choices[0].message.content
        except Exception:
            time.sleep(0.6)
    return "We couldn't generate the detailed written reasoning right now, but the calculated numbers and decision above are accurate and based on your inputs."

def get_scam_analysis(message_text):
    checklist_str = "\n".join([f'- "{key}": {desc}' for key, desc in SCAM_CHECK_LIST])
    system = f"""You are FinTrust AI's fraud detection agent. Analyze the message against this checklist:
{checklist_str}

Respond ONLY with valid JSON, no markdown, no extra text, in this exact format:
{{
  "checks": {{"urgency": true/false, "otp_request": true/false, "too_good": true/false, "suspicious_link": true/false, "grammar": true/false, "secrecy": true/false, "upfront_payment": true/false, "impersonation": true/false}},
  "verdict": "scam" or "suspicious" or "safe",
  "explanation": "2-3 sentence plain-language explanation of the verdict"
}}"""
    last_error = None
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": message_text}],
                temperature=0.2,
            )
            raw = resp.choices[0].message.content.strip()
            raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if match:
                raw = match.group(0)
            return json.loads(raw)
        except Exception as e:
            last_error = e
            time.sleep(0.6)
    # Fallback so the demo never crashes even if the model misbehaves 3x in a row
    return {
        "checks": {k: False for k, _ in SCAM_CHECK_LIST},
        "verdict": "suspicious",
        "explanation": "Could not fully analyze this message right now — treat with caution and verify through official channels.",
    }

# ============================================================
# PAGE: HOME
# ============================================================
def render_home():
    logo_col = st.columns([1, 1, 1])[1]
    with logo_col:
        st.image("assets/logo.png", use_container_width=True)

    st.markdown("""
    <div class="hero" style="margin-top:-10px;">
        <div style="text-align:center;"><span class="hero-badge">🚀 AI AGENT · FINTECH · TEAM FINTEL</span></div>
        <h1>FinTrust AI</h1>
        <p>Your AI guardian for financial trust. One agent, two jobs: helping you make smart investment decisions with real math, and catching scams before they catch you.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="feature-card"><div class="feature-card-inner">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Investment Decision</div>
            <div class="feature-desc">Enter your amount, timeline, and goals — get a real, calculated recommendation with clear reasoning.</div>
        </div></div>
        """, unsafe_allow_html=True)
        if st.button("Open Investment Advisor →", use_container_width=True, type="primary"):
            go_to("investment")
    with col2:
        st.markdown("""
        <div class="feature-card"><div class="feature-card-inner">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Scam Checker</div>
            <div class="feature-desc">Paste a suspicious SMS, email, or WhatsApp message — watch the agent investigate step-by-step.</div>
        </div></div>
        """, unsafe_allow_html=True)
        if st.button("Open Scam Checker →", use_container_width=True, type="primary"):
            go_to("scam")

    st.markdown("""
    <div class="team-strip">
        Built by <b>Team Fintel</b> &nbsp;·&nbsp; Umamah Nasir &amp; Chaudhary Muhammad Huzaifa Ali
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE: INVESTMENT ADVISOR
# ============================================================
def render_investment():
    if st.button("← Back to Home"):
        go_to("home")

    st.markdown("""
    <div class="page-header">
        <h2>📊 Investment Decision Advisor</h2>
        <p>Real calculations, not guesses — tell us your numbers and get a grounded recommendation.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="mode-card"><div class="mode-card-inner">', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        principal = st.number_input("How much do you have to invest now? (PKR)", min_value=0, value=100000, step=5000)
        years = st.slider("Investment time horizon (years)", 1, 30, 5)
        risk_tolerance = st.select_slider("Your risk tolerance", options=["Low", "Medium", "High"], value="Medium")
    with c2:
        monthly_contribution = st.number_input("Additional monthly contribution (PKR)", min_value=0, value=5000, step=500)
        expected_return_pct = st.slider("Expected annual return (%)", 1, 50, 12)
        has_emergency_fund = st.radio("Do you already have an emergency fund (3-6 months expenses)?", ["Yes", "No"]) == "Yes"

    if st.button("🧭 Analyze My Investment", type="primary", use_container_width=True):
        inputs = {
            "principal": principal, "monthly_contribution": monthly_contribution,
            "years": years, "expected_return_pct": expected_return_pct,
            "risk_tolerance": risk_tolerance, "has_emergency_fund": has_emergency_fund,
        }
        calc = assess_investment(principal, monthly_contribution, years, expected_return_pct, risk_tolerance, has_emergency_fund)

        st.markdown("**Agent reasoning trail:**")
        placeholder = st.empty()
        rows = [
            f"Calculating projected value after {years} years at {expected_return_pct}% annual return...",
            f"Comparing return against estimated regional inflation (~10%)...",
            f"Checking emergency fund status: {'✅ In place' if has_emergency_fund else '🚩 Not in place'}...",
            f"Checking risk tolerance ({risk_tolerance}) against target return...",
        ]
        html = ""
        for r in rows:
            html += f'<div class="check-row">⚙️ {r}</div>'
            placeholder.markdown(html, unsafe_allow_html=True)
            time.sleep(0.25)

        st.markdown(f"""
        <div class="stat-grid">
            <div class="stat-box"><div class="val">PKR {calc['final_value']:,.0f}</div><div class="lbl">Projected Final Value</div></div>
            <div class="stat-box"><div class="val">PKR {calc['contributed']:,.0f}</div><div class="lbl">Total Contributed</div></div>
            <div class="stat-box"><div class="val">PKR {calc['growth']:,.0f}</div><div class="lbl">Total Growth</div></div>
        </div>
        """, unsafe_allow_html=True)

        decision_map = {
            "go": ("verdict-invest", "✅ Go Ahead", "This looks like a reasonable plan based on your numbers."),
            "caution": ("verdict-suspicious", "⚠️ Proceed With Caution", "Some flags to consider before committing."),
            "hold": ("verdict-scam", "🛑 Hold Off For Now", "There are important gaps to address first."),
        }
        css_class, title, sub = decision_map[calc["decision"]]
        st.markdown(f"""
        <div class="verdict-box {css_class}">
            <div class="verdict-title">{title}</div>
            <div class="verdict-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

        if client:
            with st.spinner("Writing detailed reasoning..."):
                try:
                    reasoning = get_investment_reasoning(inputs, calc)
                    st.markdown(f'<div class="advisor-answer">{reasoning}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Reasoning generation failed: {e}")
        else:
            st.warning("Add your Groq API key to get full written reasoning.")

    st.markdown('</div></div>', unsafe_allow_html=True)

# ============================================================
# PAGE: SCAM CHECKER
# ============================================================
def render_scam():
    if st.button("← Back to Home"):
        go_to("home")

    st.markdown("""
    <div class="page-header">
        <h2>🔍 Scam & Fraud Checker</h2>
        <p>Paste any suspicious SMS, email, or WhatsApp message — the agent investigates 8 known fraud patterns.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="mode-card"><div class="mode-card-inner">', unsafe_allow_html=True)

    if st.button("🚩 Try example scam message", use_container_width=True):
        st.session_state["scam_input"] = "URGENT: Your bank account will be suspended in 1 hour. Reply with your OTP code immediately to verify your account and avoid suspension."

    msg = st.text_area("Paste the message here:", key="scam_input", height=110,
                        placeholder="e.g. Congratulations! You've won PKR 500,000. Send your CNIC and account number to claim...")

    if st.button("🔍 Investigate This Message", type="primary", use_container_width=True):
        if not client:
            st.error("Add your Groq API key first.")
        elif not msg.strip():
            st.warning("Paste a message first.")
        else:
            try:
                with st.spinner("Analyzing..."):
                    result = get_scam_analysis(msg)

                st.markdown("**Agent reasoning trail:**")
                placeholder = st.empty()
                rows_html = ""
                for key, desc in SCAM_CHECK_LIST:
                    flagged = result["checks"].get(key, False)
                    icon = "🚩" if flagged else "✅"
                    rows_html += f'<div class="check-row"><span>{icon}</span> {desc}</div>'
                    placeholder.markdown(rows_html, unsafe_allow_html=True)
                    time.sleep(0.15)

                verdict = result.get("verdict", "suspicious")
                verdict_map = {
                    "scam": ("verdict-scam", "🚩 Likely Scam", "High risk — do not click links, share OTPs, or send money."),
                    "suspicious": ("verdict-suspicious", "⚠️ Suspicious — Be Careful", "Some red flags found. Verify through official channels before acting."),
                    "safe": ("verdict-safe", "✅ Looks Safe", "No major red flags detected — but always stay cautious."),
                }
                css_class, title, sub = verdict_map.get(verdict, verdict_map["suspicious"])
                st.markdown(f"""
                <div class="verdict-box {css_class}">
                    <div class="verdict-title">{title}</div>
                    <div class="verdict-sub">{sub}</div>
                </div>
                """, unsafe_allow_html=True)
                st.info(result.get("explanation", ""))
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    st.markdown('</div></div>', unsafe_allow_html=True)

# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "investment":
    render_investment()
elif st.session_state.page == "scam":
    render_scam()

st.markdown('<div class="footer-note">Built for a hackathon 🚀 &nbsp;|&nbsp; Powered by Groq + Llama 3.3 &nbsp;|&nbsp; Team Fintel</div>', unsafe_allow_html=True)
