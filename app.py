import streamlit as st
import json
import pdfplumber
from groq import Groq

# 1. Page Configuration Setup (Mandatory first Streamlit command)
st.set_page_config(
    page_title="CareerBridge AI",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# 2. Modern UI Dark Theme Custom CSS Setup
st.markdown("""
<style>
@import url('https://googleapis.com');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0a0a0f; color: #e8e8f0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 4rem 2rem; max-width: 1400px; }
.hero-wrap { padding: 3.5rem 0 2.5rem 0; border-bottom: 1px solid #1e1e2e; margin-bottom: 2.5rem; }
.hero-eyebrow { display: inline-block; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: #7c6af7; background: rgba(124, 106, 247, 0.12); border: 1px solid rgba(124, 106, 247, 0.25); padding: 4px 12px; border-radius: 20px; margin-bottom: 1rem; }
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: 2.8rem; font-weight: 700; color: #f0f0fa; line-height: 1.15; margin: 0 0 0.75rem 0; }
.hero-title span { background: linear-gradient(135deg, #7c6af7 0%, #a78bfa 50%, #60d4f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1rem; color: #8888a8; max-width: 700px; margin: 0; }
.panel { background: #12121e; border: 1px solid #1e1e30; border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem; }
.panel-title { font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 600; color: #d0d0e8; margin-bottom: 0.5rem; }
.score-card { background: linear-gradient(145deg, #14142a 0%, #1a1030 100%); border: 1px solid #2e2060; border-radius: 16px; padding: 2rem 1.5rem; text-align: center; }
.score-number { font-family: 'Space Grotesk', sans-serif; font-size: 4rem; font-weight: 700; color: #60d4f7; }
.gap-pill { display: inline-block; background: rgba(248, 113, 113, 0.1); border: 1px solid rgba(248, 113, 113, 0.25); color: #f87171; font-size: 0.78rem; font-weight: 500; padding: 4px 12px; border-radius: 20px; margin: 4px 4px 4px 0; }
.outreach-box { background: #0d0d18; border: 1px solid #2a2a40; border-radius: 10px; padding: 1.2rem; font-size: 0.875rem; color: #b0b0cc; line-height: 1.7; white-space: pre-wrap; }
</style>
""", unsafe_allow_html=True)

# 3. Render Dashboard Hero Section
st.markdown("""
<div class=\"hero-wrap\">
    <div class=\"hero-eyebrow\">✨ Career and Portfolio Optimization</div>
    <h1 class=\"hero-title\">Transform industry skill demands<br><span>into an actionable blueprint for interview success.</span></h1>
    <p class=\"hero-sub\">A diagnostic utility tool for job seekers. Upload your credentials and any target job specification to evaluate compatibility metrics, pinpoint exact skill gaps, receive a custom portfolio build strategy to resolve those deficiencies, and get tailored professional outreach templates.</p>
</div>
""", unsafe_allow_html=True)

# 4. Handle API Authentication Setup
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

if not api_key:
    st.info("⚠️ Please provide a GROQ_API_KEY inside your Secrets panel or Left Sidebar to run the pipeline.")
    st.stop()

client = Groq(api_key=api_key)

# 5. Interface Split Inputs Design Layout
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="panel"><p class="panel-title">Step 1: Upload Credentials</p></div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload your resume (PDF format)", type=["pdf"])
with col2:
    st.markdown('<div class="panel"><p class="panel-title">Step 2: Target Opportunity Parameters</p></div>', unsafe_allow_html=True)
    job_title = st.text_input("Target Job Position", placeholder="e.g., Junior Data Analyst")
    job_desc = st.text_area("Job Requirements Text Copy", placeholder="Paste the target job brief data metrics here...", height=150)

st.markdown("<br>", unsafe_allow_html=True)
submit_action = st.button("Execute Intelligence Pipeline", type="primary")

# 6. Deep Analytics Match Calculation Logic Layer Execution
if submit_action:
    if not uploaded_file or not job_desc or not job_title:
        st.error("❌ Action Interrupted: Please confirm you've loaded a PDF and filled out all job input details.")
        st.stop()

    with st.spinner("Compiling Semantic Verification Matrices via Groq..."):
        extracted_text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text = extracted_text + text + "\n"

        system_prompt = f"""
        Analyze this student CV text against this targeted job description requirement.
        You must respond with ONLY a valid JSON object. Do not include markdown formatting code wrappers or backticks.

        Expected JSON response structure layout exactly:
        {{
          "match_score": 85,
          "detected_gaps": ["skill1", "skill2"],
          "suggested_project_title": "String title",
          "project_blueprint": "Short layout description of a weekend portfolio proof project",
          "interview_questions": ["Question 1", "Question 2"],
          "outreach_template": "A personalized LinkedIn connection message"
        }}

        Candidate CV Text:
        {extracted_text}

        Target Job: {job_title}
        Job Description: {job_desc}
        """

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        raw_output = ""
        data = None

        try:
            # FIX 1: Accessing the corrected choices[0] array index for Groq SDK
            raw_output = completion.choices[0].message.content.strip()
            
            # FIX 2: Dynamic JSON Boundary Finder 
            start_index = raw_output.find("{")
            end_index = raw_output.rfind("}") + 1
            
            if start_index == -1 or end_index == 0:
                raise ValueError("The AI model response failed to structure a valid JSON brace envelope matrix.")
                
            clean_json_string = raw_output[start_index:end_index]
            data = json.loads(clean_json_string)
            
        except json.JSONDecodeError:
            st.error("❌ Extraction Format Mismatch: Groq generated unexpected text elements. Please execute the pipeline again.")
            st.stop()
        except ValueError as ve:
            st.error(f"❌ Syntax Error: {ve}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Internal Processing Loop Crash: {e}")
            st.stop()

    # 7. Split Screen Render Output Layout (Sits cleanly outside the spinner container)
    if data is not None:
        st.markdown("<hr style='border-top:1px solid #1e1e2e; margin:2rem 0;'>", unsafe_allow_html=True)
        res_col1, res_col2 = st.columns(2)

        with res_col1:
            match_score = data.get('match_score', 'N/A')
            st.markdown(f"""
            <div class="score-card">
                <div style="font-size:0.75rem; letter-spacing:0.1em; text-transform:uppercase; color:#7c6af7; margin-bottom:0.5rem;">Match Core Score</div>
                <div class="score-number">{match_score}%</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br><h5>Identified Gaps</h5>", unsafe_allow_html=True)
            for gap in data.get("detected_gaps", []):
                st.markdown(f'<span class="gap-pill">⚠️ {gap}</span>', unsafe_allow_html=True)

        with res_col2:
            st.subheader(f"🛠️ Portfolio Build: {data.get('suggested_project_title', 'Portfolio Project')}")
            st.info(data.get('project_blueprint', 'No description layout parsed.'))
            
            st.subheader("💡 Mock Interview Questions")
            for q in data.get("interview_questions", []):
                st.write(f"• *{q}*")
                
            st.subheader("✉️ Targeted Outreach Template")
            outreach_text = data.get("outreach_template", "")
            st.markdown(f'<div class="outreach-box">{outreach_text}</div>', unsafe_allow_html=True)
