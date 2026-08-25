import streamlit as st
from groq import Groq
import os
import json
import re
import time

# ---------- CONFIG ----------
st.set_page_config(page_title="FinTrust AI", page_icon="🛡️", layout="centered")

# ---------- API KEY HANDLING ----------
api_key = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
if not api_key:
    api_key = st.text_input("Paste your Groq API key to run this app:", type="password")
client = Groq(api_key=api_key) if api_key else None

# ---------- PREMIUM STYLING ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(circle at 20% 0%, #0f1b2e 0%, #060a12 55%, #030509 100%);
}

#MainMenu, footer {visibility: hidden;}

.hero { text-align: center; padding: 18px 0 6px 0; }
.hero-badge {
    display: inline-block; padding: 5px 14px; border-radius: 20px;
    background: linear-gradient(90deg, rgba(0,224,178,0.15), rgba(0,140,255,0.15));
    border: 1px solid rgba(0,224,178,0.35);
    color: #4be3c5; font-size: 12.5px; letter-spacing: 0.5px; font-weight: 600;
    margin-bottom: 14px;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif; font-size: 46px; font-weight: 700;
    margin: 4px 0 6px 0;
    background: linear-gradient(90deg, #ffffff 20%, #7fe9d4 60%, #4facfe 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero p { color: #8b98ab; font-size: 16px; max-width: 520px; margin: 0 auto; }

.mode-card {
    border-radius: 16px; padding: 1px;
    background: linear-gradient(135deg, rgba(79,172,254,0.35), rgba(0,224,178,0.15));
    margin: 22px 0 6px 0;
}
.mode-card-inner { background: #0b1220; border-radius: 15px; padding: 22px 24px; }

.check-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px; margin: 7px 0; border-radius: 10px;
    background: rgba(255,255,255,0.035); border: 1px solid rgba(255,255,255,0.06);
    font-size: 14.5px; color: #cdd6e3; animation: slideIn 0.4s ease;
}
@keyframes slideIn { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }
.check-icon { font-size: 16px; }

.verdict-box { padding: 22px; border-radius: 14px; margin-top: 18px; text-align: center; animation: popIn 0.35s ease; }
@keyframes popIn { from {opacity:0; transform: scale(0.96);} to {opacity:1; transform: scale(1);} }
.verdict-scam { background: linear-gradient(135deg, rgba(255,60,60,0.18), rgba(255,60,60,0.05)); border: 1px solid #ff4d4d; }
.verdict-suspicious { background: linear-gradient(135deg, rgba(255,180,0,0.18), rgba(255,180,0,0.05)); border: 1px solid #ffb400; }
.verdict-safe { background: linear-gradient(135deg, rgba(0,224,150,0.18), rgba(0,224,150,0.05)); border: 1px solid #00e096; }
.verdict-title { font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.verdict-sub { color: #aab4c4; font-size: 14px; }

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
""", unsafe_allow_html=True)

# ---------- KNOWLEDGE BASES ----------
LITERACY_KB = """
- A loan's "interest rate" is the extra cost of borrowing money, shown yearly (APR).
- "Compound interest" means earning/owing interest on top of interest already added.
- An emergency fund should ideally cover 3-6 months of essential expenses.
- Before taking a loan, check: interest rate, total repayment, monthly installment, hidden fees.
- Diversifying savings reduces risk.
- A "budget" means planning income against expenses so you spend less than you earn.
- Credit scores affect loan approval and rates; paying bills on time improves it.
- Investment "returns" are never guaranteed — higher promised returns mean higher risk.
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

# ---------- LLM CALLS ----------
def get_advisor_answer(question):
    system = f"""You are FinTrust AI's financial literacy advisor. Explain financial questions in simple,
warm, plain language for someone with little financial background. Ground your answer in this knowledge:
{LITERACY_KB}
Keep it concise (4-6 sentences), practical, and end with one clear actionable takeaway."""
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": question}],
        temperature=0.4,
    )
    return resp.choices[0].message.content

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
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": message_text}],
        temperature=0.2,
    )
    raw = resp.choices[0].message.content.strip()
    raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(raw)

# ---------- HERO ----------
st.markdown("""
<div class="hero">
    <div class="hero-badge">🛡️ AI AGENT · FINTECH · HACKATHON MVP</div>
    <h1>FinTrust AI</h1>
    <p>Your AI guardian for financial trust — plain-language guidance on money decisions, and real-time scam detection with visible reasoning.</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["💬  Ask a Financial Question", "🔍  Check a Suspicious Message"])

# ---------- TAB 1: ADVISOR ----------
with tab1:
    st.markdown('<div class="mode-card"><div class="mode-card-inner">', unsafe_allow_html=True)
    st.markdown("##### Get a simple, honest answer")
    st.caption("Ask about loans, saving, budgeting, or any money decision — explained in plain language.")

    example_cols = st.columns(2)
    example_q = None
    with example_cols[0]:
        if st.button("💡 Should I take a loan at 22% interest?", use_container_width=True):
            example_q = "I'm being offered a loan with 22% interest to buy a phone. Should I take it?"
    with example_cols[1]:
        if st.button("💰 How do I start saving with a small salary?", use_container_width=True):
            example_q = "I earn very little each month. How do I start saving?"

    question = st.text_area("Your question:", value=example_q or "", height=90, placeholder="e.g. Is compound interest good or bad for me?")

    if st.button("🧭 Get Advice", type="primary", use_container_width=True):
        if not client:
            st.error("Add your Groq API key first.")
        elif not question.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("Thinking through your question..."):
                try:
                    answer = get_advisor_answer(question)
                    st.markdown(f'<div class="advisor-answer">{answer}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Something went wrong: {e}")

    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- TAB 2: SCAM CHECKER ----------
with tab2:
    st.markdown('<div class="mode-card"><div class="mode-card-inner">', unsafe_allow_html=True)
    st.markdown("##### Paste a message — watch the agent investigate")
    st.caption("The agent checks 8 known fraud patterns step-by-step, then gives a verdict.")

    if st.button("🚩 Try example scam message", use_container_width=True):
        st.session_state["scam_input"] = "URGENT: Your bank account will be suspended in 1 hour. Reply with your OTP code immediately to verify your account and avoid suspension."

    msg = st.text_area("Paste the message here:", key="scam_input", height=100,
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
                    rows_html += f'<div class="check-row"><span class="check-icon">{icon}</span> {desc}</div>'
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

st.markdown('<div class="footer-note">Built for a hackathon 🚀 &nbsp;|&nbsp; Powered by Groq + Llama 3.3 &nbsp;|&nbsp; Team Fintellect</div>', unsafe_allow_html=True)
