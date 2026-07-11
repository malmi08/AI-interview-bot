import streamlit as st
import pypdf
from interview_engine import handle_interview_chat

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="NEUROCORE_AI - Interview Portal", layout="wide", page_icon="🧠")

# --- 2. CSS STYLING ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top right, #1a0b2e 0%, #050208 60%);
        color: white;
    }
    
    /* Navigation Bar */
    .nav-bar {
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 20px 50px; 
        background: rgba(13, 15, 20, 0.7);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05); 
        margin-bottom: 40px; 
    }
    
    .nav-logo { 
        font-weight: 800; 
        font-size: 22px; 
        background: linear-gradient(45deg, #b5179e, #7209b7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: 1px; 
    }
    .stApp {
        background-color: #0d0e15;
        color: #ffffff;
    }
    
    /* Hero Section */
    
    .hero-section { 
        text-align: center; 
        margin-bottom: 40px; 
    }
    .hero-title { 
        font-size: 42px; 
        font-weight: 800; 
        color: #ffffff; 
        margin-bottom: 12px; 
        line-height: 1.2;
    }
    .hero-subtitle { 
        color: #a0a0a5; 
        font-size: 16px; 
        max-width: 600px; 
        margin: 0 auto; 
    }
    
   
    .stImage img {
        max-width: 50% !important;  
        height: auto !important;
        max-height: 200px !important; 
        margin: 0 auto;
        display: block;
        object-fit: contain;
    }
    
    
    /* Registration Card */
    
    .registration-card {
        background: rgba(157, 78, 221, 0.06); 
        padding: 15px 25px; 
        border-radius: 16px; 
        border: 1px solid rgba(157, 78, 221, 0.3); 
        max-width: 450px; 
        margin: 20px auto;
        text-align: center;
        box-shadow: 0 0 30px rgba(157, 78, 221, 0.1);
    }
    .card-text {
        font-size: 16px;
        font-weight: 600;
        color: #e0aaff;
        margin: 0;
    }
    label { 
        color: #b5b5c0 !important; 
        font-weight: 600; 
        font-size: 13px !important; 
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div > div {
        background-color: rgba(22, 22, 26, 0.8) !important; 
        border: 1px solid #333339 !important; 
        color: white !important; 
        border-radius: 10px !important;
        padding: 4px 10px !important;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #9d4edd 0%, #7b2cbf 100%) !important; 
        color: white !important; 
        width: 100%; 
        border: none; 
        padding: 14px; 
        border-radius: 12px; 
        font-weight: 700; 
        font-size: 16px; 
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
        box-shadow: 0 8px 20px rgba(157, 78, 221, 0.3);
    }
    
   div.stButton > button:hover { 
        background: linear-gradient(135deg, #7b2cbf 0%, #5a189a 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 12px 24px rgba(157, 78, 221, 0.4);
    }
    
   /* Assessment Report */
    .report-header { 
        background: linear-gradient(135deg, #240046 0%, #5a189a 100%); 
        padding: 25px; 
        border-radius: 15px; 
        text-align: center; 
    }
    /* Assessment Report */
    .report-header {
        background: linear-gradient(135deg, #240046 0%, #5a189a 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
    }

    /* --- NEW CHAT BUBBLE STYLING --- */
    /* AI Message Bubble (Dark Grey) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background-color: #16161a !important;
        border: 1px solid #333339 !important;
        border-radius: 15px !important;
        padding: 10px 20px !important;
        margin-bottom: 20px;
    }
    /* User Message Bubble (Dark Purple) */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background-color: #26143c !important; 
        border: 1px solid #5a189a !important;
        border-radius: 15px !important;
        padding: 10px 20px !important;
        margin-bottom: 20px;
    }
    /* Chat Input Bar Styling */
    .stChatFloatingInputContainer {
        background-color: transparent !important;
    }
</style>
    

""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "messages" not in st.session_state: st.session_state.messages = []
if "history_text" not in st.session_state: st.session_state.history_text = ""
if "report_ready" not in st.session_state: st.session_state.report_ready = ""


if st.session_state.logged_in and "role" in st.session_state:
    # Dashboard  Nav Bar 
    st.markdown(f"""
        <div class="nav-bar" style="display: flex; align-items: center; justify-content: flex-start; gap: 15px;">
            <div class="nav-logo">InterviewNode</div>
            <div style="color: #666; font-size: 18px; line-height: 1;">|</div>
            <div style="color: #e0aaff; font-size: 16px; font-weight: 500; line-height: 1;">Interviewing for: {st.session_state.role}</div>
        </div>
    """, unsafe_allow_html=True)
else:
    
    st.markdown("""
        <div class="nav-bar">
            <div class="nav-logo">InterviewNode</div>
        </div>
    """, unsafe_allow_html=True)
# --- 5. APP FLOW ---
if not st.session_state.logged_in:
   # --- HERO SECTION ---
# --- HERO SECTION & ANIMATION ---
    col1, col2 = st.columns([1.7, 1.3])

    with col1:
        st.markdown("""
            <div class="hero-section">
                <div class="hero-title">Welcome to Our <span style="color: #9d4edd;">IT Interview Portal</span></div>
                
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="text-align: center; margin-top: -20px;">', unsafe_allow_html=True)
        st.image("robot.gif", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- REGISTRATION FORM ---
    st.markdown('<div class="registration-card" style="margin-top: -35px;"><p class="card-text">Unlock Your Potential with AI-Driven Interviews</p>', unsafe_allow_html=True)
    st.subheader("Launch Interview Session")
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("FULL NAME", placeholder="e.g. Nimasha")
        experience = st.selectbox("EXPERIENCE LEVEL", ["Intern", "Junior", "Mid-Level", "Senior"])
    with col2:
        target_role = st.text_input("TARGET ROLE", placeholder="e.g. Data Science")
       
    
    uploaded_file = st.file_uploader("RESUME ATTACHMENT", type=["pdf", "txt"])
    
    if st.button("START INTERVIEW"):
        if full_name and target_role and uploaded_file:
            extracted_text = ""
            if uploaded_file.name.endswith(".pdf"):
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages: extracted_text += page.extract_text() + "\n"
            else: extracted_text = uploaded_file.read().decode("utf-8")
            
            st.session_state.name = full_name
            st.session_state.role = target_role
            st.session_state.resume_text = extracted_text
            st.session_state.logged_in = True
            
            first_reply = handle_interview_chat(f"Start interview for {target_role}", "", extracted_text, user_name=full_name)
            st.session_state.messages.append({"role": "assistant", "content": first_reply})
            st.rerun()
        else:
            st.warning("Please fill all fields.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- INTERVIEW DASHBOARD ---
    
    
    with st.sidebar:
        st.markdown("### 🤖 Interview AI\n**Active**")
        st.write("") 
        
        # Generate Report / End Interview button
        if st.button("Generate Report"):
            with st.spinner("Generating Report..."):
                report = handle_interview_chat("exit", st.session_state.history_text, st.session_state.resume_text)
                st.session_state.report_ready = report
            st.rerun()
            
        st.write("---") 
        
        # New Interview button
        if st.button("➕ New Interview"):
            st.session_state.clear()
            st.rerun()

    
    
    # Reort view
    if st.session_state.report_ready:
        st.markdown('<div class="report-header"><h2> ASSESSMENT REPORT</h2></div>', unsafe_allow_html=True)
        st.write(st.session_state.report_ready)
        
    # Chat Interface 
    else:
        # chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): 
                st.write(msg["content"])
        
        # Get User input 
        if prompt := st.chat_input("Your answer..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.spinner("Analyzing..."):
                bot_reply = handle_interview_chat(prompt, st.session_state.history_text, st.session_state.resume_text)
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                st.session_state.history_text += f"\nStudent: {prompt}\nInterviewer: {bot_reply}"
                
            st.rerun()