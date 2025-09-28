# app.py
import os
from pathlib import Path
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# === Import Agents & Utils ===
from agents.intent_agent import detect_service_intent
from agents.question_agent import get_questions_for_service
from agents.eligibility_agent import evaluate_service_eligibility
from utils.translator import get_openai_client, explain_in_english, translate_to_urdu
from utils.pdf_filler import generate_application_pdf
from utils.vectorstore import search_policy

# ---------- Setup ----------
APP_ROOT = Path(__file__).parent
FORMS_DIR = APP_ROOT / "forms"
FORMS_DIR.mkdir(exist_ok=True, parents=True)

load_dotenv(APP_ROOT / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# ---------- Streamlit Page ----------
st.set_page_config(page_title="Citizen Service Navigator", page_icon="🧭", layout="wide")
st.title("🧭 Citizen Service Navigator – AI Multi-Agent Demo")

# ---------- Sidebar Settings ----------
st.sidebar.header("⚙️ Settings")
degraded_mode = st.sidebar.toggle("Degraded Mode (offline/low-cost)", value=False)
api_available = bool(OPENAI_API_KEY)
st.sidebar.write(f"🔑 OpenAI API: {'✅ Available' if api_available else '❌ Missing'}")
openai_client = get_openai_client(OPENAI_API_KEY) if (api_available and not degraded_mode) else None

# ---------- Initialise Session State ----------
for key, default in {
    "service_key": None,
    "analysis_done": False,
    "policy_results": [],
    "form_submitted": False,
    "answers": {},
}.items():
    st.session_state.setdefault(key, default)

# ---------- Step 1: Collect User Query ----------
st.markdown("### 1️⃣ Describe your issue")
user_text = st.text_area(
    "Write your situation (English or Urdu):",
    placeholder="e.g., My father is 65 and lives in Lahore. Can he get a free transport card?",
    height=120,
    key="user_query",
)

if st.button("🔍 Analyze Request", key="analyze_button"):
    if not user_text.strip():
        st.warning("⚠️ Please enter your situation first.")
        st.stop()

    # 🔍 Step 1: Intent Detection
    service_key, confidence, rationale = detect_service_intent(user_text, openai_client=openai_client)
    if not service_key:
        st.error("⚠️ Sorry, this service is not yet supported. We are working on adding it soon.")
        st.stop()

    # Store in session state
    st.session_state.service_key = service_key
    st.session_state.analysis_done = True
    st.session_state.confidence = confidence
    st.session_state.rationale = rationale

    # 🔍 Step 2: Retrieve Policy Sections
    st.session_state.policy_results = search_policy(user_text, k=3)

# ---------- Step 2: Show Detected Service + Policy ----------
if st.session_state.analysis_done and st.session_state.service_key:
    service_key = st.session_state.service_key
    st.success(f"✅ Detected Service: **{service_key}** (confidence: {st.session_state.confidence}%)")

    with st.expander("🤖 AI Understanding of Your Query"):
        st.write(st.session_state.rationale or "N/A")

    # 📜 Relevant Policy Sections
    if st.session_state.policy_results:
        st.markdown("### 📜 Relevant Policy Sections from Official Documents")
        for idx, section in enumerate(st.session_state.policy_results, 1):
            with st.expander(f"📑 Policy Section {idx}"):
                st.write(section)

    # ---------- Step 3: Dynamic Form ----------
    st.markdown("### 2️⃣ Provide Required Information")
    questions = get_questions_for_service(service_key)

    with st.form(key=f"dynamic_form_{service_key}", clear_on_submit=False):
        answers = {}
        for q in questions:
            ftype = q.get("type", "text")
            key = q["key"]
            label = q["label"]
            help_text = q.get("help", "")
            default = q.get("default", "")

            if ftype == "number":
                answers[key] = st.number_input(label, min_value=0, value=int(default or 0), step=1, help=help_text)
            elif ftype == "select":
                options = q.get("options", ["No", "Yes"])
                answers[key] = st.selectbox(label, options, help=help_text)
            else:
                answers[key] = st.text_input(label, value=str(default), help=help_text)

        submitted = st.form_submit_button("✅ Check Eligibility")

    if submitted:
        st.session_state.answers = answers
        st.session_state.form_submitted = True

# ---------- Step 4: Eligibility Decision ----------
if st.session_state.get("form_submitted", False):
    service_key = st.session_state.service_key
    answers = st.session_state.answers
    policy_context = "\n\n".join(st.session_state.policy_results) if st.session_state.policy_results else ""

    st.markdown("### 3️⃣ Eligibility Result")

    eligible, reasons, required_docs = evaluate_service_eligibility(
        service_key=service_key, 
        form_data=answers, 
        policy_context=policy_context
    )

    if eligible:
        st.success("🎉 You are **Eligible** for this service!")
    else:
        st.error("❌ You are **Not Eligible** based on the information provided.")

    # ✅ English Explanation (Safe + Always Shows)
    english_exp = explain_in_english(
        client=openai_client,
        service_key=service_key,
        form_data=answers,
        eligible=eligible,
        reasons=reasons,
        required_docs=required_docs,
        degraded=degraded_mode,
    )

    if not english_exp or len(english_exp.strip()) < 5:
        english_exp = (
            "✅ Eligibility check complete.\n\n"
            + "Reason(s): " + "; ".join(reasons if reasons else ["No reasons provided."]) + "\n\n"
            + "📜 Policy Reference: Based on available documents.\n\n"
            + ("📁 Required documents: " + ", ".join(required_docs) if required_docs else "")
        )

    st.subheader("📜 Explanation (English)")
    st.markdown(english_exp)

    # ✅ Urdu Translation (Safe Fallback)
    urdu_exp = translate_to_urdu(
        client=openai_client,
        english_text=english_exp,
        degraded=degraded_mode
    )
    st.subheader("📜 تشریح (Urdu)")
    st.write(urdu_exp)

    # ✅ Required Documents Section
    st.subheader("📁 Required Documents")
    if required_docs:
        st.write("\n".join([f"• {d}" for d in required_docs]))
    else:
        st.write("• None required.")

    # ---------- Step 5: PDF Generation ----------
    if eligible:
        st.markdown("### 4️⃣ Generate Application PDF")
        pdf_name = f"{service_key}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
        pdf_path = FORMS_DIR / pdf_name

        generate_application_pdf(
            service_key=service_key,
            form_data=answers,
            eligibility=eligible,
            reasons=reasons,
            explanation_en=english_exp,
            required_docs=required_docs,
            file_path=pdf_path,
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Application PDF",
                data=f.read(),
                file_name=pdf_name,
                mime="application/pdf",
            )

# ---------- Reset Button ----------
st.markdown("---")
st.markdown("### 🔄 Start a New Request")

if st.button("🔄 Reset and Start Over", key="reset_btn"):
    st.session_state.clear()
    st.rerun()
