# app.py (EasyWorksheet Pro Max - Thai Version with Full IPST Curriculum)
import streamlit as st
import os
import sys
from PIL import Image
import google.generativeai as genai

# Config path for local files
EXPORT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the current directory to path so we can import backend
sys.path.append(EXPORT_DIR)
from backend import WorksheetGenerator

# Initialize Generator
try:
    api_key = st.secrets.get("GEMINI_API_KEY", None)
except:
    api_key = None

# Session State for API Key and Provider
if "api_key" not in st.session_state:
    st.session_state.api_key = api_key
if "api_provider" not in st.session_state:
    st.session_state.api_provider = "Google Gemini"  # Default provider

# Session state for generated content (persist download buttons)
if "generated_pdf" not in st.session_state:
    st.session_state.generated_pdf = None
if "generated_word" not in st.session_state:
    st.session_state.generated_word = None
if "generated_filename" not in st.session_state:
    st.session_state.generated_filename = "worksheet"

generator = WorksheetGenerator(ai_api_key=st.session_state.api_key, provider=st.session_state.api_provider)

st.set_page_config(page_title="เนเธเธฃเนเธเธฃเธกเธชเธฃเนเธฒเธเนเธเธเธฒเธ EasyWorksheet", page_icon="๐€", layout="wide")

st.title("๐€ เนเธเธฃเนเธเธฃเธกเธชเธฃเนเธฒเธเนเธเธเธฒเธ EasyWorksheet")
st.caption("เธฃเธฐเธเธเธชเธฃเนเธฒเธเนเธเธเธฒเธเธญเธฑเธ•เนเธเธกเธฑเธ•เธดเธ”เนเธงเธข AI เธชเธณเธซเธฃเธฑเธเธเธธเธ“เธเธฃเธนเธขเธธเธเนเธซเธกเน (Created by Nong Aom & P'Em)")

# --- API Key Section (Always Visible) ---
with st.expander("๐”‘ เธ•เธฑเนเธเธเนเธฒ API Key", expanded=not st.session_state.api_key):
    # Provider Selection Dropdown
    provider_options = ["Google Gemini", "Groq", "OpenRouter"]
    selected_provider = st.selectbox(
        "๐”ฝ เน€เธฅเธทเธญเธเธเธนเนเนเธซเนเธเธฃเธดเธเธฒเธฃ AI:",
        options=provider_options,
        index=provider_options.index(st.session_state.api_provider) if st.session_state.api_provider in provider_options else 0
    )
    
    # Store selected provider in session state
    if selected_provider != st.session_state.api_provider:
        st.session_state.api_provider = selected_provider
        # Clear API key when switching providers
        st.session_state.api_key = None
        st.rerun()
    
    if not st.session_state.api_key:
        # Conditional API key input based on selected provider
        if selected_provider == "Google Gemini":
            api_input = st.text_input("๐”‘ เนเธชเน Google Gemini API Key", type="password", placeholder="AIza...")
            st.markdown("[๐‘ เธเธ”เธ—เธตเนเธเธตเนเน€เธเธทเนเธญเธเธญเธฃเธฑเธ API Key เธเธฃเธต (Google AI Studio)](https://aistudio.google.com/app/apikey)")
        elif selected_provider == "Groq":
            api_input = st.text_input("๐”‘ เนเธชเน Groq API Key", type="password", placeholder="gsk_...")
            st.markdown("[๐‘ เธเธ”เธ—เธตเนเธเธตเนเน€เธเธทเนเธญเธเธญเธฃเธฑเธ API Key (Groq Console)](https://console.groq.com)")
        elif selected_provider == "OpenRouter":
            api_input = st.text_input("๐”‘ เนเธชเน OpenRouter API Key", type="password", placeholder="sk-or-v1-...")
            st.markdown("[๐‘ เธเธ”เธ—เธตเนเธเธตเนเน€เธเธทเนเธญเธเธญเธฃเธฑเธ API Key (OpenRouter)](https://openrouter.ai)")
        
        if api_input:
            clean_key = api_input.strip()
            try:
                # Configure and test based on provider
                if selected_provider == "Google Gemini":
                    genai.configure(api_key=clean_key)
                    list(genai.list_models())  # Test call
                # For Groq and OpenRouter, we'll test through the generator
                
                st.session_state.api_key = clean_key
                st.session_state.api_provider = selected_provider
                st.success(f"โ… เน€เธเธทเนเธญเธกเธ•เนเธญเธเธฑเธ {selected_provider} เธชเธณเน€เธฃเนเธ!")
                st.rerun()
            except Exception as e:
                st.error(f"โ API Key เนเธกเนเธ–เธนเธเธ•เนเธญเธ: {e}")
    else:
        st.success(f"โ… เน€เธเธทเนเธญเธกเธ•เนเธญเธเธฑเธ {st.session_state.api_provider} เนเธฅเนเธง")
        if st.button("๐—‘๏ธ เธฅเธ API Key"):
            st.session_state.api_key = None
            st.session_state.api_provider = "Google Gemini"  # Reset to default
            st.rerun()

# Re-init generator if key is present (cache in session state)
if "generator" not in st.session_state:
    st.session_state.generator = None

if st.session_state.api_key:
    # Only create new generator if key or provider changed
    if (st.session_state.generator is None or 
        st.session_state.generator.ai_api_key != st.session_state.api_key or
        st.session_state.generator.provider != st.session_state.api_provider):
        st.session_state.generator = WorksheetGenerator(
            ai_api_key=st.session_state.api_key, 
            provider=st.session_state.api_provider
        )

# Use cached generator
generator = st.session_state.generator

# --- Settings Sidebar ---
with st.sidebar:
    st.header("โ๏ธ เนเธเธเธเธงเธเธเธธเธก (Control Panel)")
    
    school_name = st.text_input("๐ซ เธเธทเนเธญเนเธฃเธเน€เธฃเธตเธขเธ / เธเธทเนเธญเธเธธเธ“เธเธฃเธน", "เนเธฃเธเน€เธฃเธตเธขเธเธ•เธฑเธงเธญเธขเนเธฒเธ")
    
    uploaded_logo = st.file_uploader("๐–ผ๏ธ เธญเธฑเธเนเธซเธฅเธ”เนเธฅเนเธเนเนเธฃเธเน€เธฃเธตเธขเธ (เธ–เนเธฒเธกเธต)", type=["png", "jpg", "jpeg"])
    
    st.markdown("---")
    
    # Mode Selection (Thai)
    mode_options = [
        "๐งช เธ—เธ”เธชเธญเธ AI (Test AI)",
        "๐“ เธเธถเธเธ—เธฑเธเธฉเธฐเธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน (Math)",
        "๐”ฌ เธงเธดเธ—เธขเธฒเธจเธฒเธชเธ•เธฃเน (Science)",
        "๐“ เธ เธฒเธฉเธฒเนเธ—เธข (Thai Language)",
        "๐ เธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉ (English Language)",
        "๐“– เธชเธฑเธเธเธกเธจเธถเธเธฉเธฒ (Social Studies)",
        "๐ค– เนเธเธ—เธขเนเธเธฑเธเธซเธฒ AI (Word Problems)",
        "๐” เธเธฃเธดเธจเธเธฒเธซเธฒเธเธณเธจเธฑเธเธ—เน (Word Search)",
        "โ๏ธ เธเธถเธเธเธฑเธ”เธฅเธฒเธขเธกเธทเธญ (Handwriting)",
        "๐“ เธชเธฃเนเธฒเธเธเนเธญเธชเธญเธเธเธฒเธเนเธเธฅเน (File to Quiz)"
    ]
    mode_select = st.selectbox("เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เนเธเธเธฒเธ:", mode_options)
    
    title = st.text_input("เธซเธฑเธงเธเนเธญเนเธเธเธฒเธ", "เนเธเธเธเธถเธเธซเธฑเธ”เธ—เธตเน 1")
    
    include_qr = st.checkbox("เน€เธเธดเนเธก QR Code เน€เธเธฅเธข?", value=True)
    qr_url = st.text_input("เธฅเธดเธเธเนเน€เธเธฅเธข (เน€เธเนเธ Google Drive)", "https://example.com/answers") if include_qr else None

# --- API Check Function ---
def check_api_required():
    """Check if API key is required for current selection"""
    if st.session_state.api_key:
        return False  # API is available
    
    # List of modes/topics that require API
    ai_required_modes = [
        "เนเธเธ—เธขเนเธเธฑเธเธซเธฒ AI",
        "เธชเธฃเนเธฒเธเธเนเธญเธชเธญเธเธเธฒเธเนเธเธฅเน"
    ]
    
    # Check mode first
    for mode in ai_required_modes:
        if mode in mode_select:
            return True
    
    # Check if topic requires AI
    if "๐" in mode_select:
        return True
    
    return False

def show_api_warning():
    """Show yellow warning popup for missing or non-working API"""
    provider_name = st.session_state.api_provider if st.session_state.api_provider else "AI"
    st.warning(f"โ ๏ธ **เธ•เนเธญเธเนเธเน {provider_name} API Key** เธชเธณเธซเธฃเธฑเธเธเธตเน€เธเธญเธฃเนเธเธตเนเธเนเธฐ!", icon="๐”‘")
    st.info("๐“ เธเธฃเธญเธ API Key เนเธ”เนเธ—เธตเนเธ”เนเธฒเธเธเธเธเธญเธเธซเธเนเธฒเธเธญเธเธตเนเน€เธฅเธขเธเนเธฐ")
    
    # Show appropriate link based on provider
    if st.session_state.api_provider == "Google Gemini":
        st.markdown("[๐‘ เธเธญ API Key เธเธฃเธตเธ—เธตเนเธเธตเน (Google AI Studio)](https://aistudio.google.com/app/apikey)")
    elif st.session_state.api_provider == "Groq":
        st.markdown("[๐‘ เธเธญ API Key เธ—เธตเนเธเธตเน (Groq Console)](https://console.groq.com)")
    elif st.session_state.api_provider == "OpenRouter":
        st.markdown("[๐‘ เธเธญ API Key เธ—เธตเนเธเธตเน (OpenRouter)](https://openrouter.ai)")

def check_ai_and_generate(generator, generate_func, *args, **kwargs):
    """Check if AI is working, if not use template generation"""
    if generator.is_ai_working():
        # AI is working, use AI generation
        return generate_func(*args, **kwargs)
    else:
        # AI not working, show warning and use fallback
        st.warning("โ ๏ธ **AI เนเธกเนเธ—เธณเธเธฒเธ เธเธณเธฅเธฑเธเนเธเนเนเธเธเธ•เธฑเธงเธญเธขเนเธฒเธเนเธ—เธเธเนเธฐ**")
        st.info("๐’ก เธซเธฒเธเธ•เนเธญเธเธเธฒเธฃเนเธเน AI เธเธฃเธธเธ“เธฒเธ•เธฃเธงเธเธชเธญเธ API Key เธ—เธตเนเธ”เนเธฒเธเธเธเธเธฐเธเธฐ")
        return None  # Will be handled by caller

# --- Main Content Area ---

if "เธ—เธ”เธชเธญเธ AI" in mode_select:
    st.subheader("๐งช เธ—เธ”เธชเธญเธเธเธฒเธฃเน€เธเธทเนเธญเธกเธ•เนเธญ AI เนเธฅเธฐ Prompt")
    
    # Check AI connection
    if not st.session_state.api_key:
        st.warning("โ ๏ธ เธเธฃเธธเธ“เธฒเนเธชเน API Key เธ—เธตเนเธ”เนเธฒเธเธเธเธเนเธญเธเธเธฐเธเธฐ!")
    else:
        # Initialize generator to test
        test_generator = WorksheetGenerator(
            ai_api_key=st.session_state.api_key, 
            provider=st.session_state.api_provider
        )
        
        # Connection Status
        st.markdown("### ๐” เธชเธ–เธฒเธเธฐเธเธฒเธฃเน€เธเธทเนเธญเธกเธ•เนเธญ")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Provider:** {st.session_state.api_provider}")
        
        with col2:
            if test_generator.is_ai_working():
                st.success("**Status:** โ… เน€เธเธทเนเธญเธกเธ•เนเธญเธชเธณเน€เธฃเนเธ!")
            else:
                st.error("**Status:** โ เนเธกเนเธชเธฒเธกเธฒเธฃเธ–เน€เธเธทเนเธญเธกเธ•เนเธญเนเธ”เน")
        
        with col3:
            if test_generator.ai and hasattr(test_generator.ai, 'model_name'):
                st.info(f"**Model:** {test_generator.ai.model_name}")
        
        st.markdown("---")
        
        # Custom Prompt Section
        st.markdown("### ๐ค– เธ—เธ”เธชเธญเธ Prompt เธเธฑเธ AI")
        
        # Pre-made prompt templates
        prompt_templates = {
            "เธ—เธฑเนเธงเนเธ": "เธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน 5 เธเนเธญ เน€เธฃเธทเนเธญเธเธเธฒเธฃเธเธงเธเธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธเธเธฃเธฐเธ–เธก",
            "เธเธ“เธดเธ•": "เธชเธฃเนเธฒเธเนเธเธ—เธขเนเธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน 3 เธเนเธญ เน€เธฃเธทเนเธญเธเธเธฒเธฃเธเธนเธ“ เธชเธณเธซเธฃเธฑเธ เธ.3",
            "เธงเธดเธ—เธขเน": "เธชเธฃเนเธฒเธเธเธณเธ–เธฒเธกเธงเธดเธ—เธขเธฒเธจเธฒเธชเธ•เธฃเน 5 เธเนเธญ เน€เธฃเธทเนเธญเธเธฃเธฐเธเธเธฃเนเธฒเธเธเธฒเธขเธกเธเธธเธฉเธขเน",
            "เนเธ—เธข": "เธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธ เธฒเธฉเธฒเนเธ—เธข 5 เธเนเธญ เน€เธฃเธทเนเธญเธเธเธณเธเธฒเธก",
            "เธญเธฑเธเธเธคเธฉ": "เธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉ 5 เธเนเธญ เน€เธฃเธทเนเธญเธ Tenses",
        }
        
        template_choice = st.selectbox("๐“ เน€เธฅเธทเธญเธ Template:", list(prompt_templates.keys()), index=0)
        
        # Custom prompt input
        custom_prompt = st.text_area(
            "โ๏ธ Prompt เธเธญเธเธเธธเธ“ (เน€เธเธตเธขเธเน€เธญเธเนเธ”เน):",
            value=prompt_templates[template_choice],
            height=150
        )
        
        # Number of questions
        test_num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=5)
        
        # Test button
        if st.button("๐€ เธ—เธ”เธชเธญเธ AI", type="primary"):
            if not test_generator.is_ai_working():
                st.error("โ AI เนเธกเนเธ—เธณเธเธฒเธ! เธเธฃเธธเธ“เธฒเธ•เธฃเธงเธเธชเธญเธ API Key เธ—เธตเนเธ”เนเธฒเธเธเธเธเธฐเธเธฐ")
                st.info(f"๐’ก Provider เธ—เธตเนเนเธเน: {st.session_state.api_provider}")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธเธฃเธฐเธกเธงเธฅเธเธฅ..."):
                    try:
                        # Create a simple prompt for testing
                        test_prompt = f"""{custom_prompt}

เนเธซเนเธเธณเธ•เธญเธเนเธเธฃเธนเธเนเธเธเธเธตเน:
Questions:
1. [เธเธณเธ–เธฒเธกเธ—เธตเน 1]
2. [เธเธณเธ–เธฒเธกเธ—เธตเน 2]
...

Answers:
1. [เธเธณเธ•เธญเธเธ—เธตเน 1]
2. [เธเธณเธ•เธญเธเธ—เธตเน 2]
..."""
                        
                        result = test_generator.ai.generate(test_prompt)
                        
                        if result:
                            st.markdown("### โ… เธเธฅเธฅเธฑเธเธเนเธเธฒเธ AI")
                            st.markdown(result)
                            
                            # Parse and show in nice format
                            st.markdown("### ๐“ เธเธฅเธฅเธฑเธเธเนเนเธเธฃเธนเธเนเธเธเธ•เธฒเธฃเธฒเธ")
                            
                            # Try to parse the response
                            try:
                                parts = result.split("Answers:")
                                if len(parts) >= 2:
                                    questions = [q.strip() for q in parts[0].split("\n") if q.strip() and (q[0].isdigit() or q.startswith("-"))][-5:]
                                    answers = [a.strip() for a in parts[1].split("\n") if a.strip() and (a[0].isdigit() or a.startswith("-"))][-5:]
                                    
                                    if questions and answers:
                                        for i, (q, a) in enumerate(zip(questions, answers), 1):
                                            st.write(f"**{i}.** {q} โ’ {a}")
                            except:
                                st.info("๐“ (เธ”เธนเธเธฅเธฅเธฑเธเธเนเธ”เนเธฒเธเธเธเน€เธเนเธเธซเธฅเธฑเธ)")
                        else:
                            st.error("โ AI เนเธกเนเนเธ”เนเธชเนเธเธเธณเธ•เธญเธเธเธฅเธฑเธเธกเธฒ")
                            
                    except Exception as e:
                        st.error(f"โ เน€เธเธดเธ”เธเนเธญเธเธดเธ”เธเธฅเธฒเธ”: {e}")
        
        # Tips section
        st.markdown("---")
        st.markdown("""
        ### ๐’ก เน€เธเธฅเนเธ”เธฅเธฑเธเธเธฒเธฃเน€เธเธตเธขเธ Prompt เธ—เธตเนเธ”เธต
        
        1. **เธฃเธฐเธเธธเธงเธดเธเธฒ/เธซเธฑเธงเธเนเธญเธเธฑเธ”เน€เธเธ** เน€เธเนเธ "เธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน เน€เธฃเธทเนเธญเธเธเธฒเธฃเธเธงเธ"
        2. **เธฃเธฐเธเธธเธฃเธฐเธ”เธฑเธเธเธฑเนเธ** เน€เธเนเธ "เธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธ เธ.3"
        3. **เธฃเธฐเธเธธเธเธณเธเธงเธเธเนเธญ** เน€เธเนเธ "เธชเธฃเนเธฒเธ 5 เธเนเธญ"
        4. **เธฃเธฐเธเธธเธฃเธนเธเนเธเธเธเธณเธ•เธญเธ** เน€เธเนเธ "เนเธซเนเธเธณเธ•เธญเธเธเธฃเนเธญเธกเน€เธเธฅเธข"
        5. **เธฃเธฐเธเธธเธ เธฒเธฉเธฒ** เน€เธเนเธ "เธเธณเธ–เธฒเธกเน€เธเนเธเธ เธฒเธฉเธฒเนเธ—เธข"
        """)

if "เธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน" in mode_select:
    st.subheader("๐“ เธชเธฃเนเธฒเธเนเธเธเธฒเธเธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน (เธ•เธฒเธกเธซเธฅเธฑเธเธชเธนเธ•เธฃ เธชเธชเธงเธ—.)")
    
    # Grade Selection
    grade_options = ["เธ.1", "เธ.2", "เธ.3", "เธ.4", "เธ.5", "เธ.6", "เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]
    grade_select = st.selectbox("๐“ เน€เธฅเธทเธญเธเธฃเธฐเธ”เธฑเธเธเธฑเนเธ:", grade_options)
    
    # Full IPST Curriculum by Grade
    ipst_topics = {
        # ===== เธฃเธฐเธ”เธฑเธเธเธฃเธฐเธ–เธกเธจเธถเธเธฉเธฒ =====
        "เธ.1": [
            ("1๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธ 1 เธ–เธถเธ 5 เนเธฅเธฐ 0", "calculation"),
            ("2๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธ 6 เธ–เธถเธ 9", "calculation"),
            ("3๏ธโฃ", "เธเธฒเธฃเธเธงเธเธเธณเธเธงเธเธชเธญเธเธเธณเธเธงเธเธ—เธตเนเธเธฅเธเธงเธเนเธกเนเน€เธเธดเธ 9", "calculation"),
            ("4๏ธโฃ", "เธเธฒเธฃเธฅเธเธเธณเธเธงเธเธชเธญเธเธเธณเธเธงเธเธ—เธตเนเธ•เธฑเธงเธ•เธฑเนเธเนเธกเนเน€เธเธดเธ 9", "calculation"),
            ("5๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธ 10 เธ–เธถเธ 20", "calculation"),
            ("6๏ธโฃ", "เธเธฒเธฃเธเธงเธเนเธฅเธฐเธเธฒเธฃเธฅเธเธเธณเธเธงเธเธ—เธตเนเธเธฅเธฅเธฑเธเธเนเนเธฅเธฐเธ•เธฑเธงเธ•เธฑเนเธเนเธกเนเน€เธเธดเธ 20", "calculation"),
            ("7๏ธโฃ", "เธเธฒเธฃเธงเธฑเธ”เธเธงเธฒเธกเธขเธฒเธง ๐", "ai"),
            ("8๏ธโฃ", "เธเธฒเธฃเธเธฑเนเธ ๐", "ai"),
            ("9๏ธโฃ", "เธเธฒเธฃเธ•เธงเธ ๐", "ai"),
            ("๐”", "เธเธณเธเธงเธเธเธฑเธ 21 เธ–เธถเธ 100", "calculation"),
            ("1๏ธโฃ1๏ธโฃ", "เธฃเธนเธเน€เธฃเธเธฒเธเธ“เธดเธ• ๐", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เน€เธงเธฅเธฒ ๐", "ai"),
            ("1๏ธโฃ3๏ธโฃ", "เธเธฒเธฃเธเธงเธเนเธฅเธฐเธเธฒเธฃเธฅเธเธเธณเธเธงเธเธ—เธตเนเธเธฅเธฅเธฑเธเธเนเนเธฅเธฐเธ•เธฑเธงเธ•เธฑเนเธเนเธกเนเน€เธเธดเธ 100", "calculation"),
            ("1๏ธโฃ4๏ธโฃ", "เธเธฒเธฃเธเธงเธ เธฅเธเธฃเธฐเธเธ", "calculation"),
        ],
        "เธ.2": [
            ("1๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธเนเธกเนเน€เธเธดเธ 1,000", "calculation"),
            ("2๏ธโฃ", "เธเธฒเธฃเธเธงเธเนเธฅเธฐเธเธฒเธฃเธฅเธเธเธณเธเธงเธเธเธฑเธเธ—เธตเนเธเธฅเธฅเธฑเธเธเนเนเธฅเธฐเธ•เธฑเธงเธ•เธฑเนเธเนเธกเนเน€เธเธดเธ 100", "calculation"),
            ("3๏ธโฃ", "เธเธฒเธฃเธงเธฑเธ”เธเธงเธฒเธกเธขเธฒเธง ๐", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเธเธงเธเนเธฅเธฐเธเธฒเธฃเธฅเธเธเธณเธเธงเธเธเธฑเธเธ—เธตเนเธเธฅเธฅเธฑเธเธเนเนเธฅเธฐเธ•เธฑเธงเธ•เธฑเนเธเนเธกเนเน€เธเธดเธ 1,000", "calculation"),
            ("5๏ธโฃ", "เธเธฒเธฃเธเธฑเนเธ ๐", "ai"),
            ("6๏ธโฃ", "เธเธฒเธฃเธเธนเธ“", "calculation"),
            ("7๏ธโฃ", "เน€เธงเธฅเธฒ ๐", "ai"),
            ("8๏ธโฃ", "เน€เธเธดเธ ๐", "ai"),
            ("9๏ธโฃ", "เธเธฒเธฃเธซเธฒเธฃ", "calculation"),
            ("๐”", "เธเธฒเธฃเธ•เธงเธ ๐", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธฃเธนเธเน€เธฃเธเธฒเธเธ“เธดเธ• ๐", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธเธฒเธฃเธเธงเธ เธฅเธ เธเธนเธ“ เธซเธฒเธฃเธฃเธฐเธเธ", "calculation"),
        ],
        "เธ.3": [
            ("1๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธเนเธกเนเน€เธเธดเธ 100,000", "calculation"),
            ("2๏ธโฃ", "เธเธฒเธฃเธเธงเธเนเธฅเธฐเธเธฒเธฃเธฅเธเธเธณเธเธงเธเธเธฑเธเธ—เธตเนเธเธฅเธฅเธฑเธเธเนเนเธฅเธฐเธ•เธฑเธงเธ•เธฑเนเธเนเธกเนเน€เธเธดเธ 100,000", "calculation"),
            ("3๏ธโฃ", "เนเธเธเธ เธนเธกเธดเธฃเธนเธเธ เธฒเธเนเธฅเธฐเนเธเธเธ เธนเธกเธดเนเธ—เนเธ ๐", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเธงเธฑเธ”เธเธงเธฒเธกเธขเธฒเธง ๐", "ai"),
            ("5๏ธโฃ", "เน€เธงเธฅเธฒ ๐", "ai"),
            ("6๏ธโฃ", "เธเธฒเธฃเธเธฑเนเธ เธเธฒเธฃเธ•เธงเธ ๐", "ai"),
            ("7๏ธโฃ", "เธเธฒเธฃเธเธนเธ“", "calculation"),
            ("8๏ธโฃ", "เธเธฒเธฃเธซเธฒเธฃ", "calculation"),
            ("9๏ธโฃ", "เน€เธเธดเธเนเธฅเธฐเธเธฒเธฃเธเธฑเธเธ—เธถเธเธฃเธฒเธขเธฃเธฑเธเธฃเธฒเธขเธเนเธฒเธข ๐", "ai"),
            ("๐”", "เธเธธเธ” เน€เธชเนเธเธ•เธฃเธ เธฃเธฑเธเธชเธต เธชเนเธงเธเธเธญเธเน€เธชเนเธเธ•เธฃเธ เธกเธธเธก ๐", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธฃเธนเธเน€เธฃเธเธฒเธเธ“เธดเธ• ๐", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธเธฒเธฃเธเธงเธ เธฅเธ เธเธนเธ“ เธซเธฒเธฃเธฃเธฐเธเธ", "calculation"),
        ],
        "เธ.4": [
            ("1๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธเธ—เธตเนเธกเธฒเธเธเธงเนเธฒ 100,000", "calculation"),
            ("2๏ธโฃ", "เธเธฒเธฃเธเธงเธเนเธฅเธฐเธเธฒเธฃเธฅเธ", "calculation"),
            ("3๏ธโฃ", "เน€เธฃเธเธฒเธเธ“เธดเธ• ๐", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเธเธนเธ“", "calculation"),
            ("5๏ธโฃ", "เธเธฒเธฃเธซเธฒเธฃ", "calculation"),
            ("6๏ธโฃ", "เนเธเธเธ เธนเธกเธดเธฃเธนเธเธ เธฒเธ เนเธเธเธ เธนเธกเธดเนเธ—เนเธ เนเธฅเธฐเธ•เธฒเธฃเธฒเธ ๐", "ai"),
            ("7๏ธโฃ", "เธเธฒเธฃเธงเธฑเธ” ๐", "ai"),
            ("8๏ธโฃ", "เธเธทเนเธเธ—เธตเน ๐", "ai"),
            ("9๏ธโฃ", "เน€เธเธดเธ ๐", "ai"),
            ("๐”", "เน€เธจเธฉเธชเนเธงเธ", "calculation"),
            ("1๏ธโฃ1๏ธโฃ", "เน€เธงเธฅเธฒ ๐", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธ—เธจเธเธดเธขเธก", "calculation"),
            ("1๏ธโฃ3๏ธโฃ", "เธเธฒเธฃเธเธงเธ เธฅเธ เธเธนเธ“ เธซเธฒเธฃเธฃเธฐเธเธ", "calculation"),
        ],
        "เธ.5": [
            ("1๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธ เนเธฅเธฐเธเธฒเธฃเธเธงเธ เธเธฒเธฃเธฅเธ เธเธฒเธฃเธเธนเธ“ เธเธฒเธฃเธซเธฒเธฃ", "calculation"),
            ("2๏ธโฃ", "เธกเธธเธก ๐", "ai"),
            ("3๏ธโฃ", "เน€เธชเนเธเธเธเธฒเธ ๐", "ai"),
            ("4๏ธโฃ", "เธชเธ–เธดเธ•เธดเนเธฅเธฐเธเธงเธฒเธกเธเนเธฒเธเธฐเน€เธเนเธเน€เธเธทเนเธญเธเธ•เนเธ ๐", "ai"),
            ("5๏ธโฃ", "เน€เธจเธฉเธชเนเธงเธ", "calculation"),
            ("6๏ธโฃ", "เธเธฒเธฃเธเธงเธ เธเธฒเธฃเธฅเธ เธเธฒเธฃเธเธนเธ“ เธเธฒเธฃเธซเธฒเธฃเน€เธจเธฉเธชเนเธงเธ", "calculation"),
            ("7๏ธโฃ", "เธ—เธจเธเธดเธขเธก", "calculation"),
            ("8๏ธโฃ", "เธเธฒเธฃเธเธงเธ เธเธฒเธฃเธฅเธ เธเธฒเธฃเธเธนเธ“เธ—เธจเธเธดเธขเธก", "calculation"),
            ("9๏ธโฃ", "เธเธ—เธเธฃเธฐเธขเธธเธเธ•เน ๐", "ai"),
            ("๐”", "เธฃเธนเธเธชเธตเนเน€เธซเธฅเธตเนเธขเธก ๐", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธฃเธนเธเธชเธฒเธกเน€เธซเธฅเธตเนเธขเธก ๐", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธฃเธนเธเธงเธเธเธฅเธก ๐", "ai"),
            ("1๏ธโฃ3๏ธโฃ", "เธฃเธนเธเน€เธฃเธเธฒเธเธ“เธดเธ•เธชเธฒเธกเธกเธดเธ•เธดเนเธฅเธฐเธเธฃเธดเธกเธฒเธ•เธฃเธเธญเธเธ—เธฃเธเธชเธตเนเน€เธซเธฅเธตเนเธขเธกเธกเธธเธกเธเธฒเธ ๐", "ai"),
        ],
        "เธ.6": [
            ("1๏ธโฃ", "เธเธณเธเธงเธเธเธฑเธ เนเธฅเธฐเธเธฒเธฃเธเธงเธ เธเธฒเธฃเธฅเธ เธเธฒเธฃเธเธนเธ“ เธเธฒเธฃเธซเธฒเธฃ", "calculation"),
            ("2๏ธโฃ", "เธ•เธฑเธงเธเธฃเธฐเธเธญเธเธเธญเธเธเธณเธเธงเธเธเธฑเธ ๐", "ai"),
            ("3๏ธโฃ", "เน€เธจเธฉเธชเนเธงเธ เนเธฅเธฐเธเธฒเธฃเธเธงเธ เธเธฒเธฃเธฅเธ เธเธฒเธฃเธเธนเธ“ เธเธฒเธฃเธซเธฒเธฃ", "calculation"),
            ("4๏ธโฃ", "เธ—เธจเธเธดเธขเธก", "calculation"),
            ("5๏ธโฃ", "เธเธฒเธฃเธเธงเธ เธเธฒเธฃเธฅเธ เธเธฒเธฃเธเธนเธ“ เนเธฅเธฐเธเธฒเธฃเธซเธฒเธฃเธ—เธจเธเธดเธขเธก", "calculation"),
            ("6๏ธโฃ", "เน€เธชเนเธเธเธเธฒเธ ๐", "ai"),
            ("7๏ธโฃ", "เธชเธกเธเธฒเธฃเนเธฅเธฐเธเธฒเธฃเนเธเนเธชเธกเธเธฒเธฃ ๐", "ai"),
            ("8๏ธโฃ", "เธ—เธดเธจ เนเธเธเธ—เธตเนเนเธฅเธฐเนเธเธเธเธฑเธ ๐", "ai"),
            ("9๏ธโฃ", "เธฃเธนเธเธชเธตเนเน€เธซเธฅเธตเนเธขเธก ๐", "ai"),
            ("๐”", "เธฃเธนเธเธงเธเธเธฅเธก ๐", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธเธ—เธเธฃเธฐเธขเธธเธเธ•เน ๐", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธฃเธนเธเน€เธฃเธเธฒเธเธ“เธดเธ•เธชเธฒเธกเธกเธดเธ•เธดเนเธฅเธฐเธเธฃเธดเธกเธฒเธ•เธฃเธเธญเธเธ—เธฃเธเธชเธตเนเน€เธซเธฅเธตเนเธขเธกเธกเธธเธกเธเธฒเธ ๐", "ai"),
            ("1๏ธโฃ3๏ธโฃ", "เธชเธ–เธดเธ•เธดเนเธฅเธฐเธเธงเธฒเธกเธเนเธฒเธเธฐเน€เธเนเธเน€เธเธทเนเธญเธเธ•เนเธ ๐", "ai"),
        ],
        
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒเธ•เธญเธเธ•เนเธ =====
        "เธก.1": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธเธณเธเธงเธเน€เธ•เนเธก", "calculation"),
                ("2๏ธโฃ", "เธเธฒเธฃเธชเธฃเนเธฒเธเธ—เธฒเธเน€เธฃเธเธฒเธเธ“เธดเธ• ๐", "ai"),
                ("3๏ธโฃ", "เน€เธฅเธเธขเธเธเธณเธฅเธฑเธ", "calculation"),
                ("4๏ธโฃ", "เธ—เธจเธเธดเธขเธกเนเธฅเธฐเน€เธจเธฉเธชเนเธงเธ", "calculation"),
                ("5๏ธโฃ", "เธฃเธนเธเน€เธฃเธเธฒเธเธ“เธดเธ• 2 เธกเธดเธ•เธดเนเธฅเธฐ 3 เธกเธดเธ•เธด ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธชเธกเธเธฒเธฃเน€เธเธดเธเน€เธชเนเธเธ•เธฑเธงเนเธเธฃเน€เธ”เธตเธขเธง ๐", "ai"),
                ("2๏ธโฃ", "เธญเธฑเธ•เธฃเธฒเธชเนเธงเธ เธชเธฑเธ”เธชเนเธงเธ เนเธฅเธฐเธฃเนเธญเธขเธฅเธฐ", "calculation"),
                ("3๏ธโฃ", "เธเธฃเธฒเธเนเธฅเธฐเธเธงเธฒเธกเธชเธฑเธกเธเธฑเธเธเนเน€เธเธดเธเน€เธชเนเธ ๐", "ai"),
                ("4๏ธโฃ", "เธชเธ–เธดเธ•เธด (1) ๐", "ai"),
            ]
        },
        "เธก.2": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธ—เธคเธฉเธเธตเธเธ—เธเธตเธ—เธฒเนเธเธฃเธฑเธช ๐", "ai"),
                ("2๏ธโฃ", "เธเธงเธฒเธกเธฃเธนเนเน€เธเธทเนเธญเธเธ•เนเธเน€เธเธตเนเธขเธงเธเธฑเธเธเธณเธเธงเธเธเธฃเธดเธ ๐", "ai"),
                ("3๏ธโฃ", "เธเธฃเธดเธเธถเธกเนเธฅเธฐเธ—เธฃเธเธเธฃเธฐเธเธญเธ ๐", "ai"),
                ("4๏ธโฃ", "เธเธฒเธฃเนเธเธฅเธเธ—เธฒเธเน€เธฃเธเธฒเธเธ“เธดเธ• ๐", "ai"),
                ("5๏ธโฃ", "เธชเธกเธเธฑเธ•เธดเธเธญเธเน€เธฅเธเธขเธเธเธณเธฅเธฑเธ", "calculation"),
                ("6๏ธโฃ", "เธเธซเธธเธเธฒเธก ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธชเธ–เธดเธ•เธด (2) ๐", "ai"),
                ("2๏ธโฃ", "เธเธงเธฒเธกเน€เธ—เนเธฒเธเธฑเธเธ—เธธเธเธเธฃเธฐเธเธฒเธฃ ๐", "ai"),
                ("3๏ธโฃ", "เน€เธชเนเธเธเธเธฒเธ ๐", "ai"),
                ("4๏ธโฃ", "เธเธฒเธฃเนเธซเนเน€เธซเธ•เธธเธเธฅเธ—เธฒเธเน€เธฃเธเธฒเธเธ“เธดเธ• ๐", "ai"),
                ("5๏ธโฃ", "เธเธฒเธฃเนเธขเธเธ•เธฑเธงเธเธฃเธฐเธเธญเธเธเธญเธเธเธซเธธเธเธฒเธกเธ”เธตเธเธฃเธตเธชเธญเธ ๐", "ai"),
            ]
        },
        "เธก.3": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธญเธชเธกเธเธฒเธฃเน€เธเธดเธเน€เธชเนเธเธ•เธฑเธงเนเธเธฃเน€เธ”เธตเธขเธง ๐", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเนเธขเธเธ•เธฑเธงเธเธฃเธฐเธเธญเธเธเธญเธเธเธซเธธเธเธฒเธกเธ—เธตเนเธกเธตเธ”เธตเธเธฃเธตเธชเธนเธเธเธงเนเธฒเธชเธญเธ ๐", "ai"),
                ("3๏ธโฃ", "เธชเธกเธเธฒเธฃเธเธณเธฅเธฑเธเธชเธญเธเธ•เธฑเธงเนเธเธฃเน€เธ”เธตเธขเธง ๐", "ai"),
                ("4๏ธโฃ", "เธเธงเธฒเธกเธเธฅเนเธฒเธข ๐", "ai"),
                ("5๏ธโฃ", "เธเธฃเธฒเธเธเธญเธเธเธฑเธเธเนเธเธฑเธเธเธณเธฅเธฑเธเธชเธญเธ ๐", "ai"),
                ("6๏ธโฃ", "เธชเธ–เธดเธ•เธด (3) ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธฃเธฐเธเธเธชเธกเธเธฒเธฃเน€เธเธดเธเน€เธชเนเธเธชเธญเธเธ•เธฑเธงเนเธเธฃ ๐", "ai"),
                ("2๏ธโฃ", "เธงเธเธเธฅเธก ๐", "ai"),
                ("3๏ธโฃ", "เธเธตเธฃเธฐเธกเธดเธ” เธเธฃเธงเธข เนเธฅเธฐเธ—เธฃเธเธเธฅเธก ๐", "ai"),
                ("4๏ธโฃ", "เธเธงเธฒเธกเธเนเธฒเธเธฐเน€เธเนเธ ๐", "ai"),
                ("5๏ธโฃ", "เธญเธฑเธ•เธฃเธฒเธชเนเธงเธเธ•เธฃเธตเนเธเธ“เธกเธดเธ•เธด ๐", "ai"),
            ]
        },
        
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒเธ•เธญเธเธเธฅเธฒเธข =====
        "เธก.4": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เน€เธเธ• ๐", "ai"),
                ("2๏ธโฃ", "เธ•เธฃเธฃเธเธจเธฒเธชเธ•เธฃเน ๐", "ai"),
                ("3๏ธโฃ", "เธเธณเธเธงเธเธเธฃเธดเธ ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธงเธฒเธกเธชเธฑเธกเธเธฑเธเธเนเนเธฅเธฐเธเธฑเธเธเนเธเธฑเธ ๐", "ai"),
                ("2๏ธโฃ", "เธเธฑเธเธเนเธเธฑเธเน€เธญเธเธเนเนเธเน€เธเธเน€เธเธตเธขเธฅเนเธฅเธฐเธเธฑเธเธเนเธเธฑเธเธฅเธญเธเธฒเธฃเธดเธ—เธถเธก ๐", "ai"),
                ("3๏ธโฃ", "เน€เธฃเธเธฒเธเธ“เธดเธ•เธงเธดเน€เธเธฃเธฒเธฐเธซเนเนเธฅเธฐเธ เธฒเธเธ•เธฑเธ”เธเธฃเธงเธข ๐", "ai"),
            ]
        },
        "เธก.5": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธเธฑเธเธเนเธเธฑเธเธ•เธฃเธตเนเธเธ“เธกเธดเธ•เธด ๐", "ai"),
                ("2๏ธโฃ", "เน€เธกเธ—เธฃเธดเธเธเน ๐", "ai"),
                ("3๏ธโฃ", "เน€เธงเธเน€เธ•เธญเธฃเน ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธณเธเธงเธเน€เธเธดเธเธเนเธญเธ ๐", "ai"),
                ("2๏ธโฃ", "เธซเธฅเธฑเธเธเธฒเธฃเธเธฑเธเน€เธเธทเนเธญเธเธ•เนเธ ๐", "ai"),
                ("3๏ธโฃ", "เธเธงเธฒเธกเธเนเธฒเธเธฐเน€เธเนเธ ๐", "ai"),
            ]
        },
        "เธก.6": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธฅเธณเธ”เธฑเธเนเธฅเธฐเธญเธเธธเธเธฃเธก ๐", "ai"),
                ("2๏ธโฃ", "เนเธเธฅเธเธนเธฅเธฑเธชเน€เธเธทเนเธญเธเธ•เนเธ ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธงเธฒเธกเธซเธกเธฒเธขเธเธญเธเธชเธ–เธดเธ•เธดเธจเธฒเธชเธ•เธฃเนเนเธฅเธฐเธเนเธญเธกเธนเธฅ ๐", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเธงเธดเน€เธเธฃเธฒเธฐเธซเนเนเธฅเธฐเธเธณเน€เธชเธเธญเธเนเธญเธกเธนเธฅเน€เธเธดเธเธเธธเธ“เธ เธฒเธ ๐", "ai"),
                ("3๏ธโฃ", "เธเธฒเธฃเธงเธดเน€เธเธฃเธฒเธฐเธซเนเนเธฅเธฐเธเธณเน€เธชเธเธญเธเนเธญเธกเธนเธฅเน€เธเธดเธเธเธฃเธดเธกเธฒเธ“ ๐", "ai"),
                ("4๏ธโฃ", "เธ•เธฑเธงเนเธเธฃเธชเธธเนเธกเนเธฅเธฐเธเธฒเธฃเนเธเธเนเธเธเธเธงเธฒเธกเธเนเธฒเธเธฐเน€เธเนเธ ๐", "ai"),
            ]
        },
    }
    
    # Check if grade is เธก.1-6 (has terms)
    if grade_select in ["เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]:
        # Select term first
        term_options = list(ipst_topics[grade_select].keys())
        term_select = st.selectbox("๐“… เน€เธฅเธทเธญเธเน€เธ—เธญเธก:", term_options)
        topics = ipst_topics[grade_select][term_select]
    else:
        # Primary school grades
        topics = ipst_topics.get(grade_select, [])
    
    # Topic selection with display names
    topic_options = [f"{prefix} {name}" for prefix, name, _ in topics]
    topic_select = st.selectbox("๐“– เน€เธฅเธทเธญเธเธซเธฑเธงเธเนเธญ:", topic_options)
    
    # Get selected topic details
    selected_topic = None
    selected_type = None
    for prefix, name, topic_type in topics:
        full_name = f"{prefix} {name}"
        if full_name == topic_select:
            selected_topic = name
            selected_type = topic_type
            break
    
    # Settings based on topic type
    if selected_type == "calculation":
        # Math settings
        if "เธเธฒเธฃเธเธนเธ“" in selected_topic:
            op_label = "เธเธนเธ“ (x)"
        elif "เธเธฒเธฃเธซเธฒเธฃ" in selected_topic:
            op_label = "เธซเธฒเธฃ (รท)"
        elif "เธเธฒเธฃเธฅเธ" in selected_topic or "เธฅเธเธฃเธฐเธเธ" in selected_topic:
            op_label = "เธฅเธ (-)"
        elif "เธเธงเธ" in selected_topic or "เธฃเธฐเธเธ" in selected_topic:
            op_label = "เธเธงเธ (+)"
        else:
            op_label = st.selectbox("เน€เธฅเธทเธญเธเน€เธเธฃเธทเนเธญเธเธซเธกเธฒเธข", ["เธเธงเธ (+)", "เธฅเธ (-)", "เธเธนเธ“ (x)", "เธซเธฒเธฃ (รท)"])
        
        # Map Thai label to English key for backend
        op_map = {"เธเธงเธ (+)": "Addition (+)", "เธฅเธ (-)": "Subtraction (-)", "เธเธนเธ“ (x)": "Multiplication (x)", "เธซเธฒเธฃ (รท)": "Division (รท)"}
        op = op_map.get(op_label, "Addition (+)")
        
        # Auto-config ranges based on grade
        d_min, d_max = 1, 20
        if grade_select == "เธ.1":
            if "10 เธ–เธถเธ 20" in selected_topic:
                d_min, d_max = 10, 20
            elif "21 เธ–เธถเธ 100" in selected_topic:
                d_min, d_max = 21, 100
            else:
                d_min, d_max = 1, 20
        elif grade_select == "เธ.2":
            if "1,000" in selected_topic:
                d_min, d_max = 100, 1000
            else:
                d_min, d_max = 1, 100
        elif grade_select == "เธ.3":
            d_min, d_max = 10, 100000
        elif grade_select in ["เธ.4", "เธ.5", "เธ.6"]:
            d_min, d_max = 100, 100000
        
        num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=20)
        
        # Custom Prompt Section (for AI topics)
        if selected_type == "ai":
            with st.expander("โ๏ธ เธเธฃเธฑเธเนเธ•เนเธ Prompt (เนเธกเนเธเธฑเธเธเธฑเธ)", expanded=False):
                custom_prompt = st.text_area(
                    "Prompt เธชเธณเธซเธฃเธฑเธ AI (เธ–เนเธฒเน€เธงเนเธเธงเนเธฒเธเธเธฐเนเธเนเธเนเธฒเน€เธฃเธดเนเธกเธ•เนเธ)",
                    value="",
                    height=100,
                    help="เธเธฃเธฑเธเนเธ•เนเธ prompt เน€เธเธทเนเธญเนเธซเนเนเธ”เนเธเธฅเธฅเธฑเธเธเนเธ•เธฒเธกเธ•เนเธญเธเธเธฒเธฃ"
                )
                
                st.markdown("**๐’ก เธ•เธฑเธงเธญเธขเนเธฒเธ Prompt เธ—เธตเนเธ”เธต:**")
                st.code("เธชเธฃเนเธฒเธเนเธเธ—เธขเนเธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน 10 เธเนเธญ เน€เธฃเธทเนเธญเธเธเธฒเธฃเธเธงเธ เธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธเธเธฃเธฐเธ–เธกเธ.2 เนเธซเนเนเธเธ—เธขเนเธกเธตเธเธงเธฒเธกเธซเธฅเธฒเธเธซเธฅเธฒเธข เน€เธเนเธ เธชเธ–เธฒเธเธเธฒเธฃเธ“เนเนเธเธเธตเธงเธดเธ•เธเธฃเธดเธ เธเธฑเธเธซเธฒเธ—เธตเนเธ•เนเธญเธเธเธดเธ”เธงเธดเน€เธเธฃเธฒเธฐเธซเน เนเธฅเธฐเธกเธตเน€เธเธฅเธขเธเธฃเนเธญเธกเธงเธดเธเธตเธ—เธณ", language="text")
        
        if st.button("๐€ เธชเธฃเนเธฒเธเนเธเธเธฒเธ", type="primary"):
            # Check if AI is required
            if selected_type == "ai":
                if not st.session_state.api_key:
                    st.info("๐”‘ เธ•เนเธญเธเนเธเน API Key เธชเธณเธซเธฃเธฑเธเธซเธฑเธงเธเนเธญเธเธตเนเธเนเธฐ เธเธฃเธญเธ API Key เนเธ”เนเธ—เธตเนเธ”เนเธฒเธเธเธเธเธฐเธเธฐ")
                else:
                    # AI generation
                    questions, answers = generator.generate_ai_worksheet(selected_topic, grade_select, num_q)
                    pdf = generator.create_pdf(title, school_name, selected_topic, questions, answers, qr_url, uploaded_logo)
                    word = generator.create_word_doc(title, school_name, selected_topic, questions, answers)
                    
                    st.session_state.generated_pdf = pdf
                    st.session_state.generated_word = word
                    st.session_state.generated_filename = "worksheet"
            else:
                # Calculation generation (no AI needed)
                questions, answers = generator.generate_questions(op, num_q, d_min, d_max)
                pdf = generator.create_pdf(title, school_name, selected_topic, questions, answers, qr_url, uploaded_logo)
                word = generator.create_word_doc(title, school_name, selected_topic, questions, answers)
                
                st.session_state.generated_pdf = pdf
                st.session_state.generated_word = word
                st.session_state.generated_filename = "worksheet"
                st.session_state.preview_questions = questions
                st.session_state.preview_answers = answers
        
        # Show preview and download buttons if content is generated
        if st.session_state.generated_pdf is not None:
            st.success("โ… เธชเธฃเนเธฒเธเธชเธณเน€เธฃเนเธ!")
            
            # Preview section
            with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธณเธ–เธฒเธกเนเธฅเธฐเน€เธเธฅเธข", expanded=True):
                st.markdown("### ๐“ เธเธณเธ–เธฒเธก / Questions")
                for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                    st.write(f"**{i}.** {q}")
                if len(st.session_state.preview_questions) > 10:
                    st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_questions) - 10} เธเนเธญ")
                
                st.markdown("### โ… เน€เธเธฅเธข / Answers")
                for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                    st.write(f"**{i}.** {a}")
                if len(st.session_state.preview_answers) > 10:
                    st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_answers) - 10} เธเนเธญ")
            
            c1, c2 = st.columns(2)
            c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
            c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            if st.button("๐—‘๏ธ เธฅเนเธฒเธเนเธฅเธฐเธชเธฃเนเธฒเธเนเธซเธกเน"):
                st.session_state.generated_pdf = None
                st.session_state.generated_word = None
                st.session_state.preview_questions = None
                st.session_state.preview_answers = None
                st.rerun()
    
    else:  # AI required topic
        st.info(f"๐“ เธซเธฑเธงเธเนเธญเธเธตเนเธ•เนเธญเธเนเธเน AI เนเธเธเธฒเธฃเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธเนเธฐ")
        st.markdown("โน๏ธ **เธซเธกเธฒเธขเน€เธซเธ•เธธ:** เธซเธฑเธงเธเนเธญเธ—เธตเนเธกเธต ๐ เธเธฐเนเธเน Google AI เนเธเธเธฒเธฃเธชเธฃเนเธฒเธเนเธเธ—เธขเนเนเธฅเธฐเนเธเธเธเธถเธเธซเธฑเธ”เธ—เธตเนเธซเธฅเธฒเธเธซเธฅเธฒเธข")
        
        num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=20)
        
        if st.button("๐€ เธชเธฃเนเธฒเธเนเธเธเธฒเธ", type="primary"):
            if not st.session_state.api_key:
                st.info("๐”‘ เธ•เนเธญเธเนเธเน API Key เธชเธณเธซเธฃเธฑเธเธซเธฑเธงเธเนเธญเธเธตเนเธเนเธฐ เธเธฃเธญเธ API Key เนเธ”เนเธ—เธตเนเธ”เนเธฒเธเธเธเธเธฐเธเธฐ")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”..."):
                    questions, answers = generator.generate_ai_worksheet(selected_topic, grade_select, num_q)
                    pdf = generator.create_pdf(title, school_name, selected_topic, questions, answers, qr_url, uploaded_logo)
                    word = generator.create_word_doc(title, school_name, selected_topic, questions, answers)
                    
                    st.session_state.generated_pdf = pdf
                    st.session_state.generated_word = word
                    st.session_state.generated_filename = "worksheet"
        
        # Show download buttons if content is generated
        if st.session_state.generated_pdf is not None:
            st.success("เธชเธฃเนเธฒเธเธชเธณเน€เธฃเนเธ! เธ”เธฒเธงเธเนเนเธซเธฅเธ”เนเธ”เนเธ—เธตเนเธ”เนเธฒเธเธฅเนเธฒเธ")
            c1, c2 = st.columns(2)
            c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
            c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            if st.button("๐—‘๏ธ เธฅเนเธฒเธเนเธฅเธฐเธชเธฃเนเธฒเธเนเธซเธกเน"):
                st.session_state.generated_pdf = None
                st.session_state.generated_word = None
                st.rerun()

elif "เธงเธดเธ—เธขเธฒเธจเธฒเธชเธ•เธฃเน" in mode_select:
    st.subheader("๐”ฌ เธชเธฃเนเธฒเธเนเธเธเธฒเธเธงเธดเธ—เธขเธฒเธจเธฒเธชเธ•เธฃเน (เธ•เธฒเธกเธซเธฅเธฑเธเธชเธนเธ•เธฃ เธชเธชเธงเธ—.)")
    
    # Science Curriculum Data
    science_topics = {
        # ===== เธฃเธฐเธ”เธฑเธเธเธฃเธฐเธ–เธกเธจเธถเธเธฉเธฒ =====
        "เธ.1": [
            ("1๏ธโฃ", "เธชเธดเนเธเธ•เนเธฒเธเธฃเธญเธเธ•เธฑเธงเน€เธฃเธฒ (เธชเธดเนเธเธกเธตเธเธตเธงเธดเธ•, เธชเธดเนเธเนเธกเนเธกเธตเธเธตเธงเธดเธ•, เธชเธกเธเธฑเธ•เธดเธเธญเธเธงเธฑเธชเธ”เธธ) ๐", "ai"),
            ("2๏ธโฃ", "เธเธทเธเธฃเธญเธเธ•เธฑเธงเน€เธฃเธฒ (เธชเนเธงเธเธเธฃเธฐเธเธญเธเธเธญเธเธเธทเธ, เธเธฒเธฃเน€เธเธฃเธดเธเน€เธ•เธดเธเนเธ•) ๐", "ai"),
            ("3๏ธโฃ", "เธชเธฑเธ•เธงเนเธฃเธญเธเธ•เธฑเธงเน€เธฃเธฒ (เธชเธฑเธ•เธงเนเธซเธฅเธฒเธเธซเธฅเธฒเธขเธเธเธดเธ”, เธเธฒเธฃเธ”เธนเนเธฅเธชเธฑเธ•เธงเน) ๐", "ai"),
            ("4๏ธโฃ", "เธ”เธงเธเธ”เธฒเธงเนเธฅเธฐเธ—เนเธญเธเธเนเธฒ (เธ”เธงเธเธญเธฒเธ—เธดเธ•เธขเน, เธ”เธงเธเธเธฑเธเธ—เธฃเน, เธ”เธงเธเธ”เธฒเธง) ๐", "ai"),
            ("5๏ธโฃ", "เธชเธ เธฒเธเธญเธฒเธเธฒเธจ (เธซเธเธฒเธง, เธฃเนเธญเธ, เธเธ, เธฅเธก) ๐", "ai"),
        ],
        "เธ.2": [
            ("1๏ธโฃ", "เธชเธดเนเธเธกเธตเธเธตเธงเธดเธ•เธเธฑเธเธเธฒเธฃเธ”เธณเธฃเธเธเธตเธงเธดเธ• (เธญเธฒเธซเธฒเธฃ, เธ—เธตเนเธญเธขเธนเนเธญเธฒเธจเธฑเธข, เธเธฒเธฃเธชเธทเธเธเธฑเธเธเธธเน) ๐", "ai"),
            ("2๏ธโฃ", "เธชเธดเนเธเนเธงเธ”เธฅเนเธญเธก (เนเธชเธ, เน€เธชเธตเธขเธ, เธเธงเธฒเธกเธฃเนเธญเธ) ๐", "ai"),
            ("3๏ธโฃ", "เธเนเธณเนเธฅเธฐเธญเธฒเธเธฒเธจ (เธชเธ–เธฒเธเธฐเธเธญเธเธเนเธณ, เธเธฒเธฃเน€เธเธดเธ”เธเธ) ๐", "ai"),
            ("4๏ธโฃ", "เธ”เธดเธ (เธญเธเธเนเธเธฃเธฐเธเธญเธเธเธญเธเธ”เธดเธ, เธเธเธดเธ”เธเธญเธเธ”เธดเธ) ๐", "ai"),
            ("5๏ธโฃ", "เธ—เนเธญเธเธเนเธฒเนเธฅเธฐเธเธฒเธฃเธเธขเธฒเธเธฃเธ“เนเธญเธฒเธเธฒเธจ (เธเธฒเธฃเธชเธฑเธเน€เธเธ•เน€เธกเธ, เธเธฒเธฃเธเธขเธฒเธเธฃเธ“เนเธญเธฒเธเธฒเธจ) ๐", "ai"),
        ],
        "เธ.3": [
            ("1๏ธโฃ", "เธฃเนเธฒเธเธเธฒเธขเธเธญเธเน€เธฃเธฒ (เธฃเธฐเธเธเธขเนเธญเธขเธญเธฒเธซเธฒเธฃ, เธฃเธฐเธเธเธซเธฒเธขเนเธ) ๐", "ai"),
            ("2๏ธโฃ", "เธเธทเธเธเธฑเธเธเธฒเธฃเธ”เธณเธฃเธเธเธตเธงเธดเธ• (เธเธฒเธฃเธชเธฑเธเน€เธเธฃเธฒเธฐเธซเนเธ”เนเธงเธขเนเธชเธ, เธเธฒเธฃเธเธขเธฒเธขเธเธฑเธเธเธธเน) ๐", "ai"),
            ("3๏ธโฃ", "เธชเธดเนเธเธกเธตเธเธตเธงเธดเธ•เธเธฑเธเธชเธดเนเธเนเธงเธ”เธฅเนเธญเธก (เธซเนเธงเธเนเธเนเธญเธฒเธซเธฒเธฃ, เธชเธกเธ”เธธเธฅเนเธเธเธฃเธฃเธกเธเธฒเธ•เธด) ๐", "ai"),
            ("4๏ธโฃ", "เธงเธฑเธชเธ”เธธเธฃเธญเธเธ•เธฑเธง (เนเธฅเธซเธฐ, เนเธกเน, เธเธฅเธฒเธชเธ•เธดเธ) ๐", "ai"),
            ("5๏ธโฃ", "เนเธฃเธเนเธฅเธฐเธเธฒเธฃเน€เธเธฅเธทเนเธญเธเธ—เธตเน (เนเธฃเธเธเธฅเธฑเธ, เนเธฃเธเธ”เธถเธ, เนเธฃเธเน€เธชเธตเธขเธ”เธ—เธฒเธ) ๐", "ai"),
            ("6๏ธโฃ", "เธเธฅเธฑเธเธเธฒเธ (เธเธงเธฒเธกเธฃเนเธญเธ, เนเธชเธ, เน€เธชเธตเธขเธ) ๐", "ai"),
        ],
        "เธ.4": [
            ("1๏ธโฃ", "เธฃเธฐเธเธเธฃเนเธฒเธเธเธฒเธข (เธฃเธฐเธเธเธซเธกเธธเธเน€เธงเธตเธขเธเน€เธฅเธทเธญเธ”, เธฃเธฐเธเธเธเธฑเธเธ–เนเธฒเธข) ๐", "ai"),
            ("2๏ธโฃ", "เธเธทเธเธ—เธตเนเธซเธฅเธฒเธเธซเธฅเธฒเธข (เธเธฒเธฃเธเธณเนเธเธเธเธทเธ, เธเธฒเธฃเธชเธทเธเธเธฑเธเธเธธเนเธเธทเธ) ๐", "ai"),
            ("3๏ธโฃ", "เธชเธดเนเธเธกเธตเธเธตเธงเธดเธ•เธเธฑเธเธชเธดเนเธเนเธงเธ”เธฅเนเธญเธก (เนเธซเธฅเนเธเธเนเธณ, เธซเนเธงเธเนเธเนเธญเธฒเธซเธฒเธฃ) ๐", "ai"),
            ("4๏ธโฃ", "เธชเธชเธฒเธฃ (เธชเธ–เธฒเธเธฐ, เธเธฒเธฃเน€เธเธฅเธตเนเธขเธเนเธเธฅเธ) ๐", "ai"),
            ("5๏ธโฃ", "เนเธฃเธเนเธฅเธฐเธเธงเธฒเธกเธ”เธฑเธ (เนเธฃเธเนเธเธเธฃเธฃเธกเธเธฒเธ•เธด, เธเธงเธฒเธกเธ”เธฑเธเธญเธฒเธเธฒเธจ) ๐", "ai"),
            ("6๏ธโฃ", "เธเธฅเธฑเธเธเธฒเธเนเธเธเนเธฒ (เนเธเธเนเธฒเธเธทเนเธเธเธฒเธ, เธงเธเธเธฃเนเธเธเนเธฒ) ๐", "ai"),
        ],
        "เธ.5": [
            ("1๏ธโฃ", "เธฃเธฐเธเธเธชเธธเธเธ เธฒเธ (เธฎเธญเธฃเนเนเธกเธ, เธเธฒเธฃเน€เธเธฃเธดเธเน€เธ•เธดเธเนเธ•) ๐", "ai"),
            ("2๏ธโฃ", "เธเธฒเธฃเธชเธทเธเธเธฑเธเธเธธเน (เธเธฒเธฃเธชเธทเธเธเธฑเธเธเธธเนเธชเธฑเธ•เธงเน, เธเธฒเธฃเธชเธทเธเธเธฑเธเธเธธเนเธเธทเธ) ๐", "ai"),
            ("3๏ธโฃ", "เธชเธดเนเธเนเธงเธ”เธฅเนเธญเธก (เธเธฒเธฃเธ–เนเธฒเธขเธ—เธญเธ”เธเธฅเธฑเธเธเธฒเธ, เธชเธดเนเธเธกเธตเธเธตเธงเธดเธ•เธเธฑเธเธชเธดเนเธเนเธงเธ”เธฅเนเธญเธก) ๐", "ai"),
            ("4๏ธโฃ", "เธชเธชเธฒเธฃ (เธญเธฐเธ•เธญเธก, เธเธฒเธ•เธธ, เธชเธฒเธฃเธเธฃเธฐเธเธญเธ) ๐", "ai"),
            ("5๏ธโฃ", "เนเธฃเธเนเธฅเธฐเธเธฒเธฃเน€เธเธฅเธทเนเธญเธเธ—เธตเน (เนเธฃเธเนเธเนเธกเธ–เนเธงเธ, เนเธฃเธเน€เธชเธตเธขเธ”เธ—เธฒเธ) ๐", "ai"),
            ("6๏ธโฃ", "เธเธฅเธทเนเธ (เธเธฅเธทเนเธเน€เธชเธตเธขเธ, เธเธฅเธทเนเธเนเธชเธ) ๐", "ai"),
        ],
        "เธ.6": [
            ("1๏ธโฃ", "เธฃเธฐเธเธเธ•เนเธญเธกเนเธฃเนเธ—เนเธญ (เธฎเธญเธฃเนเนเธกเธ, เธ•เนเธญเธกเนเธฃเนเธ—เนเธญเธชเธณเธเธฑเธ) ๐", "ai"),
            ("2๏ธโฃ", "เธเธฑเธเธเธธเธจเธฒเธชเธ•เธฃเนเน€เธเธทเนเธญเธเธ•เนเธ (เธฅเธฑเธเธฉเธ“เธฐเธ—เธฒเธเธเธฑเธเธเธธเธเธฃเธฃเธก, เธเธฒเธฃเธ–เนเธฒเธขเธ—เธญเธ”เธฅเธฑเธเธฉเธ“เธฐ) ๐", "ai"),
            ("3๏ธโฃ", "เธงเธดเธงเธฑเธ’เธเธฒเธเธฒเธฃ (เธเธฒเธฃเน€เธเธฅเธตเนเธขเธเนเธเธฅเธเธเธญเธเธชเธดเนเธเธกเธตเธเธตเธงเธดเธ•) ๐", "ai"),
            ("4๏ธโฃ", "เธชเธชเธฒเธฃเนเธฅเธฐเธเธฅเธฑเธเธเธฒเธ (เธเธเธ—เธฃเธเธเธฅเธฑเธเธเธฒเธ, เธเธฒเธฃเธ–เนเธฒเธขเนเธญเธเธเธฅเธฑเธเธเธฒเธ) ๐", "ai"),
            ("5๏ธโฃ", "เธฃเธฐเธเธเธชเธธเธฃเธดเธขเธฐ (เธ”เธฒเธงเน€เธเธฃเธฒเธฐเธซเน, เธเธฒเธฃเน€เธเธดเธ”เธเธฅเธฒเธเธงเธฑเธ-เธเธฅเธฒเธเธเธทเธ) ๐", "ai"),
            ("6๏ธโฃ", "เธชเธดเนเธเนเธงเธ”เธฅเนเธญเธก (เธ—เธฃเธฑเธเธขเธฒเธเธฃเธเธฃเธฃเธกเธเธฒเธ•เธด, เธเธฒเธฃเธญเธเธธเธฃเธฑเธเธฉเน) ๐", "ai"),
        ],
        
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒเธ•เธญเธเธ•เนเธ =====
        "เธก.1": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธชเธฒเธฃเธเธฃเธดเธชเธธเธ—เธเธดเน ๐", "ai"),
                ("2๏ธโฃ", "เธซเธเนเธงเธขเธเธทเนเธเธเธฒเธเธเธญเธเธชเธดเนเธเธกเธตเธเธตเธงเธดเธ• ๐", "ai"),
                ("3๏ธโฃ", "เธซเธเนเธงเธขเธเธทเนเธเธเธฒเธเธเธญเธเธเธฒเธฃเธ”เธณเธฃเธเธเธตเธงเธดเธ•เธเธญเธเธเธทเธ ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธฅเธฑเธเธเธฒเธเธเธงเธฒเธกเธฃเนเธญเธ ๐", "ai"),
                ("2๏ธโฃ", "เธเธฃเธฐเธเธงเธเธเธฒเธฃเน€เธเธฅเธตเนเธขเธเนเธเธฅเธเธฅเธกเธเนเธฒเธญเธฒเธเธฒเธจ ๐", "ai"),
            ]
        },
        "เธก.2": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธชเธฒเธฃเธฅเธฐเธฅเธฒเธข ๐", "ai"),
                ("2๏ธโฃ", "เธฃเนเธฒเธเธเธฒเธขเธกเธเธธเธฉเธขเน ๐", "ai"),
                ("3๏ธโฃ", "เธเธฒเธฃเน€เธเธฅเธทเนเธญเธเธ—เธตเนเนเธฅเธฐเนเธฃเธ ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธฒเธเนเธฅเธฐเธเธฅเธฑเธเธเธฒเธ ๐", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเนเธขเธเธชเธฒเธฃ ๐", "ai"),
                ("3๏ธโฃ", "เนเธฅเธเนเธฅเธฐเธเธฒเธฃเน€เธเธฅเธตเนเธขเธเนเธเธฅเธ ๐", "ai"),
            ]
        },
        "เธก.3": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธเธฑเธเธเธธเธจเธฒเธชเธ•เธฃเน ๐", "ai"),
                ("2๏ธโฃ", "เธเธฅเธทเนเธเนเธฅเธฐเนเธชเธ ๐", "ai"),
                ("3๏ธโฃ", "เธฃเธฐเธเธเธชเธธเธฃเธดเธขเธฐเธเธญเธเน€เธฃเธฒ ๐", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธเธดเธเธดเธฃเธดเธขเธฒเน€เธเธกเธตเนเธฅเธฐเธงเธฑเธชเธ”เธธเนเธเธเธตเธงเธดเธ•เธเธฃเธฐเธเธณเธงเธฑเธ ๐", "ai"),
                ("2๏ธโฃ", "เนเธเธเนเธฒ ๐", "ai"),
                ("3๏ธโฃ", "เธฃเธฐเธเธเธเธดเน€เธงเธจเนเธฅเธฐเธเธงเธฒเธกเธซเธฅเธฒเธเธซเธฅเธฒเธขเธ—เธฒเธเธเธตเธงเธ เธฒเธ ๐", "ai"),
            ]
        },
    }
    
    # Grade Selection
    science_grade_options = ["เธ.1", "เธ.2", "เธ.3", "เธ.4", "เธ.5", "เธ.6", "เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]
    science_grade = st.selectbox("๐“ เน€เธฅเธทเธญเธเธฃเธฐเธ”เธฑเธเธเธฑเนเธ:", science_grade_options)
    
    # เธก.4-6 Subject Selector (เน€เธเธกเธต เธเธดเธชเธดเธเธชเน เธเธตเธงเธฐ)
    if science_grade in ["เธก.4", "เธก.5", "เธก.6"]:
        subject_options = ["เน€เธเธกเธต (Chemistry)", "เธเธดเธชเธดเธเธชเน (Physics)", "เธเธตเธงเธงเธดเธ—เธขเธฒ (Biology)"]
        science_subject = st.selectbox("๐งช เน€เธฅเธทเธญเธเธงเธดเธเธฒ:", subject_options)
        
        # Get subject key
        subject_key = science_subject.split(" (")[0]  # "เน€เธเธกเธต", "เธเธดเธชเธดเธเธชเน", or "เธเธตเธงเธงเธดเธ—เธขเธฒ"
    
    # Check if grade is เธก.1-3 (has terms) or เธก.4-6 (has subjects)
    if science_grade in ["เธก.1", "เธก.2", "เธก.3"]:
        # Select term first
        science_term_options = list(science_topics[science_grade].keys())
        science_term = st.selectbox("๐“… เน€เธฅเธทเธญเธเน€เธ—เธญเธก:", science_term_options)
        science_topics_list = science_topics[science_grade][science_term]
        selected_grade_level = science_grade
    elif science_grade in ["เธก.4", "เธก.5", "เธก.6"]:
        # เธก.4-6: Select term first
        science_term_options = ["เน€เธ—เธญเธก 1", "เน€เธ—เธญเธก 2"]
        science_term = st.selectbox("๐“… เน€เธฅเธทเธญเธเน€เธ—เธญเธก:", science_term_options)
        
        # Get topics based on subject and grade
        science_topics_list = []
        
        # ===== เน€เธเธกเธต (Chemistry) เธก.4-6 =====
        if subject_key == "เน€เธเธกเธต":
            if science_grade == "เธก.4":
                science_topics_list = [
                    ("1๏ธโฃ", "เธญเธฐเธ•เธญเธกเนเธฅเธฐเธชเธกเธเธฑเธ•เธดเธเธญเธเธเธฒเธ•เธธ ๐", "ai"),
                    ("2๏ธโฃ", "เธเธฑเธเธเธฐเน€เธเธกเธต ๐", "ai"),
                    ("3๏ธโฃ", "เธเธฃเธดเธกเธฒเธ“เธชเธฑเธกเธเธฑเธเธเนเนเธเธเธเธดเธเธดเธฃเธดเธขเธฒเน€เธเธกเธต ๐", "ai"),
                ]
            elif science_grade == "เธก.5":
                science_topics_list = [
                    ("1๏ธโฃ", "เธชเธกเธเธฑเธ•เธดเธเธญเธเธเนเธฒเธเนเธฅเธฐเธชเธกเธเธฒเธฃเน€เธเธกเธต ๐", "ai"),
                    ("2๏ธโฃ", "เธญเธฑเธ•เธฃเธฒเธเธฒเธฃเน€เธเธดเธ”เธเธเธดเธเธดเธฃเธดเธขเธฒเน€เธเธกเธต ๐", "ai"),
                    ("3๏ธโฃ", "เธชเธกเธ”เธธเธฅเน€เธเธกเธต ๐", "ai"),
                    ("4๏ธโฃ", "เธเธฃเธ”-เน€เธเธช ๐", "ai"),
                ]
            elif science_grade == "เธก.6":
                science_topics_list = [
                    ("1๏ธโฃ", "เนเธเธเนเธฒเน€เธเธกเธต ๐", "ai"),
                    ("2๏ธโฃ", "เธเธฒเธ•เธธเธญเธดเธเธ—เธฃเธตเธขเนเนเธฅเธฐเธชเธฒเธฃเธเธตเธงเนเธกเน€เธฅเธเธธเธฅ ๐", "ai"),
                    ("3๏ธโฃ", "เน€เธเธกเธตเธญเธดเธเธ—เธฃเธตเธขเน ๐", "ai"),
                ]
        
        # ===== เธเธดเธชเธดเธเธชเน (Physics) เธก.4-6 =====
        elif subject_key == "เธเธดเธชเธดเธเธชเน":
            if science_grade == "เธก.4":
                science_topics_list = [
                    ("1๏ธโฃ", "เธเธฒเธฃเน€เธเธฅเธทเนเธญเธเธ—เธตเนเนเธเธงเธ•เธฃเธ ๐", "ai"),
                    ("2๏ธโฃ", "เนเธฃเธเนเธฅเธฐเธเธเธเธฒเธฃเน€เธเธฅเธทเนเธญเธเธ—เธตเน ๐", "ai"),
                    ("3๏ธโฃ", "เธเธฒเธเนเธฅเธฐเธเธฅเธฑเธเธเธฒเธ ๐", "ai"),
                    ("4๏ธโฃ", "เนเธกเน€เธกเธเธ•เธฑเธกเนเธฅเธฐเธเธฒเธฃเธเธ ๐", "ai"),
                ]
            elif science_grade == "เธก.5":
                science_topics_list = [
                    ("1๏ธโฃ", "เธเธฒเธฃเน€เธเธฅเธทเนเธญเธเธ—เธตเนเนเธเธฃเธฐเธเธเธ•เนเธฒเธเน (เธงเธเธเธฅเธก, เนเธเนเธ, เธชเธฑเนเธ) ๐", "ai"),
                    ("2๏ธโฃ", "เนเธฃเธเนเธเธเธฃเธฃเธกเธเธฒเธ•เธด ๐", "ai"),
                    ("3๏ธโฃ", "เธเธฅเธทเนเธ ๐", "ai"),
                    ("4๏ธโฃ", "เน€เธชเธตเธขเธ ๐", "ai"),
                    ("5๏ธโฃ", "เนเธชเธ ๐", "ai"),
                ]
            elif science_grade == "เธก.6":
                science_topics_list = [
                    ("1๏ธโฃ", "เนเธเธเนเธฒเธชเธ–เธดเธ•เนเธฅเธฐเนเธเธเนเธฒเธเธฃเธฐเนเธช ๐", "ai"),
                    ("2๏ธโฃ", "เนเธกเนเน€เธซเธฅเนเธเนเธเธเนเธฒ ๐", "ai"),
                    ("3๏ธโฃ", "เธเธดเธชเธดเธเธชเนเธญเธฐเธ•เธญเธก ๐", "ai"),
                    ("4๏ธโฃ", "เธเธดเธชเธดเธเธชเนเธเธดเธงเน€เธเธฅเธตเธขเธฃเน ๐", "ai"),
                ]
        
        # ===== เธเธตเธงเธงเธดเธ—เธขเธฒ (Biology) เธก.4-6 =====
        elif subject_key == "เธเธตเธงเธงเธดเธ—เธขเธฒ":
            if science_grade == "เธก.4":
                science_topics_list = [
                    ("1๏ธโฃ", "เธฃเธฐเธเธเธขเนเธญเธขเธญเธฒเธซเธฒเธฃ ๐", "ai"),
                    ("2๏ธโฃ", "เธฃเธฐเธเธเธซเธฒเธขเนเธ ๐", "ai"),
                    ("3๏ธโฃ", "เธฃเธฐเธเธเธซเธกเธธเธเน€เธงเธตเธขเธเน€เธฅเธทเธญเธ” ๐", "ai"),
                    ("4๏ธโฃ", "เธฃเธฐเธเธเธเธฑเธเธ–เนเธฒเธข ๐", "ai"),
                    ("5๏ธโฃ", "เธฃเธฐเธเธเธเธฃเธฐเธชเธฒเธ— ๐", "ai"),
                    ("6๏ธโฃ", "เธฃเธฐเธเธเธ•เนเธญเธกเนเธฃเนเธ—เนเธญ ๐", "ai"),
                ]
            elif science_grade == "เธก.5":
                science_topics_list = [
                    ("1๏ธโฃ", "เธเธฒเธฃเธ–เนเธฒเธขเธ—เธญเธ”เธชเธฒเธฃเธ เธฒเธขเนเธเธฃเนเธฒเธเธเธฒเธข ๐", "ai"),
                    ("2๏ธโฃ", "เธฃเธฐเธเธเธ เธนเธกเธดเธเธธเนเธกเธเธฑเธ ๐", "ai"),
                    ("3๏ธโฃ", "เธเธฒเธฃเธชเธทเธเธเธฑเธเธเธธเนเนเธฅเธฐเธเธฑเธ’เธเธฒเธเธฒเธฃ ๐", "ai"),
                    ("4๏ธโฃ", "เธเธฒเธฃเธ–เนเธฒเธขเธ—เธญเธ”เธฅเธฑเธเธฉเธ“เธฐเธ—เธฒเธเธเธฑเธเธเธธเธเธฃเธฃเธก ๐", "ai"),
                ]
            elif science_grade == "เธก.6":
                science_topics_list = [
                    ("1๏ธโฃ", "เธเธฑเธเธเธธเธจเธฒเธชเธ•เธฃเน ๐", "ai"),
                    ("2๏ธโฃ", "เธเธฑเธเธเธธเธเธฃเธฃเธกเน€เธ—เธเนเธเนเธฅเธขเธต ๐", "ai"),
                    ("3๏ธโฃ", "เธงเธดเธงเธฑเธ’เธเธฒเธเธฒเธฃ ๐", "ai"),
                    ("4๏ธโฃ", "เธเธดเน€เธงเธจเธงเธดเธ—เธขเธฒ ๐", "ai"),
                    ("5๏ธโฃ", "เธชเธดเนเธเนเธงเธ”เธฅเนเธญเธก ๐", "ai"),
                ]
        
        selected_grade_level = f"{science_grade} {subject_key}"
    else:
        # Primary school grades
        science_topics_list = science_topics.get(science_grade, [])
        selected_grade_level = science_grade
    
    # ==== DROPDOWN STRUCTURE ====
    # Create type dropdown
    create_options = [
        "๐“ เนเธเธเธฒเธ / เนเธเธเธเธถเธเธซเธฑเธ” (Worksheet)",
        "๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ (Summary)",
        "๐“ เนเธเธ—เธขเนเธเนเธญเธชเธญเธ (Quiz)"
    ]
    create_type = st.selectbox("เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เธ—เธตเนเธ•เนเธญเธเธเธฒเธฃ:", create_options, key="science_create_type")
    
    # Source dropdown
    source_options = [
        "๐ค– AI เธชเธฃเนเธฒเธเนเธซเน (เธเธฒเธเธซเธฑเธงเธเนเธญ)",
        "๐“ เธเธฒเธเนเธเธฅเน (PDF/Word)",
        "โ๏ธ เธเธฒเธ Prompt (เน€เธเธตเธขเธเน€เธญเธ)"
    ]
    source_type = st.selectbox("เน€เธฅเธทเธญเธเธงเธดเธเธตเธชเธฃเนเธฒเธ:", source_options, key="science_source")
    
    # ==== AI SOURCE (TOPIC) ====
    if "AI เธชเธฃเนเธฒเธเนเธซเน" in source_type:
        # Topic selection
        science_topic_options = [f"{prefix} {name}" for prefix, name, _ in science_topics_list]
        science_topic_select = st.selectbox("๐“– เน€เธฅเธทเธญเธเธซเธฑเธงเธเนเธญ:", science_topic_options, key="science_topic")
        
        # Get selected topic details
        selected_science_topic = None
        for prefix, name, topic_type in science_topics_list:
            full_name = f"{prefix} {name}"
            if full_name == science_topic_select:
                clean_name = name.replace(" ๐", "")
                selected_science_topic = clean_name
                selected_science_type = topic_type
                break
        
        # Show num_q only if not summary
        num_q = 10
        if "เธชเธฃเธธเธ" not in create_type:
            num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=10, key="science_num")
        
        # Generate button
        if st.button("๐€ เธชเธฃเนเธฒเธเธเธฒเธ AI", type="primary", key="science_ai_gen"):
            if not st.session_state.api_key:
                st.warning("โ ๏ธ เธ•เนเธญเธเนเธเน API Key เธเนเธฐ!")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธ..."):
                    if "เธชเธฃเธธเธ" in create_type:
                        # Generate summary
                        summary_prompt = f"เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒเธงเธดเธ—เธขเธฒเธจเธฒเธชเธ•เธฃเนเน€เธฃเธทเนเธญเธ {selected_science_topic} เธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธเธฃเธฐเธ”เธฑเธ {science_grade}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        pdf = generator.create_summary_pdf(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result)
                        
                        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธชเธฃเธธเธ", expanded=True):
                            st.markdown("### ๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ")
                            st.write(summary_result)
                        
                        st.success("โ… เธชเธฃเนเธฒเธเธชเธฃเธธเธเธชเธณเน€เธฃเนเธ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        # Generate worksheet/quiz
                        grade_context = {
                            "เธ.1": "Grade 1 (Thailand IPST Science Curriculum)",
                            "เธ.2": "Grade 2 (Thailand IPST Science Curriculum)",
                            "เธ.3": "Grade 3 (Thailand IPST Science Curriculum)",
                            "เธ.4": "Grade 4 (Thailand IPST Science Curriculum)",
                            "เธ.5": "Grade 5 (Thailand IPST Science Curriculum)",
                            "เธ.6": "Grade 6 (Thailand IPST Science Curriculum)",
                            "เธก.1": "Grade 7 / Matthayom 1 (Thailand IPST Science Curriculum)",
                            "เธก.2": "Grade 8 / Matthayom 2 (Thailand IPST Science Curriculum)",
                            "เธก.3": "Grade 9 / Matthayom 3 (Thailand IPST Science Curriculum)",
                        }
                        
                        # Generate based on grade/subject
                        if science_grade in ["เธก.4", "เธก.5", "เธก.6"]:
                            if subject_key == "เน€เธเธกเธต":
                                questions, answers = generator.generate_chemistry_worksheet(selected_science_topic, science_grade, num_q)
                            elif subject_key == "เธเธดเธชเธดเธเธชเน":
                                questions, answers = generator.generate_physics_worksheet(selected_science_topic, science_grade, num_q)
                            elif subject_key == "เธเธตเธงเธงเธดเธ—เธขเธฒ":
                                questions, answers = generator.generate_biology_worksheet(selected_science_topic, science_grade, num_q)
                            else:
                                questions, answers = generator.generate_science_worksheet(selected_science_topic, science_grade, num_q)
                        else:
                            questions, answers = generator.generate_science_worksheet(selected_science_topic, grade_context.get(science_grade, science_grade), num_q)
                        
                        pdf = generator.create_pdf(title, school_name, selected_science_topic, questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, selected_science_topic, questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "science_worksheet"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    
    # ==== FILE SOURCE ====
    elif "เนเธเธฅเน" in source_type:
        uploaded_file = st.file_uploader("๐“ เธญเธฑเธเนเธซเธฅเธ”เนเธเธฅเน (PDF เธซเธฃเธทเธญ Word)", type=["pdf", "docx", "doc"], key="science_file")
        
        if uploaded_file:
            with st.spinner("๐“– เธเธณเธฅเธฑเธเธญเนเธฒเธเนเธเธฅเน..."):
                file_content = generator.extract_text_from_file(uploaded_file)
                if file_content and "Error" not in file_content:
                    st.success(f"โ… เธญเนเธฒเธเนเธเธฅเนเธชเธณเน€เธฃเนเธ! ({len(file_content)} เธ•เธฑเธงเธญเธฑเธเธฉเธฃ)")
        
        num_q = 10
        if "เธชเธฃเธธเธ" not in create_type:
            num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=10, key="science_file_num")
        
        if st.button("๐€ เธชเธฃเนเธฒเธเธเธฒเธเนเธเธฅเน", type="primary", key="science_file_gen"):
            if not uploaded_file:
                st.warning("โ ๏ธ เธเธฃเธธเธ“เธฒเธญเธฑเธเนเธซเธฅเธ”เนเธเธฅเนเธเนเธญเธเธเนเธฐ!")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธ..."):
                    summarized = generator.summarize_text(file_content, max_length=2000)
                    
                    if "เธชเธฃเธธเธ" in create_type:
                        pdf = generator.create_summary_pdf(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summarized, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summarized)
                        
                        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธชเธฃเธธเธ", expanded=True):
                            st.markdown("### ๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ")
                            st.write(summarized)
                        
                        st.success("โ… เธชเธฃเนเธฒเธเธชเธฃเธธเธเธชเธณเน€เธฃเนเธ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_quiz_from_text(summarized, num_q)
                        
                        pdf = generator.create_pdf(title, school_name, "Quiz from File", questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, "Quiz from File", questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "science_quiz"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    
    # ==== PROMPT SOURCE ====
    elif "Prompt" in source_type:
        prompt_input = st.text_area("๐“ เน€เธเธตเธขเธเธซเธฑเธงเธเนเธญเธซเธฃเธทเธญเน€เธเธทเนเธญเธซเธฒเธ—เธตเนเธ•เนเธญเธเธเธฒเธฃ:", height=100, key="science_prompt")
        
        num_q = 10
        if "เธชเธฃเธธเธ" not in create_type:
            num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=10, key="science_prompt_num")
        
        if st.button("๐€ เธชเธฃเนเธฒเธเธเธฒเธ Prompt", type="primary", key="science_prompt_gen"):
            if not prompt_input:
                st.warning("โ ๏ธ เธเธฃเธธเธ“เธฒเน€เธเธตเธขเธเธซเธฑเธงเธเนเธญเธเนเธญเธเธเนเธฐ!")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธ..."):
                    if "เธชเธฃเธธเธ" in create_type:
                        summary_prompt = f"เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒเธงเธดเธ—เธขเธฒเธจเธฒเธชเธ•เธฃเนเธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธเธฃเธฐเธ”เธฑเธ {science_grade}\n\nเน€เธเธทเนเธญเธซเธฒ:\n{prompt_input}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        pdf = generator.create_summary_pdf(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result)
                        
                        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธชเธฃเธธเธ", expanded=True):
                            st.markdown("### ๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ")
                            st.write(summary_result)
                        
                        st.success("โ… เธชเธฃเนเธฒเธเธชเธฃเธธเธเธชเธณเน€เธฃเนเธ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_quiz_from_text(prompt_input, num_q)
                        
                        pdf = generator.create_pdf(title, school_name, "Quiz from Prompt", questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, "Quiz from Prompt", questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "science_quiz"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    
    # Show preview for summary (non-generated)
    # handled in preview section below# Show preview and download buttons if content is generated
    if st.session_state.generated_pdf is not None and st.session_state.get("generated_filename") == "science_worksheet":
        st.success("โ… เธชเธฃเนเธฒเธเนเธเธเธฒเธเธงเธดเธ—เธขเธฒเธจเธฒเธชเธ•เธฃเนเธชเธณเน€เธฃเนเธ!")
        
        # Preview section
        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธณเธ–เธฒเธกเนเธฅเธฐเน€เธเธฅเธข", expanded=True):
            st.markdown("### ๐“ เธเธณเธ–เธฒเธก / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_questions) - 10} เธเนเธญ")
            
            st.markdown("### โ… เน€เธเธฅเธข / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_answers) - 10} เธเนเธญ")
        
        c1, c2 = st.columns(2)
        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("๐—‘๏ธ เธฅเนเธฒเธเนเธฅเธฐเธชเธฃเนเธฒเธเนเธซเธกเน"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "เธ เธฒเธฉเธฒเนเธ—เธข" in mode_select:
    st.subheader("๐“ เธชเธฃเนเธฒเธเนเธเธเธฒเธเธ เธฒเธฉเธฒเนเธ—เธข (เธ•เธฒเธกเธซเธฅเธฑเธเธชเธนเธ•เธฃเธเธฃเธฐเธ—เธฃเธงเธเธจเธถเธเธฉเธฒเธเธดเธเธฒเธฃ)")
    
    # Thai Language Curriculum Data
    thai_topics = {
        # ===== เธฃเธฐเธ”เธฑเธเธเธฃเธฐเธ–เธกเธจเธถเธเธฉเธฒ =====
        "เธ.1": [
            ("1๏ธโฃ", "เธ•เธฑเธงเธญเธฑเธเธฉเธฃเนเธ—เธข (เธเธขเธฑเธเธเธเธฐเนเธ—เธข 44 เธ•เธฑเธง, เธชเธฃเธฐ 32 เธฃเธนเธ)", "ai"),
            ("2๏ธโฃ", "เธชเธฃเธฐเนเธเธ เธฒเธฉเธฒเนเธ—เธข (เธชเธฃเธฐเน€เธ”เธตเนเธขเธง, เธชเธฃเธฐเธเธฃเธฐเธชเธก)", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเธญเนเธฒเธเธญเธญเธเน€เธชเธตเธขเธ (เธญเนเธฒเธเธเธฒเธเธงเธฃเธฃเธ“เธขเธธเธเธ•เน)", "ai"),
            ("4๏ธโฃ", "เธเธณเธจเธฑเธเธ—เนเธเธทเนเธเธเธฒเธ (เธเธณเธชเธดเนเธเธเธญเธ, เธเธณเธชเธฑเธ•เธงเน, เธเธณเธเธฃเธญเธเธเธฃเธฑเธง)", "ai"),
            ("5๏ธโฃ", "เธเธฃเธฐเนเธขเธเนเธฅเธฐเน€เธฃเธทเนเธญเธเธชเธฑเนเธ (เธเธฃเธฐเนเธขเธเธชเธฑเนเธ, เธเธดเธ—เธฒเธเธชเธฑเนเธ)", "ai"),
        ],
        "เธ.2": [
            ("1๏ธโฃ", "เธเธณเนเธฅเธฐเธเธงเธฒเธกเธซเธกเธฒเธข (เธเธณเธเนเธณ, เธเธณเธ•เธฃเธเธเนเธฒเธก, เธเธณเธเนเธญเธ)", "ai"),
            ("2๏ธโฃ", "เธซเธเนเธงเธขเธเธณเธชเธฃเธฃเธเธเธฒเธก (เธชเธฃเธฃเธเธเธฒเธก, เธเธณเธชเธฃเธฃเธเธเธฒเธกเธชเธฃเธฃเธเธเธธเธฃเธ“)", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธ (เน€เธเธตเธขเธเธ•เธฒเธกเธเธณเธเธญเธ, เน€เธเธตเธขเธเธเธฃเธฐเนเธขเธ)", "ai"),
            ("4๏ธโฃ", "เธเธดเธ—เธฒเธเธเธทเนเธเธเนเธฒเธ (เธเธดเธ—เธฒเธเธเธฒเธ”เธ, เธเธดเธ—เธฒเธเธเธทเนเธเธเนเธฒเธเนเธ—เธข)", "ai"),
            ("5๏ธโฃ", "เธเธฒเธฃเธญเนเธฒเธเธเธฑเธเนเธเธเธงเธฒเธก (เธญเนเธฒเธเน€เธฃเธทเนเธญเธเธชเธฑเนเธ, เธ•เธญเธเธเธณเธ–เธฒเธก)", "ai"),
        ],
        "เธ.3": [
            ("1๏ธโฃ", "เธเธเธดเธ”เธเธญเธเธเธณ (เธเธณเธเธฒเธก, เธเธณเธเธฃเธดเธขเธฒ, เธเธณเธเธธเธ“เธจเธฑเธเธ—เน)", "ai"),
            ("2๏ธโฃ", "เธเธฅเธญเธเนเธเธ” (เนเธเธฃเธเธชเธฃเนเธฒเธเธเธฅเธญเธเนเธเธ”, เธเธณเธเธฃเธธ-เธฅเธซเธธ)", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเน€เธฃเธตเธขเธเธเธงเธฒเธก (เน€เธเธตเธขเธเน€เธฃเธตเธขเธเธเธงเธฒเธกเธชเธฑเนเธ)", "ai"),
            ("4๏ธโฃ", "เธเธณเธฃเธฒเธเธฒเธจเธฑเธเธ—เนเน€เธเธทเนเธญเธเธ•เนเธ (เธเธณเธเธถเนเธเธ•เนเธ-เธฅเธเธ—เนเธฒเธข)", "ai"),
            ("5๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเนเธ—เธข (เธเธธเธเธเนเธฒเธเธเธธเธเนเธเธ, เธชเธธเธ เธฒเธฉเธดเธ•เนเธ—เธข)", "ai"),
        ],
        "เธ.4": [
            ("1๏ธโฃ", "เธซเธเนเธงเธขเธเธณเนเธฅเธฐเธเธงเธฒเธกเธซเธกเธฒเธข (เธเธณเธ เธฒเธฉเธฒเธ•เนเธฒเธเธเธฃเธฐเน€เธ—เธจ, เธเธณเธขเธทเธก)", "ai"),
            ("2๏ธโฃ", "เธเธเธดเธ”เธเธญเธเธเธณ (เธเธณเธชเธฃเธฃเธเธเธฒเธก, เธเธณเธชเธฑเธเธเธฒเธ, เธเธณเธเธธเธเธเธ—)", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเธญเนเธฒเธเธ•เธตเธเธงเธฒเธก (เธญเนเธฒเธเธเธ—เธเธงเธฒเธก, เธญเนเธฒเธเธเนเธฒเธง)", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเธเธ”เธซเธกเธฒเธข (เธเธ”เธซเธกเธฒเธขเธเธญเธเธเธธเธ“, เธเธ”เธซเธกเธฒเธขเน€เธเธดเธ)", "ai"),
            ("5๏ธโฃ", "เธเธฅเธญเธเธชเธธเธ เธฒเธ (เนเธเธฃเธเธชเธฃเนเธฒเธเธเธฅเธญเธเธชเธธเธ เธฒเธ)", "ai"),
        ],
        "เธ.5": [
            ("1๏ธโฃ", "เธเธฃเธฐเนเธขเธเนเธฅเธฐเธญเธเธเนเธเธฃเธฐเธเธญเธ (เธญเธเธเนเธเธฃเธฐเนเธขเธ, เธเธเธดเธ”เธเธญเธเธเธฃเธฐเนเธขเธ)", "ai"),
            ("2๏ธโฃ", "เธงเธฅเธตเนเธฅเธฐเธญเธเธธเธเธฃเธฐเนเธขเธ (เธงเธฅเธตเธเธฒเธก, เธงเธฅเธตเธเธฃเธดเธขเธฒ)", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเธฃเธฒเธขเธเธฒเธ (เธฃเธฒเธขเธเธฒเธเธเธฒเธฃเธจเธถเธเธฉเธฒ, เธฃเธฒเธขเธเธฒเธเธเนเธฒเธง)", "ai"),
            ("4๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเธชเธธเธเธ—เธฃเธตเธขเธ เธฒเธ (เธเธฒเธเธขเนเธเธฅเธญเธเธเธ—เธฃเนเธญเธขเธเธฃเธญเธ)", "ai"),
            ("5๏ธโฃ", "เธ เธฒเธฉเธฒเธ–เธดเนเธ (เธ เธฒเธฉเธฒเธญเธตเธชเธฒเธ, เธ เธฒเธฉเธฒเน€เธซเธเธทเธญ, เธ เธฒเธฉเธฒเนเธ•เน)", "ai"),
        ],
        "เธ.6": [
            ("1๏ธโฃ", "เธซเธฅเธฑเธเธเธฒเธฃเนเธเนเธเธณ (เธเธณเธฃเธฒเธเธฒเธจเธฑเธเธ—เน, เธเธณเธชเธธเธ เธฒเธ)", "ai"),
            ("2๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเน€เธเธดเธเธชเธฃเนเธฒเธเธชเธฃเธฃเธเน (เน€เธฃเธตเธขเธเธเธงเธฒเธก, เธเธดเธ—เธฒเธเธชเธฑเนเธ)", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเธญเนเธฒเธเธงเธดเน€เธเธฃเธฒเธฐเธซเน (เธงเธดเน€เธเธฃเธฒเธฐเธซเนเน€เธฃเธทเนเธญเธ, เธงเธดเน€เธเธฃเธฒเธฐเธซเนเธเนเธฒเธง)", "ai"),
            ("4๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเธงเธฃเธฃเธ“เธเธฃเธฃเธก (เธงเธฃเธฃเธ“เธเธฃเธฃเธกเธฃเธฐเธ”เธฑเธเธเธฒเธ•เธด)", "ai"),
            ("5๏ธโฃ", "เธเธฒเธฃเธเธณเน€เธชเธเธญ (เธเธฒเธฃเธเธนเธ”, เธเธฒเธฃเธเธณเน€เธชเธเธญเธเนเธญเธกเธนเธฅ)", "ai"),
        ],
        
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒเธ•เธญเธเธ•เนเธ =====
        "เธก.1": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธซเธเนเธงเธขเธเธณเธชเธฃเธฃเธเธเธฒเธก (เธเธฒเธฃเนเธเนเธชเธฃเธฃเธเธเธฒเธกเนเธเธเธฃเธดเธเธ—เธ•เนเธฒเธเน)", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเน€เธเธฅเธตเนเธขเธเธฃเธนเธเธเธณ (เธเธฒเธฃเธเธฑเธเธเธณเธเธฃเธดเธขเธฒ, เธเธฒเธฃเธฅเธ”เธฃเธนเธเธเธณ)", "ai"),
                ("3๏ธโฃ", "เธงเธฅเธตเนเธฅเธฐเธญเธเธธเธเธฃเธฐเนเธขเธ (เธงเธฅเธตเธเธขเธฒเธข, เธญเธเธธเธเธฃเธฐเนเธขเธ)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธต (เธฃเนเธญเธขเธเธฃเธญเธเนเธ—เธข, เธเธฒเธเธขเนเธขเธฒเธเน€เธญเธ)", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเธญเนเธฒเธ-เน€เธเธตเธขเธ (เธญเนเธฒเธเธเธ—เธเธงเธฒเธก, เน€เธเธตเธขเธเน€เธฃเธตเธขเธเธเธงเธฒเธก)", "ai"),
            ]
        },
        "เธก.2": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธเธณเนเธฅเธฐเธเธฃเธฐเนเธขเธเธเนเธญเธ (เธเธฃเธฐเนเธขเธเธเนเธญเธ, เธเธฃเธฐเนเธขเธเธเนเธญเธเธเธฅเธ)", "ai"),
                ("2๏ธโฃ", "เธเธฅเธญเธเนเธเธ”-เธเธฅเธญเธเธชเธธเธ เธฒเธ (เธเธฒเธฃเนเธ•เนเธเธเธฅเธญเธ, เธชเธฑเธกเธเธฑเธชเธเธฅเธญเธ)", "ai"),
                ("3๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเธญเธตเธชเธฒเธ (เธฅเธดเน€เธ, เนเธเธ, เธซเธเธฑเธเนเธซเธเน)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเน€เธเธดเธเธชเธฃเนเธฒเธเธชเธฃเธฃเธเน (เน€เธเธตเธขเธเธเธดเธขเธฒเธขเธชเธฑเนเธ, เธเธ—เธฅเธฐเธเธฃ)", "ai"),
                ("2๏ธโฃ", "เธ เธฒเธฉเธฒเธ–เธดเนเธเนเธฅเธฐเธ เธฒเธฉเธฒเธเธฅเธฒเธ (เธเธงเธฒเธกเนเธ•เธเธ•เนเธฒเธ, เธเธฒเธฃเนเธเน)", "ai"),
            ]
        },
        "เธก.3": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธ เธฒเธฉเธฒเธเธฑเธเธชเธฑเธเธเธก (เธ เธฒเธฉเธฒเนเธฅเธฐเธญเธณเธเธฒเธ, เธ เธฒเธฉเธฒเนเธฅเธฐเน€เธเธจเธชเธ เธฒเธ)", "ai"),
                ("2๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเนเธ—เธข (เธเธดเธ—เธฒเธเธฃเธฒเธกเน€เธเธตเธขเธฃเธ•เธดเน, เธเธธเธเธเนเธฒเธเธเธธเธเนเธเธ)", "ai"),
                ("3๏ธโฃ", "เธเธฒเธฃเธญเนเธฒเธเธงเธดเธเธฒเธเธฉเน (เธงเธดเธเธฒเธเธฉเนเธเธ—เธเธงเธฒเธก, เธงเธดเธเธฒเธเธฉเนเธเนเธฒเธง)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเธงเธดเธเธฒเธเธฒเธฃ (เธฃเธฒเธขเธเธฒเธเธงเธดเธเธฑเธข, เธเธ—เธเธงเธฒเธกเธงเธดเธเธฒเธเธฒเธฃ)", "ai"),
                ("2๏ธโฃ", "เธงเธฒเธ—เธตเธงเธดเธ—เธขเธฒ (เธเธฒเธฃเนเธ•เนเนเธขเนเธ, เธเธฒเธฃเน€เธเธตเธขเธเธเนเธญเน€เธชเธเธญ)", "ai"),
            ]
        },
        
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒเธ•เธญเธเธเธฅเธฒเธข =====
        "เธก.4": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธ เธฒเธฉเธฒเธเธฑเธเธเธฒเธฃเธชเธทเนเธญเธชเธฒเธฃ (เธ เธฒเธฉเธฒเนเธเธญเธเธเนเธเธฃ, เธ เธฒเธฉเธฒเธเธธเธฃเธเธดเธ)", "ai"),
                ("2๏ธโฃ", "เธซเธฅเธฑเธเธ เธฒเธฉเธฒเนเธ—เธข (เธ—เธคเธฉเธเธตเธ เธฒเธฉเธฒ, เธ เธฒเธฉเธฒเธเธฑเธเธเธงเธฒเธกเธเธดเธ”)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเธฃเนเธงเธกเธชเธกเธฑเธข (เธเธดเธขเธฒเธขเนเธ—เธขเธฃเนเธงเธกเธชเธกเธฑเธข)", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเน€เธเธดเธเธงเธดเธเธฒเธเธฒเธฃ (เธเธ—เธเธงเธฒเธกเธงเธดเน€เธเธฃเธฒเธฐเธซเน)", "ai"),
                ("3๏ธโฃ", "เธชเธทเนเธญเนเธฅเธฐเธ เธฒเธฉเธฒ (เธ เธฒเธฉเธฒเนเธเธฉเธ“เธฒ, เธ เธฒเธฉเธฒเธชเธทเนเธญ)", "ai"),
            ]
        },
        "เธก.5": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเนเธ—เธขเนเธฅเธฐเธญเธฒเน€เธเธตเธขเธ (เธงเธฃเธฃเธ“เธเธ”เธตเธญเธฒเน€เธเธตเธขเธ)", "ai"),
                ("2๏ธโฃ", "เธ เธฒเธฉเธฒเนเธฅเธฐเธงเธฑเธ’เธเธเธฃเธฃเธก (เธ เธฒเธฉเธฒเธเธฑเธเธงเธฑเธ’เธเธเธฃเธฃเธกเนเธ—เธข)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธเธฒเธฃเธเธณเน€เธชเธเธญ (เธเธฒเธฃเธเธนเธ”เนเธเธ—เธตเนเธชเธฒเธเธฒเธฃเธ“เธฐ)", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเธชเธฃเนเธฒเธเธชเธฃเธฃเธเน (เธเธ—เธฅเธฐเธเธฃ, เธเธ—เธ เธฒเธเธขเธเธ•เธฃเน)", "ai"),
                ("3๏ธโฃ", "เธงเธฒเธ—เธตเธงเธดเธ—เธขเธฒ (เธเธฒเธฃเนเธ•เนเธงเธฒเธ—เธต, เธเธฒเธฃเน€เธเธตเธขเธเธเนเธญเน€เธชเธเธญ)", "ai"),
            ]
        },
        "เธก.6": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "เธ เธฒเธฉเธฒเธเธฑเธเน€เธ—เธเนเธเนเธฅเธขเธต (เธ เธฒเธฉเธฒเธญเธดเธเน€เธ—เธญเธฃเนเน€เธเนเธ•, เธ เธฒเธฉเธฒเนเธเน€เธเธตเธขเธฅ)", "ai"),
                ("2๏ธโฃ", "เธ เธฒเธฉเธฒเนเธฅเธฐเธญเธฒเธเธตเธ (เธ เธฒเธฉเธฒเธชเธณเธซเธฃเธฑเธเธญเธฒเธเธตเธเธ•เนเธฒเธเน)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "เธงเธฃเธฃเธ“เธเธ”เธตเนเธฅเธฐเธ เธฒเธเธขเธเธ•เธฃเน (เธเธฒเธฃเธ”เธฑเธ”เนเธเธฅเธเธงเธฃเธฃเธ“เธเธ”เธต)", "ai"),
                ("2๏ธโฃ", "เธเธฒเธฃเน€เธเธตเธขเธเน€เธเธทเนเธญเธชเธทเนเธญเธชเธฒเธฃ (เธเธ—เธเธงเธฒเธกเธชเธฒเธฃเธเธ”เธต)", "ai"),
                ("3๏ธโฃ", "เธเธฒเธฃเธเธฃเธฐเน€เธกเธดเธเธเธฅเธเธฒเธเธ เธฒเธฉเธฒ (เธเธฒเธฃเธงเธดเธเธฒเธฃเธ“เน, เธเธฒเธฃเธเธฃเธฐเน€เธกเธดเธ)", "ai"),
            ]
        },
    }
    
    # ==== DROPDOWN STRUCTURE ====
    # Create type dropdown
    create_options = [
        "๐“ เนเธเธเธฒเธ / เนเธเธเธเธถเธเธซเธฑเธ” (Worksheet)",
        "๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ (Summary)",
        "๐“ เนเธเธ—เธขเนเธเนเธญเธชเธญเธ (Quiz)"
    ]
    create_type = st.selectbox("เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เธ—เธตเนเธ•เนเธญเธเธเธฒเธฃ:", create_options, key="thai_create_type")
    
    # Source dropdown
    source_options = [
        "๐ค– AI เธชเธฃเนเธฒเธเนเธซเน (เธเธฒเธเธซเธฑเธงเธเนเธญ)",
        "๐“ เธเธฒเธเนเธเธฅเน (PDF/Word)",
        "โ๏ธ เธเธฒเธ Prompt (เน€เธเธตเธขเธเน€เธญเธ)"
    ]
    source_type = st.selectbox("เน€เธฅเธทเธญเธเธงเธดเธเธตเธชเธฃเนเธฒเธ:", source_options, key="thai_source")
    
    # Grade Selection
    thai_grade_options = ["เธ.1", "เธ.2", "เธ.3", "เธ.4", "เธ.5", "เธ.6", "เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]
    thai_grade_select = st.selectbox("๐“ เน€เธฅเธทเธญเธเธฃเธฐเธ”เธฑเธเธเธฑเนเธ:", thai_grade_options)
    
    # Check if grade is เธก.1-6 (has terms)
    if thai_grade_select in ["เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]:
        thai_term_options = list(thai_topics[thai_grade_select].keys())
        thai_term_select = st.selectbox("๐“… เน€เธฅเธทเธญเธเน€เธ—เธญเธก:", thai_term_options)
        thai_topics_list = thai_topics[thai_grade_select][thai_term_select]
        selected_thai_grade = thai_grade_select
    else:
        thai_topics_list = thai_topics.get(thai_grade_select, [])
        selected_thai_grade = thai_grade_select
    
    # Topic selection
    thai_topic_options = [f"{prefix} {name}" for prefix, name, _ in thai_topics_list]
    thai_topic_select = st.selectbox("๐“– เน€เธฅเธทเธญเธเธซเธฑเธงเธเนเธญ:", thai_topic_options)
    
    selected_thai_topic = None
    for prefix, name, topic_type in thai_topics_list:
        full_name = f"{prefix} {name}"
        if full_name == thai_topic_select:
            selected_thai_topic = name
            break
    
    # ==== AI SOURCE ====
    if "AI เธชเธฃเนเธฒเธเนเธซเน" in source_type:
        st.info("๐“ เธซเธฑเธงเธเนเธญเธ เธฒเธฉเธฒเนเธ—เธขเนเธเน AI เนเธเธเธฒเธฃเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธเนเธฐ")
        
        exercise_types = [
            "เธ—เธฑเนเธเธซเธกเธ” (เธเธชเธกเธเธชเธฒเธ)",
            "เธเธฒเธฃเน€เธเธตเธขเธ (Writing Exercises)",
            "เธเธฒเธฃเธญเนเธฒเธ (Reading Comprehension)",
            "เธซเธฅเธฑเธเธ เธฒเธฉเธฒ (Grammar Exercises)",
            "เธเธณเธจเธฑเธเธ—เน (Vocabulary)",
            "เธงเธฃเธฃเธ“เธเธ”เธต (Literature)"
        ]
        exercise_type = st.selectbox("๐“ เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เนเธเธเธเธถเธเธซเธฑเธ”:", exercise_types)
        
        num_q = 10
        if "เธชเธฃเธธเธ" not in create_type:
            num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=10)
        
        if st.button("๐€ เธชเธฃเนเธฒเธเธเธฒเธ AI", type="primary", key="thai_ai_gen"):
            if not st.session_state.api_key:
                st.warning("โ ๏ธ เธ•เนเธญเธเนเธเน API Key เธเนเธฐ!")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธ..."):
                    if "เธชเธฃเธธเธ" in create_type:
                        summary_prompt = f"เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒเธ เธฒเธฉเธฒเนเธ—เธขเน€เธฃเธทเนเธญเธ {selected_thai_topic} เธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธเธฃเธฐเธ”เธฑเธ {thai_grade_select}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        pdf = generator.create_summary_pdf(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result)
                        
                        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธชเธฃเธธเธ", expanded=True):
                            st.markdown("### ๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ")
                            st.write(summary_result)
                        
                        st.success("โ… เธชเธฃเนเธฒเธเธชเธฃเธธเธเธชเธณเน€เธฃเนเธ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_thai_worksheet(selected_thai_topic, thai_grade_select, num_q, "mix")
                        
                        pdf = generator.create_pdf(title, school_name, selected_thai_topic, questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, selected_thai_topic, questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "thai_worksheet"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    
    # ==== FILE SOURCE ====
    elif "เนเธเธฅเน" in source_type:
        uploaded_file = st.file_uploader("๐“ เธญเธฑเธเนเธซเธฅเธ”เนเธเธฅเน (PDF เธซเธฃเธทเธญ Word)", type=["pdf", "docx", "doc"], key="thai_file")
        
        if uploaded_file:
            with st.spinner("๐“– เธเธณเธฅเธฑเธเธญเนเธฒเธเนเธเธฅเน..."):
                file_content = generator.extract_text_from_file(uploaded_file)
                if file_content and "Error" not in file_content:
                    st.success(f"โ… เธญเนเธฒเธเนเธเธฅเนเธชเธณเน€เธฃเนเธ! ({len(file_content)} เธ•เธฑเธงเธญเธฑเธเธฉเธฃ)")
        
        num_q = 10
        if "เธชเธฃเธธเธ" not in create_type:
            num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=10, key="thai_file_num")
        
        if st.button("๐€ เธชเธฃเนเธฒเธเธเธฒเธเนเธเธฅเน", type="primary", key="thai_file_gen"):
            if not uploaded_file:
                st.warning("โ ๏ธ เธเธฃเธธเธ“เธฒเธญเธฑเธเนเธซเธฅเธ”เนเธเธฅเนเธเนเธญเธเธเนเธฐ!")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธ..."):
                    summarized = generator.summarize_text(file_content, max_length=2000)
                    
                    if "เธชเธฃเธธเธ" in create_type:
                        pdf = generator.create_summary_pdf(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summarized, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summarized)
                        
                        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธชเธฃเธธเธ", expanded=True):
                            st.markdown("### ๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ")
                            st.write(summarized)
                        
                        st.success("โ… เธชเธฃเนเธฒเธเธชเธฃเธธเธเธชเธณเน€เธฃเนเธ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_quiz_from_text(summarized, num_q)
                        
                        pdf = generator.create_pdf(title, school_name, "Quiz from File", questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, "Quiz from File", questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "thai_quiz"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    
    # ==== PROMPT SOURCE ====
    elif "Prompt" in source_type:
        prompt_input = st.text_area("๐“ เน€เธเธตเธขเธเธซเธฑเธงเธเนเธญเธซเธฃเธทเธญเน€เธเธทเนเธญเธซเธฒเธ—เธตเนเธ•เนเธญเธเธเธฒเธฃ:", height=100, key="thai_prompt")
        
        num_q = 10
        if "เธชเธฃเธธเธ" not in create_type:
            num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=10, key="thai_prompt_num")
        
        if st.button("๐€ เธชเธฃเนเธฒเธเธเธฒเธ Prompt", type="primary", key="thai_prompt_gen"):
            if not prompt_input:
                st.warning("โ ๏ธ เธเธฃเธธเธ“เธฒเน€เธเธตเธขเธเธซเธฑเธงเธเนเธญเธเนเธญเธเธเนเธฐ!")
            else:
                with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธ..."):
                    if "เธชเธฃเธธเธ" in create_type:
                        summary_prompt = f"เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒเธ เธฒเธฉเธฒเนเธ—เธขเธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธ\n\nเน€เธเธทเนเธญเธซเธฒ:\n{prompt_input}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        pdf = generator.create_summary_pdf(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ", summary_result)
                        
                        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธชเธฃเธธเธ", expanded=True):
                            st.markdown("### ๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ")
                            st.write(summary_result)
                        
                        st.success("โ… เธชเธฃเนเธฒเธเธชเธฃเธธเธเธชเธณเน€เธฃเนเธ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_quiz_from_text(prompt_input, num_q)
                        
                        pdf = generator.create_pdf(title, school_name, "Quiz from Prompt", questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, "Quiz from Prompt", questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "thai_quiz"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
        if not st.session_state.api_key:
            st.info("๐”‘ เธ•เนเธญเธเนเธเน API Key เธชเธณเธซเธฃเธฑเธเธซเธฑเธงเธเนเธญเธ เธฒเธฉเธฒเนเธ—เธขเธเนเธฐ เธเธฃเธญเธ API Key เนเธ”เนเธ—เธตเนเธ”เนเธฒเธเธเธเธเธฐเธเธฐ")
        else:
            with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธ เธฒเธฉเธฒเนเธ—เธข..."):
                # Map exercise type to prompt
                exercise_mapping = {
                    "เธ—เธฑเนเธเธซเธกเธ” (เธเธชเธกเธเธชเธฒเธ)": "mix",
                    "เธเธฒเธฃเน€เธเธตเธขเธ (Writing Exercises)": "writing",
                    "เธเธฒเธฃเธญเนเธฒเธ (Reading Comprehension)": "reading",
                    "เธซเธฅเธฑเธเธ เธฒเธฉเธฒ (Grammar Exercises)": "grammar",
                    "เธเธณเธจเธฑเธเธ—เน (Vocabulary)": "vocabulary",
                    "เธงเธฃเธฃเธ“เธเธ”เธต (Literature)": "literature"
                }
                
                questions, answers = generator.generate_thai_worksheet(
                    selected_thai_topic, 
                    selected_thai_grade,
                    num_q,
                    exercise_mapping.get(exercise_type, "mix")
                )
                
                pdf = generator.create_pdf(title, school_name, selected_thai_topic, questions, answers, qr_url, uploaded_logo)
                word = generator.create_word_doc(title, school_name, selected_thai_topic, questions, answers)
                
                st.session_state.generated_pdf = pdf
                st.session_state.generated_word = word
                st.session_state.generated_filename = "thai_worksheet"
                st.session_state.preview_questions = questions
                st.session_state.preview_answers = answers
    
    # Show preview and download buttons if content is generated
    if st.session_state.generated_pdf is not None and st.session_state.get("generated_filename") == "thai_worksheet":
        st.success("โ… เธชเธฃเนเธฒเธเนเธเธเธฒเธเธ เธฒเธฉเธฒเนเธ—เธขเธชเธณเน€เธฃเนเธ!")
        
        # Preview section
        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธณเธ–เธฒเธกเนเธฅเธฐเน€เธเธฅเธข", expanded=True):
            st.markdown("### ๐“ เธเธณเธ–เธฒเธก / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_questions) - 10} เธเนเธญ")
            
            st.markdown("### โ… เน€เธเธฅเธข / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_answers) - 10} เธเนเธญ")
        
        c1, c2 = st.columns(2)
        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("๐—‘๏ธ เธฅเนเธฒเธเนเธฅเธฐเธชเธฃเนเธฒเธเนเธซเธกเน"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "เธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉ" in mode_select:
    st.subheader("๐ เธชเธฃเนเธฒเธเนเธเธเธฒเธเธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉ (English Language)")
    
    # ==== DROPDOWN STRUCTURE ====
    create_options = [
        "๐“ เนเธเธเธฒเธ / เนเธเธเธเธถเธเธซเธฑเธ” (Worksheet)",
        "๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ (Summary)",
        "๐“ เนเธเธ—เธขเนเธเนเธญเธชเธญเธ (Quiz)"
    ]
    create_type = st.selectbox("เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เธ—เธตเนเธ•เนเธญเธเธเธฒเธฃ:", create_options, key="english_create_type")
    
    source_options = [
        "๐ค– AI เธชเธฃเนเธฒเธเนเธซเน (เธเธฒเธเธซเธฑเธงเธเนเธญ)",
        "๐“ เธเธฒเธเนเธเธฅเน (PDF/Word)",
        "โ๏ธ เธเธฒเธ Prompt (เน€เธเธตเธขเธเน€เธญเธ)"
    ]
    source_type = st.selectbox("เน€เธฅเธทเธญเธเธงเธดเธเธตเธชเธฃเนเธฒเธ:", source_options, key="english_source")
    
    # English Language Curriculum Data
    english_topics = {
        # ===== เธฃเธฐเธ”เธฑเธเธเธฃเธฐเธ–เธกเธจเธถเธเธฉเธฒ =====
        "เธ.1": [
            ("1๏ธโฃ", "Alphabet (A-Z uppercase/lowercase)", "ai"),
            ("2๏ธโฃ", "Phonics (Aa-Zz sounds)", "ai"),
            ("3๏ธโฃ", "Numbers 1-10 (counting)", "ai"),
            ("4๏ธโฃ", "Colors (Red, blue, green, yellow, etc.)", "ai"),
            ("5๏ธโฃ", "Shapes (Circle, square, triangle, etc.)", "ai"),
            ("6๏ธโฃ", "Body Parts (Head, eyes, ears, nose, etc.)", "ai"),
            ("7๏ธโฃ", "Family (Mother, father, sister, brother)", "ai"),
            ("8๏ธโฃ", "Animals (Cat, dog, bird, fish, etc.)", "ai"),
        ],
        "เธ.2": [
            ("1๏ธโฃ", "Numbers 11-100 (counting)", "ai"),
            ("2๏ธโฃ", "Days & Months (Monday-Sunday, Jan-Dec)", "ai"),
            ("3๏ธโฃ", "Time (O'clock, half past)", "ai"),
            ("4๏ธโฃ", "Food & Drinks (Rice, bread, water, milk)", "ai"),
            ("5๏ธโฃ", "Clothing (Shirt, pants, dress, shoes)", "ai"),
            ("6๏ธโฃ", "Weather (Hot, cold, rainy, sunny)", "ai"),
            ("7๏ธโฃ", "Places (School, home, market, hospital)", "ai"),
            ("8๏ธโฃ", "Greetings (Hello, goodbye, thank you)", "ai"),
        ],
        "เธ.3": [
            ("1๏ธโฃ", "Present Simple (I am, you are, he/she is)", "ai"),
            ("2๏ธโฃ", "This-That-These-Those", "ai"),
            ("3๏ธโฃ", "Have-Has (possession)", "ai"),
            ("4๏ธโฃ", "Prepositions (In, on, under, behind)", "ai"),
            ("5๏ธโฃ", "WH-Questions (What, Where, When, Why, Who)", "ai"),
            ("6๏ธโฃ", "Daily Routines (Wake up, eat breakfast)", "ai"),
            ("7๏ธโฃ", "Occupations (Doctor, teacher, farmer)", "ai"),
            ("8๏ธโฃ", "Adjectives (Big, small, tall, beautiful)", "ai"),
        ],
        "เธ.4": [
            ("1๏ธโฃ", "Past Simple (was/were)", "ai"),
            ("2๏ธโฃ", "Regular Verbs (Played, watched, cleaned)", "ai"),
            ("3๏ธโฃ", "Irregular Verbs (Went, ate, drank, saw)", "ai"),
            ("4๏ธโฃ", "Object Pronouns (Me, him, her, us, them)", "ai"),
            ("5๏ธโฃ", "There is-There are", "ai"),
            ("6๏ธโฃ", "Commands (Open the door, close the window)", "ai"),
            ("7๏ธโฃ", "Descriptions (Describing people/things)", "ai"),
            ("8๏ธโฃ", "School Subjects (Math, English, Science, Art)", "ai"),
        ],
        "เธ.5": [
            ("1๏ธโฃ", "Future Will-Going to", "ai"),
            ("2๏ธโฃ", "Present Continuous (am/is/are + verb-ing)", "ai"),
            ("3๏ธโฃ", "Can-Could (ability, permission)", "ai"),
            ("4๏ธโฃ", "Some-Any", "ai"),
            ("5๏ธโฃ", "Telling Time (Quarter past, quarter to)", "ai"),
            ("6๏ธโฃ", "Giving Directions (Turn left, turn right)", "ai"),
            ("7๏ธโฃ", "Invitations (Would you like...?, Let's...)", "ai"),
            ("8๏ธโฃ", "Letter Writing (Formal and informal)", "ai"),
        ],
        "เธ.6": [
            ("1๏ธโฃ", "Tenses Review (Present, Past, Future)", "ai"),
            ("2๏ธโฃ", "Modal Verbs (Must, should, have to, may)", "ai"),
            ("3๏ธโฃ", "Passive Voice (is/are + verb3)", "ai"),
            ("4๏ธโฃ", "If Clauses (Conditionals type 1)", "ai"),
            ("5๏ธโฃ", "Reported Speech (Said, told, asked)", "ai"),
            ("6๏ธโฃ", "Conjunctions (And, but, or, because, so)", "ai"),
            ("7๏ธโฃ", "Reading Comprehension (Passages, questions)", "ai"),
            ("8๏ธโฃ", "Paragraph Writing (3-5 sentences)", "ai"),
        ],
        
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒเธ•เธญเธเธ•เนเธ =====
        "เธก.1": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "Present Perfect (have/has + verb3)", "ai"),
                ("2๏ธโฃ", "Since-For (time expressions)", "ai"),
                ("3๏ธโฃ", "Tag Questions (aren't you?, isn't it?)", "ai"),
                ("4๏ธโฃ", "Relative Clauses (Who, which, that)", "ai"),
                ("5๏ธโฃ", "Gerunds & Infinitives", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "Making Suggestions (Let's, Why don't we)", "ai"),
                ("2๏ธโฃ", "Phone Conversations", "ai"),
                ("3๏ธโฃ", "Shopping & Money", "ai"),
                ("4๏ธโฃ", "Travel & Transportation ๐", "ai"),
                ("5๏ธโฃ", "Health & Fitness ๐", "ai"),
            ]
        },
        "เธก.2": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "Past Continuous (was/were + verb-ing)", "ai"),
                ("2๏ธโฃ", "Future Continuous (will be + verb-ing)", "ai"),
                ("3๏ธโฃ", "Conditionals Type 2 (If I were, I would)", "ai"),
                ("4๏ธโฃ", "Reported Questions", "ai"),
                ("5๏ธโฃ", "Quantifiers (Much, many, a few, a little)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "Comparison (Adjectives, adverbs)", "ai"),
                ("2๏ธโฃ", "Wish Sentences (I wish I could...)", "ai"),
                ("3๏ธโฃ", "Email Writing (Formal and informal)", "ai"),
                ("4๏ธโฃ", "News Writing ๐", "ai"),
                ("5๏ธโฃ", "Story Writing ๐", "ai"),
            ]
        },
        "เธก.3": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "Conditionals All Types (Type 1, 2, 3)", "ai"),
                ("2๏ธโฃ", "Passive Voice (All tenses)", "ai"),
                ("3๏ธโฃ", "Reported Speech (All reporting verbs)", "ai"),
                ("4๏ธโฃ", "Gerunds & Infinitives (Special uses)", "ai"),
                ("5๏ธโฃ", "Modal Perfects (Should have, could have)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "Articles (A, an, the, zero article)", "ai"),
                ("2๏ธโฃ", "Essay Writing (Opinion, comparison)", "ai"),
                ("3๏ธโฃ", "O-NET Preparation (Grammar, vocabulary)", "ai"),
                ("4๏ธโฃ", "Critical Reading ๐", "ai"),
                ("5๏ธโฃ", "Creative Writing ๐", "ai"),
            ]
        },
        
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒเธ•เธญเธเธเธฅเธฒเธข =====
        "เธก.4": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "Narrative Tenses (Past perfect)", "ai"),
                ("2๏ธโฃ", "Future Perfect (will have + verb3)", "ai"),
                ("3๏ธโฃ", "Mixed Conditionals", "ai"),
                ("4๏ธโฃ", "Wish-Remorse (I wish I had...)", "ai"),
                ("5๏ธโฃ", "Linking Words (However, although, despite)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "Paragraph Development", "ai"),
                ("2๏ธโฃ", "Speaking: Opinions (I think, In my opinion)", "ai"),
                ("3๏ธโฃ", "Vocabulary 1500 (Word families, synonyms)", "ai"),
                ("4๏ธโฃ", "Academic Vocabulary ๐", "ai"),
                ("5๏ธโฃ", "Debating Skills ๐", "ai"),
            ]
        },
        "เธก.5": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "Mixed Tenses Review", "ai"),
                ("2๏ธโฃ", "Modal Verbs Review (Must, have to, should)", "ai"),
                ("3๏ธโฃ", "Participle Clauses", "ai"),
                ("4๏ธโฃ", "Passive Voice Review", "ai"),
                ("5๏ธโฃ", "Essay Types (Argumentative, descriptive)", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "Speaking: Debating (Agree/disagree)", "ai"),
                ("2๏ธโฃ", "Listening Skills (News, interviews)", "ai"),
                ("3๏ธโฃโฃ", "Vocabulary 2000 (Idioms, phrasal verbs)", "ai"),
                ("4๏ธโฃ", "Academic Writing ๐", "ai"),
                ("5๏ธโฃ", "Presentation Skills ๐", "ai"),
            ]
        },
        "เธก.6": {
            "เน€เธ—เธญเธก 1": [
                ("1๏ธโฃ", "Advanced Grammar (Inversion, emphasis)", "ai"),
                ("2๏ธโฃ", "Academic Writing (Research, citations)", "ai"),
                ("3๏ธโฃ", "Critical Reading (Analysis, inference)", "ai"),
                ("4๏ธโฃ", "Presentation Skills", "ai"),
            ],
            "เน€เธ—เธญเธก 2": [
                ("1๏ธโฃ", "Test Preparation (O-NET, University entrance)", "ai"),
                ("2๏ธโฃ", "Career English (Resume, interview)", "ai"),
                ("3๏ธโฃ", "Global Issues (Environment, technology)", "ai"),
                ("4๏ธโฃ", "Literature (Poems, short stories)", "ai"),
            ]
        },
    }
    
    # Grade Selection
    english_grade_options = ["เธ.1", "เธ.2", "เธ.3", "เธ.4", "เธ.5", "เธ.6", "เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]
    english_grade_select = st.selectbox("๐“ เน€เธฅเธทเธญเธเธฃเธฐเธ”เธฑเธเธเธฑเนเธ:", english_grade_options)
    
    # Check if grade is เธก.1-6 (has terms)
    if english_grade_select in ["เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]:
        # Select term first
        english_term_options = list(english_topics[english_grade_select].keys())
        english_term_select = st.selectbox("๐“… เน€เธฅเธทเธญเธเน€เธ—เธญเธก:", english_term_options)
        english_topics_list = english_topics[english_grade_select][english_term_select]
        selected_english_grade = english_grade_select
    else:
        # Primary school grades
        english_topics_list = english_topics.get(english_grade_select, [])
        selected_english_grade = english_grade_select
    
    # Topic selection with display names
    english_topic_options = [f"{prefix} {name}" for prefix, name, _ in english_topics_list]
    english_topic_select = st.selectbox("๐“– เน€เธฅเธทเธญเธเธซเธฑเธงเธเนเธญ:", english_topic_options)
    
    # Get selected topic details
    selected_english_topic = None
    for prefix, name, topic_type in english_topics_list:
        full_name = f"{prefix} {name}"
        if full_name == english_topic_select:
            # Remove ๐ for backend
            clean_name = name.replace(" ๐", "")
            selected_english_topic = clean_name
            break
    
    # Show AI requirement message only once
    st.info("๐“ เธซเธฑเธงเธเนเธญเธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉเธ—เธฑเนเธเธซเธกเธ”เธ•เนเธญเธเนเธเน AI เนเธเธเธฒเธฃเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธเนเธฐ")
    
    # Exercise type selector
    exercise_types = [
        "เธ—เธฑเนเธเธซเธกเธ” (เธเธชเธกเธเธชเธฒเธ - All Types)",
        "เนเธงเธขเธฒเธเธฃเธ“เน (Grammar Exercises)",
        "เธเธณเธจเธฑเธเธ—เน (Vocabulary)",
        "เธเธฒเธฃเธญเนเธฒเธ (Reading Comprehension)",
        "เธเธฒเธฃเน€เธเธตเธขเธ (Writing)",
        "เธเธฒเธฃเธเธฑเธ (Listening Scripts)",
        "เธเธฒเธฃเธเธนเธ” (Speaking Prompts)"
    ]
    exercise_type = st.selectbox("๐“ เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เนเธเธเธเธถเธเธซเธฑเธ”:", exercise_types)
    
    num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=20)
    
    # Custom Prompt Section
    with st.expander("โ๏ธ เธเธฃเธฑเธเนเธ•เนเธ Prompt (เนเธกเนเธเธฑเธเธเธฑเธ)", expanded=False):
        english_prompt = st.text_area(
            "Prompt เธชเธณเธซเธฃเธฑเธ AI (เธ–เนเธฒเน€เธงเนเธเธงเนเธฒเธเธเธฐเนเธเนเธเนเธฒเน€เธฃเธดเนเธกเธ•เนเธ)",
            value="",
            height=100,
            help="เธเธฃเธฑเธเนเธ•เนเธ prompt เน€เธเธทเนเธญเนเธซเนเนเธ”เนเธเธฅเธฅเธฑเธเธเนเธ•เธฒเธกเธ•เนเธญเธเธเธฒเธฃ"
        )
        
        st.markdown("**๐’ก เธ•เธฑเธงเธญเธขเนเธฒเธ Prompt เธ—เธตเนเธ”เธต:**")
        st.code("Create 10 English grammar exercises about Past Tense for Prathom 3 students. Include fill-in-the-blank, multiple choice, and sentence transformation exercises with answers.", language="text")
    
    if st.button("๐€ เธชเธฃเนเธฒเธเนเธเธเธฒเธเธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉ", type="primary"):
        if not st.session_state.api_key:
            st.info("๐”‘ เธ•เนเธญเธเนเธเน API Key เธชเธณเธซเธฃเธฑเธเธซเธฑเธงเธเนเธญเธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉเธเนเธฐ เธเธฃเธญเธ API Key เนเธ”เนเธ—เธตเนเธ”เนเธฒเธเธเธเธเธฐเธเธฐ")
        else:
            with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉ..."):
                # Map exercise type to prompt
                exercise_mapping = {
                    "เธ—เธฑเนเธเธซเธกเธ” (เธเธชเธกเธเธชเธฒเธ - All Types)": "mix",
                    "เนเธงเธขเธฒเธเธฃเธ“เน (Grammar Exercises)": "grammar",
                    "เธเธณเธจเธฑเธเธ—เน (Vocabulary)": "vocabulary",
                    "เธเธฒเธฃเธญเนเธฒเธ (Reading Comprehension)": "reading",
                    "เธเธฒเธฃเน€เธเธตเธขเธ (Writing)": "writing",
                    "เธเธฒเธฃเธเธฑเธ (Listening Scripts)": "listening",
                    "เธเธฒเธฃเธเธนเธ” (Speaking Prompts)": "speaking"
                }
                
                questions, answers = generator.generate_english_worksheet(
                    selected_english_topic, 
                    selected_english_grade,
                    num_q,
                    exercise_mapping.get(exercise_type, "mix")
                )
                
                pdf = generator.create_pdf(title, school_name, selected_english_topic, questions, answers, qr_url, uploaded_logo)
                word = generator.create_word_doc(title, school_name, selected_english_topic, questions, answers)
                
                st.session_state.generated_pdf = pdf
                st.session_state.generated_word = word
                st.session_state.generated_filename = "english_worksheet"
                st.session_state.preview_questions = questions
                st.session_state.preview_answers = answers
    
    # Show preview and download buttons if content is generated
    if st.session_state.generated_pdf is not None and st.session_state.get("generated_filename") == "english_worksheet":
        st.success("โ… เธชเธฃเนเธฒเธเนเธเธเธฒเธเธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉเธชเธณเน€เธฃเนเธ!")
        
        # Preview section
        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธณเธ–เธฒเธกเนเธฅเธฐเน€เธเธฅเธข", expanded=True):
            st.markdown("### ๐“ เธเธณเธ–เธฒเธก / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_questions) - 10} เธเนเธญ")
            
            st.markdown("### โ… เน€เธเธฅเธข / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_answers) - 10} เธเนเธญ")
        
        c1, c2 = st.columns(2)
        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("๐—‘๏ธ เธฅเนเธฒเธเนเธฅเธฐเธชเธฃเนเธฒเธเนเธซเธกเน"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "เธชเธฑเธเธเธกเธจเธถเธเธฉเธฒ" in mode_select:
    st.subheader("๐“– เธชเธฃเนเธฒเธเนเธเธเธฒเธเธชเธฑเธเธเธกเธจเธถเธเธฉเธฒ (เธ•เธฒเธกเธซเธฅเธฑเธเธชเธนเธ•เธฃ เธชเธชเธงเธ—.)")
    
    # ==== DROPDOWN STRUCTURE ====
    create_options = [
        "๐“ เนเธเธเธฒเธ / เนเธเธเธเธถเธเธซเธฑเธ” (Worksheet)",
        "๐“ เธชเธฃเธธเธเน€เธเธทเนเธญเธซเธฒ (Summary)",
        "๐“ เนเธเธ—เธขเนเธเนเธญเธชเธญเธ (Quiz)"
    ]
    create_type = st.selectbox("เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เธ—เธตเนเธ•เนเธญเธเธเธฒเธฃ:", create_options, key="social_create_type")
    
    source_options = [
        "๐ค– AI เธชเธฃเนเธฒเธเนเธซเน (เธเธฒเธเธซเธฑเธงเธเนเธญ)",
        "๐“ เธเธฒเธเนเธเธฅเน (PDF/Word)",
        "โ๏ธ เธเธฒเธ Prompt (เน€เธเธตเธขเธเน€เธญเธ)"
    ]
    source_type = st.selectbox("เน€เธฅเธทเธญเธเธงเธดเธเธตเธชเธฃเนเธฒเธ:", source_options, key="social_source")
    
    # Social Studies Curriculum Data
    social_studies_topics = {
        # ===== เธฃเธฐเธ”เธฑเธเธเธฃเธฐเธ–เธกเธจเธถเธเธฉเธฒ =====
        "เธ.1": [
            ("1๏ธโฃ", "เธ•เธฑเธงเน€เธฃเธฒเนเธฅเธฐเธเธฃเธญเธเธเธฃเธฑเธง", "ai"),
            ("2๏ธโฃ", "เธเนเธฒเธเนเธฅเธฐเธ—เธตเนเธญเธขเธนเนเธญเธฒเธจเธฑเธข", "ai"),
            ("3๏ธโฃ", "เนเธฃเธเน€เธฃเธตเธขเธเนเธฅเธฐเน€เธเธทเนเธญเธ", "ai"),
            ("4๏ธโฃ", "เธเธธเธกเธเธเนเธฅเธฐเธฅเธฐเนเธงเธเธเนเธฒเธ", "ai"),
            ("5๏ธโฃ", "เธชเธ–เธฒเธเธ—เธตเนเธชเธณเธเธฑเธเนเธเธเธธเธกเธเธ", "ai"),
            ("6๏ธโฃ", "เธญเธฒเธเธตเธเนเธเธเธธเธกเธเธ", "ai"),
            ("7๏ธโฃ", "เธเธฒเธฃเนเธเนเธเนเธฒเธขเน€เธเธดเธ", "ai"),
            ("8๏ธโฃ", "เธ—เธดเธจเธ—เธฒเธเนเธฅเธฐเนเธเธเธ—เธตเนเธเนเธฒเธขเน", "ai"),
            ("9๏ธโฃ", "เธงเธฑเธเธชเธณเธเธฑเธเนเธฅเธฐเน€เธ—เธจเธเธฒเธฅ", "ai"),
            ("๐”", "เธจเธฒเธชเธเธฒเนเธฅเธฐเธเธงเธฒเธกเน€เธเธทเนเธญเธเธทเนเธเธเนเธฒเธ", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธ•เธฑเธงเน€เธฃเธฒ", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธเธฃเธฃเธกเธเธฒเธ•เธดเธฃเธญเธเธ•เธฑเธง", "ai"),
        ],
        "เธ.2": [
            ("1๏ธโฃ", "เธเธฃเธญเธเธเธฃเธฑเธงเนเธฅเธฐเธเธงเธฒเธกเธชเธฑเธกเธเธฑเธเธเน", "ai"),
            ("2๏ธโฃ", "เนเธฃเธเน€เธฃเธตเธขเธเธเธฑเธเธเธฒเธฃเน€เธฃเธตเธขเธเธฃเธนเน", "ai"),
            ("3๏ธโฃ", "เน€เธเธทเนเธญเธเนเธฅเธฐเธเธฒเธฃเธญเธขเธนเนเธฃเนเธงเธกเธเธฑเธ", "ai"),
            ("4๏ธโฃ", "เธเธธเธกเธเธเนเธฅเธฐเธ—เนเธญเธเธ–เธดเนเธ", "ai"),
            ("5๏ธโฃ", "เธชเธดเธ—เธเธดเนเธฅเธฐเธซเธเนเธฒเธ—เธตเนเธเธญเธเน€เธ”เนเธ", "ai"),
            ("6๏ธโฃ", "เธเธเธซเธกเธฒเธขเนเธเธเธตเธงเธดเธ•เธเธฃเธฐเธเธณเธงเธฑเธ", "ai"),
            ("7๏ธโฃ", "เน€เธเธดเธเธ•เธฃเธฒเนเธฅเธฐเธเธฒเธฃเธเธทเนเธญเธเธฒเธข", "ai"),
            ("8๏ธโฃ", "เธเธฒเธฃเธญเธญเธกเน€เธเธดเธ", "ai"),
            ("9๏ธโฃ", "เนเธเธเธ—เธตเนเนเธฅเธฐเธ—เธดเธจเธ—เธฒเธ", "ai"),
            ("๐”", "เธ—เธฃเธฑเธเธขเธฒเธเธฃเนเธเธเธธเธกเธเธ", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเธ—เนเธญเธเธ–เธดเนเธ", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธงเธฑเธ’เธเธเธฃเธฃเธกเธเธฃเธฐเน€เธเธ“เธตเนเธ—เธข", "ai"),
        ],
        "เธ.3": [
            ("1๏ธโฃ", "เธเธฒเธฃเธเธเธเธฃเธญเธเนเธเธเธฃเธญเธเธเธฃเธฑเธง", "ai"),
            ("2๏ธโฃ", "เธเธฒเธฃเธเธเธเธฃเธญเธเนเธเนเธฃเธเน€เธฃเธตเธขเธ", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเธเธเธเธฃเธญเธเนเธเธเธธเธกเธเธ", "ai"),
            ("4๏ธโฃ", "เธ—เนเธญเธเธ–เธดเนเธเธเธญเธเน€เธฃเธฒ", "ai"),
            ("5๏ธโฃ", "เธเธฒเธฃเน€เธเธฅเธตเนเธขเธเนเธเธฅเธเธเธญเธเธเธธเธกเธเธ", "ai"),
            ("6๏ธโฃ", "เธ เธนเธกเธดเธ เธฒเธเนเธเธเธฃเธฐเน€เธ—เธจเนเธ—เธข", "ai"),
            ("7๏ธโฃ", "เธฅเธฑเธเธฉเธ“เธฐเธ เธนเธกเธดเธเธฃเธฐเน€เธ—เธจเนเธ—เธข", "ai"),
            ("8๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเนเธเธเธธเธกเธเธ", "ai"),
            ("9๏ธโฃ", "เธเธฒเธฃเธเธฅเธดเธ• เธเธฒเธฃเธเธฃเธดเนเธ เธ", "ai"),
            ("๐”", "เธเธธเธ—เธเธเธฃเธฐเธงเธฑเธ•เธดเนเธฅเธฐเธเธธเธ—เธเธจเธฒเธชเธเธฒ", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธงเธฑเธ’เธเธเธฃเธฃเธกเธเธฃเธฐเน€เธเธ“เธตเนเธ—เธข", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธเธงเธฒเธกเธฃเธฑเธเธเธฒเธ•เธดเนเธ—เธข", "ai"),
        ],
        "เธ.4": [
            ("1๏ธโฃ", "เธเธฒเธฃเธเธเธเธฃเธญเธเธ—เนเธญเธเธ–เธดเนเธ", "ai"),
            ("2๏ธโฃ", "เธเธฒเธฃเน€เธฅเธทเธญเธเธ•เธฑเนเธเนเธเนเธฃเธเน€เธฃเธตเธขเธ", "ai"),
            ("3๏ธโฃ", "เธซเธเนเธฒเธ—เธตเนเธเธฅเน€เธกเธทเธญเธ", "ai"),
            ("4๏ธโฃ", "เธชเธดเธ—เธเธดเธเธญเธเน€เธ”เนเธ", "ai"),
            ("5๏ธโฃ", "เธ เธนเธกเธดเธ เธฒเธเธญเธฒเน€เธเธตเธขเธ", "ai"),
            ("6๏ธโฃ", "เธเธฃเธฐเน€เธ—เธจเน€เธเธทเนเธญเธเธเนเธฒเธเนเธ—เธข", "ai"),
            ("7๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเนเธเธเธธเธกเธเธ", "ai"),
            ("8๏ธโฃ", "เธเธฒเธฃเธเธฅเธดเธ•เนเธฅเธฐเธเธฒเธฃเธเธฃเธดเนเธ เธ", "ai"),
            ("9๏ธโฃ", "เธเธฒเธฃเธเธฃเธดเธซเธฒเธฃเน€เธเธดเธเนเธฅเธฐเธเธฒเธฃเธญเธญเธก", "ai"),
            ("๐”", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเนเธ—เธขเธชเธกเธฑเธขเธชเธธเนเธเธ—เธฑเธข", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธเธฒเธฃเธชเธนเธเน€เธชเธตเธขเธ”เธดเธเนเธ”เธ", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธเธธเธเธเธฅเธชเธณเธเธฑเธเนเธเธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเนเธ—เธข", "ai"),
        ],
        "เธ.5": [
            ("1๏ธโฃ", "เธเธฒเธฃเธเธเธเธฃเธญเธเธฃเธฐเธเธญเธเธเธฃเธฐเธเธฒเธเธดเธเนเธ•เธข", "ai"),
            ("2๏ธโฃ", "เธชเธ–เธฒเธเธฑเธเธเธฃเธฐเธกเธซเธฒเธเธฉเธฑเธ•เธฃเธดเธขเนเนเธ—เธข", "ai"),
            ("3๏ธโฃ", "เธชเธดเธ—เธเธดเธกเธเธธเธฉเธขเธเธ", "ai"),
            ("4๏ธโฃ", "เธซเธเนเธฒเธ—เธตเนเธเธฅเน€เธกเธทเธญเธเนเธ—เธข", "ai"),
            ("5๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเนเธเธฃเธฐเธ”เธฑเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("6๏ธโฃ", "เธเธฒเธฃเธเนเธฒเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("7๏ธโฃ", "เธ เธนเธกเธดเธจเธฒเธชเธ•เธฃเนเน€เธญเน€เธเธตเธข", "ai"),
            ("8๏ธโฃ", "เธ—เธฃเธฑเธเธขเธฒเธเธฃเธเธฃเธฃเธกเธเธฒเธ•เธด", "ai"),
            ("9๏ธโฃ", "เธชเธดเนเธเนเธงเธ”เธฅเนเธญเธกเนเธฅเธฐเธเธฒเธฃเธญเธเธธเธฃเธฑเธเธฉเน", "ai"),
            ("๐”", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเธญเธฒเน€เธเธตเธขเธ", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธเธงเธฒเธกเธฃเนเธงเธกเธกเธทเธญเนเธเธญเธฒเน€เธเธตเธขเธ", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเธญเธฒเน€เธเธตเธขเธ", "ai"),
        ],
        "เธ.6": [
            ("1๏ธโฃ", "เธเธฒเธฃเธเธเธเธฃเธญเธเธฃเธฐเธเธญเธเธเธฃเธฐเธเธฒเธเธดเธเนเธ•เธขเนเธเนเธ—เธข", "ai"),
            ("2๏ธโฃ", "เธฃเธฑเธเธเธฃเธฃเธกเธเธนเธเนเธฅเธฐเธเธฒเธฃเธกเธตเธชเนเธงเธเธฃเนเธงเธก", "ai"),
            ("3๏ธโฃ", "เธชเธดเธ—เธเธดเธซเธเนเธฒเธ—เธตเนเธเธฅเน€เธกเธทเธญเธ", "ai"),
            ("4๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเนเธฅเธ", "ai"),
            ("5๏ธโฃ", "เน€เธ—เธเนเธเนเธฅเธขเธตเธเธฑเธเน€เธจเธฃเธฉเธเธเธดเธ", "ai"),
            ("6๏ธโฃ", "เธ เธนเธกเธดเธจเธฒเธชเธ•เธฃเนเนเธฅเธ", "ai"),
            ("7๏ธโฃ", "เธชเธ เธฒเธเธ เธนเธกเธดเธญเธฒเธเธฒเธจเนเธฅเธฐเธ เธนเธกเธดเธเธฃเธฐเน€เธ—เธจเนเธฅเธ", "ai"),
            ("8๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเนเธฅเธ", "ai"),
            ("9๏ธโฃ", "เธกเธฃเธ”เธเธ—เธฒเธเธงเธฑเธ’เธเธเธฃเธฃเธกเนเธฅเธ", "ai"),
            ("๐”", "เธเธงเธฒเธกเธชเธฑเธกเธเธฑเธเธเนเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("1๏ธโฃ1๏ธโฃ", "เธญเธเธเนเธเธฃเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("1๏ธโฃ2๏ธโฃ", "เธเธงเธฒเธกเธกเธฑเนเธเธเธเนเธฅเธฐเธชเธฑเธเธ•เธดเธ เธฒเธเนเธฅเธ", "ai"),
        ],
        # ===== เธฃเธฐเธ”เธฑเธเธกเธฑเธเธขเธกเธจเธถเธเธฉเธฒ =====
        "เธก.1": [
            ("1๏ธโฃ", "เธจเธฒเธชเธเธฒเธเธฑเธเธงเธดเธ–เธตเธเธตเธงเธดเธ•", "ai"),
            ("2๏ธโฃ", "เธเธธเธ“เธเนเธฒเธเธญเธเธจเธฒเธชเธเธฒ", "ai"),
            ("3๏ธโฃ", "เธชเธดเธ—เธเธดเธซเธเนเธฒเธ—เธตเนเธเธฅเน€เธกเธทเธญเธ", "ai"),
            ("4๏ธโฃ", "เธเธเธซเธกเธฒเธขเนเธเธชเธฑเธเธเธก", "ai"),
            ("5๏ธโฃ", "เธเธฒเธฃเธเธฃเธดเธซเธฒเธฃเธ—เธฃเธฑเธเธขเธฒเธเธฃ", "ai"),
            ("6๏ธโฃ", "เธฃเธฐเธเธเน€เธจเธฃเธฉเธเธเธดเธ", "ai"),
            ("7๏ธโฃ", "เธ เธนเธกเธดเธจเธฒเธชเธ•เธฃเนเธเธฑเธเธเธตเธงเธดเธ•เธเธฃเธฐเธเธณเธงเธฑเธ", "ai"),
            ("8๏ธโฃ", "เนเธเธเธ—เธตเนเนเธฅเธฐเธเธฒเธฃเธญเนเธฒเธเธเนเธญเธกเธนเธฅเธ เธนเธกเธด", "ai"),
            ("9๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเธชเธนเนเธเธฑเธเธเธธเธเธฑเธ", "ai"),
            ("๐”", "เธญเธฒเธเธตเธเนเธฅเธฐเธเธฒเธฃเธ—เธณเธเธฒเธ", "ai"),
        ],
        "เธก.2": [
            ("1๏ธโฃ", "เธจเธฒเธชเธเธฒเธชเธฒเธเธฅเนเธฅเธฐเธเธฒเธฃเธญเธขเธนเนเธฃเนเธงเธกเธเธฑเธ", "ai"),
            ("2๏ธโฃ", "เธเธงเธฒเธกเธซเธฅเธฒเธเธซเธฅเธฒเธขเธ—เธฒเธเธจเธฒเธชเธเธฒ", "ai"),
            ("3๏ธโฃ", "เธเธฃเธฐเธเธฒเธเธดเธเนเธ•เธขเนเธฅเธฐเธเธฒเธฃเธกเธตเธชเนเธงเธเธฃเนเธงเธก", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเน€เธฅเธทเธญเธเธ•เธฑเนเธเนเธฅเธฐเธเธฒเธฃเธฅเธเธเธฐเนเธเธ", "ai"),
            ("5๏ธโฃ", "เธเธฒเธฃเธ•เธฅเธฒเธ”เนเธฅเธฐเธเธฒเธฃเน€เธเธดเธ", "ai"),
            ("6๏ธโฃ", "เธเธฒเธฃเธฅเธเธ—เธธเธเนเธฅเธฐเธเธฒเธฃเธญเธญเธก", "ai"),
            ("7๏ธโฃ", "เธ เธนเธกเธดเธจเธฒเธชเธ•เธฃเนเนเธเธ เธนเธกเธดเธ เธฒเธเธญเธฒเน€เธเธตเธขเธ", "ai"),
            ("8๏ธโฃ", "เธเธงเธฒเธกเธชเธฑเธกเธเธฑเธเธเนเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("9๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเธญเธฒเน€เธเธตเธขเธ", "ai"),
            ("๐”", "เธงเธฑเธ’เธเธเธฃเธฃเธกเธญเธฒเน€เธเธตเธขเธ", "ai"),
        ],
        "เธก.3": [
            ("1๏ธโฃ", "เธจเธฒเธชเธเธฒเธเธฑเธเธเธฒเธฃเธเธฑเธ’เธเธฒเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("2๏ธโฃ", "เธจเธตเธฅเธเธฃเธฃเธกเนเธเธขเธธเธเนเธฅเธเธฒเธ เธดเธงเธฑเธ•เธเน", "ai"),
            ("3๏ธโฃ", "เธเธฒเธฃเน€เธกเธทเธญเธเนเธเธเธฃเธฐเน€เธ—เธจเนเธ—เธข", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเน€เธฅเธทเธญเธเธ•เธฑเนเธเนเธฅเธฐเธเธฃเธฃเธเธเธฒเธฃเน€เธกเธทเธญเธ", "ai"),
            ("5๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเนเธ—เธขเนเธฅเธฐเธเธฒเธฃเน€เธเธฅเธตเนเธขเธเนเธเธฅเธ", "ai"),
            ("6๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเนเธฅเธเนเธฅเธฐเธเธฒเธฃเธเนเธฒเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("7๏ธโฃ", "เธ เธนเธกเธดเธจเธฒเธชเธ•เธฃเนเนเธฅเธ", "ai"),
            ("8๏ธโฃ", "เธชเธดเนเธเนเธงเธ”เธฅเนเธญเธกเนเธฅเธฐเธเธงเธฒเธกเธขเธฑเนเธเธขเธทเธ", "ai"),
            ("9๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเนเธฅเธเธชเธกเธฑเธขเนเธซเธกเน", "ai"),
            ("๐”", "เธขเธธเธเธชเธเธเธฃเธฒเธกเนเธฅเธเธเธฃเธฑเนเธเธ—เธตเน 1-2", "ai"),
        ],
        "เธก.4": [
            ("1๏ธโฃ", "เธจเธฒเธชเธเธฒเธเธฑเธเธชเธฑเธเธเธก", "ai"),
            ("2๏ธโฃ", "เธจเธฒเธชเธเธฒเน€เธเธฃเธตเธขเธเน€เธ—เธตเธขเธ", "ai"),
            ("3๏ธโฃ", "เธชเธดเธ—เธเธดเธกเธเธธเธฉเธขเธเธเธชเธฒเธเธฅ", "ai"),
            ("4๏ธโฃ", "เธเธเธซเธกเธฒเธขเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("5๏ธโฃ", "เน€เธจเธฃเธฉเธเธจเธฒเธชเธ•เธฃเนเธเธธเธฃเธเธดเธ", "ai"),
            ("6๏ธโฃ", "เธเธฒเธฃเธ•เธฅเธฒเธ”เนเธฅเธฐเธเธฒเธฃเธเธฑเธ”เธเธฒเธฃ", "ai"),
            ("7๏ธโฃ", "เธ เธนเธกเธดเธจเธฒเธชเธ•เธฃเนเธเธฒเธฃเน€เธกเธทเธญเธ", "ai"),
            ("8๏ธโฃ", "เธ—เธฃเธฑเธเธขเธฒเธเธฃเนเธฅเธฐเธชเธดเนเธเนเธงเธ”เธฅเนเธญเธกเนเธฅเธ", "ai"),
            ("9๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเธชเธฑเธเธเธก", "ai"),
            ("๐”", "เธงเธฑเธ’เธเธเธฃเธฃเธกเนเธฅเธฐเธญเธฒเธฃเธขเธเธฃเธฃเธกเนเธฅเธ", "ai"),
        ],
        "เธก.5": [
            ("1๏ธโฃ", "เธจเธฒเธชเธเธฒเธเธฑเธเธเธงเธฒเธกเธเธฑเธ”เนเธขเนเธ", "ai"),
            ("2๏ธโฃ", "เธจเธฒเธชเธเธฒเนเธเธขเธธเธเนเธฅเธเธฒเธ เธดเธงเธฑเธ•เธเน", "ai"),
            ("3๏ธโฃ", "เธเธฃเธฐเธเธฒเธเธดเธเนเธ•เธขเนเธฅเธฐเธฃเธฐเธเธญเธเธเธฒเธฃเธเธเธเธฃเธญเธ", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเน€เธกเธทเธญเธเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("5๏ธโฃ", "เน€เธจเธฃเธฉเธเธจเธฒเธชเธ•เธฃเนเธเธฒเธฃเธเธฑเธ’เธเธฒ", "ai"),
            ("6๏ธโฃ", "เธเธงเธฒเธกเธกเธฑเนเธเธเธเธ—เธฒเธเน€เธจเธฃเธฉเธเธเธดเธ", "ai"),
            ("7๏ธโฃ", "เธ เธนเธกเธดเธจเธฒเธชเธ•เธฃเนเน€เธจเธฃเธฉเธเธเธดเธเนเธฅเธ", "ai"),
            ("8๏ธโฃ", "เธเธฒเธฃเธ—เธนเธ•เนเธฅเธฐเธเธงเธฒเธกเธชเธฑเธกเธเธฑเธเธเนเธฃเธฐเธซเธงเนเธฒเธเธเธฒเธ•เธด", "ai"),
            ("9๏ธโฃ", "เธเธฃเธฐเธงเธฑเธ•เธดเธจเธฒเธชเธ•เธฃเนเน€เธจเธฃเธฉเธเธเธดเธ", "ai"),
            ("๐”", "เน€เธ—เธเนเธเนเธฅเธขเธตเธเธฑเธเธเธฒเธฃเน€เธเธฅเธตเนเธขเธเนเธเธฅเธเธ—เธฒเธเธชเธฑเธเธเธก", "ai"),
        ],
        "เธก.6": [
            ("1๏ธโฃ", "เธจเธฒเธชเธเธฒ เธเธธเธ“เธเธฃเธฃเธก เนเธฅเธฐเธเธฃเธดเธขเธเธฃเธฃเธก", "ai"),
            ("2๏ธโฃ", "เธชเธฑเธเธเธกเนเธฅเธฐเธงเธฑเธ’เธเธเธฃเธฃเธกเธฃเนเธงเธกเธชเธกเธฑเธข", "ai"),
            ("3๏ธโฃ", "เธชเธดเธ—เธเธดเธกเธเธธเธฉเธขเธเธเนเธเธเธฃเธฐเน€เธ—เธจเนเธ—เธข", "ai"),
            ("4๏ธโฃ", "เธเธฒเธฃเน€เธกเธทเธญเธเนเธฅเธฐเธเธฒเธฃเธเธเธเธฃเธญเธเนเธเธญเธเธฒเธเธ•", "ai"),
            ("5๏ธโฃ", "เน€เธจเธฃเธฉเธเธเธดเธเนเธ—เธขเนเธเธเธฃเธดเธเธ—เนเธฅเธ", "ai"),
            ("6๏ธโฃ", "เธเธงเธฒเธกเธกเธฑเนเธเธเธเธฃเธฐเธซเธงเนเธฒเธเธเธฃเธฐเน€เธ—เธจ", "ai"),
            ("7๏ธโฃ", "เธญเธฒเน€เธเธตเธขเธเนเธเธจเธ•เธงเธฃเธฃเธฉเธ—เธตเน 21", "ai"),
            ("8๏ธโฃ", "เนเธฅเธเธฒเธ เธดเธงเธฑเธ•เธเนเนเธฅเธฐเธเธงเธฒเธกเธ—เนเธฒเธ—เธฒเธข", "ai"),
            ("9๏ธโฃ", "เธญเธฒเธเธตเธเนเธเธญเธเธฒเธเธ•เนเธฅเธฐเธ—เธฑเธเธฉเธฐเธจเธ•เธงเธฃเธฃเธฉเธ—เธตเน 21", "ai"),
            ("๐”", "เธเธฒเธฃเน€เธเนเธเธเธฅเน€เธกเธทเธญเธเนเธฅเธ", "ai"),
        ],
    }
    
    # Grade Selection
    social_grade_options = ["เธ.1", "เธ.2", "เธ.3", "เธ.4", "เธ.5", "เธ.6", "เธก.1", "เธก.2", "เธก.3", "เธก.4", "เธก.5", "เธก.6"]
    social_grade_select = st.selectbox("๐“ เน€เธฅเธทเธญเธเธฃเธฐเธ”เธฑเธเธเธฑเนเธ:", social_grade_options)
    
    # Topic selection with display names
    social_topics_list = social_studies_topics.get(social_grade_select, [])
    social_topic_options = [f"{prefix} {name}" for prefix, name, _ in social_topics_list]
    social_topic_select = st.selectbox("๐“– เน€เธฅเธทเธญเธเธซเธฑเธงเธเนเธญ:", social_topic_options)
    
    # Get selected topic details
    selected_social_topic = None
    for prefix, name, topic_type in social_topics_list:
        full_name = f"{prefix} {name}"
        if full_name == social_topic_select:
            selected_social_topic = name
            break
    
    # Show AI requirement message
    st.info("๐“ เธซเธฑเธงเธเนเธญเธชเธฑเธเธเธกเธจเธถเธเธฉเธฒเธ—เธฑเนเธเธซเธกเธ”เธ•เนเธญเธเนเธเน AI เนเธเธเธฒเธฃเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธเนเธฐ")
    
    # Exercise type selector
    exercise_types = [
        "เธ—เธฑเนเธเธซเธกเธ” (เธเธชเธกเธเธชเธฒเธ)",
        "เธเธงเธฒเธกเธฃเธนเนเธเธทเนเธเธเธฒเธ (Knowledge)",
        "เธเธงเธฒเธกเน€เธเนเธฒเนเธ (Comprehension)",
        "เธเธฒเธฃเธงเธดเน€เธเธฃเธฒเธฐเธซเน (Analysis)",
        "เธเธฒเธฃเธเธฃเธฐเน€เธกเธดเธเธเนเธฒ (Evaluation)",
        "เธเธฒเธฃเธชเธฃเนเธฒเธเธชเธฃเธฃเธเน (Creation)"
    ]
    exercise_type = st.selectbox("๐“ เน€เธฅเธทเธญเธเธเธฃเธฐเน€เธ เธ—เนเธเธเธเธถเธเธซเธฑเธ”:", exercise_types)
    
    num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=20)
    
    # Custom Prompt Section
    with st.expander("โ๏ธ เธเธฃเธฑเธเนเธ•เนเธ Prompt (เนเธกเนเธเธฑเธเธเธฑเธ)", expanded=False):
        social_prompt = st.text_area(
            "Prompt เธชเธณเธซเธฃเธฑเธ AI (เธ–เนเธฒเน€เธงเนเธเธงเนเธฒเธเธเธฐเนเธเนเธเนเธฒเน€เธฃเธดเนเธกเธ•เนเธ)",
            value="",
            height=100,
            help="เธเธฃเธฑเธเนเธ•เนเธ prompt เน€เธเธทเนเธญเนเธซเนเนเธ”เนเธเธฅเธฅเธฑเธเธเนเธ•เธฒเธกเธ•เนเธญเธเธเธฒเธฃ"
        )
        
        st.markdown("**๐’ก เธ•เธฑเธงเธญเธขเนเธฒเธ Prompt เธ—เธตเนเธ”เธต:**")
        st.code("เธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธชเธฑเธเธเธกเธจเธถเธเธฉเธฒ 10 เธเนเธญ เน€เธฃเธทเนเธญเธเธเธฒเธฃเธเธเธเธฃเธญเธเธฃเธฐเธเธญเธเธเธฃเธฐเธเธฒเธเธดเธเนเธ•เธข เธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธ เธ.5 เนเธซเนเธกเธตเธ—เธฑเนเธเธเธณเธ–เธฒเธกเธ–เธนเธ-เธเธดเธ” เธเธฃเธเธฑเธข เนเธฅเธฐเธเธณเธ–เธฒเธกเน€เธเธดเธ” เธเธฃเนเธญเธกเน€เธเธฅเธขเธฅเธฐเน€เธญเธตเธขเธ”", language="text")
    
    if st.button("๐€ เธชเธฃเนเธฒเธเนเธเธเธฒเธเธชเธฑเธเธเธกเธจเธถเธเธฉเธฒ", type="primary"):
        if not st.session_state.api_key:
            st.info("๐”‘ เธ•เนเธญเธเนเธเน API Key เธชเธณเธซเธฃเธฑเธเธซเธฑเธงเธเนเธญเธชเธฑเธเธเธกเธจเธถเธเธฉเธฒเธเนเธฐ เธเธฃเธญเธ API Key เนเธ”เนเธ—เธตเนเธ”เนเธฒเธเธเธเธเธฐเธเธฐ")
        else:
            with st.spinner("๐ค– AI เธเธณเธฅเธฑเธเธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”เธชเธฑเธเธเธกเธจเธถเธเธฉเธฒ..."):
                # Map exercise type to prompt
                exercise_mapping = {
                    "เธ—เธฑเนเธเธซเธกเธ” (เธเธชเธกเธเธชเธฒเธ)": "mix",
                    "เธเธงเธฒเธกเธฃเธนเนเธเธทเนเธเธเธฒเธ (Knowledge)": "knowledge",
                    "เธเธงเธฒเธกเน€เธเนเธฒเนเธ (Comprehension)": "comprehension",
                    "เธเธฒเธฃเธงเธดเน€เธเธฃเธฒเธฐเธซเน (Analysis)": "analysis",
                    "เธเธฒเธฃเธเธฃเธฐเน€เธกเธดเธเธเนเธฒ (Evaluation)": "evaluation",
                    "เธเธฒเธฃเธชเธฃเนเธฒเธเธชเธฃเธฃเธเน (Creation)": "creation"
                }
                
                questions, answers = generator.generate_social_studies_worksheet(
                    selected_social_topic, 
                    social_grade_select,
                    num_q,
                    exercise_mapping.get(exercise_type, "mix")
                )
                
                pdf = generator.create_pdf(title, school_name, selected_social_topic, questions, answers, qr_url, uploaded_logo)
                word = generator.create_word_doc(title, school_name, selected_social_topic, questions, answers)
                
                st.session_state.generated_pdf = pdf
                st.session_state.generated_word = word
                st.session_state.generated_filename = "social_worksheet"
                st.session_state.preview_questions = questions
                st.session_state.preview_answers = answers
    
    # Show preview and download buttons if content is generated
    if st.session_state.generated_pdf is not None and st.session_state.get("generated_filename") == "social_worksheet":
        st.success("โ… เธชเธฃเนเธฒเธเนเธเธเธฒเธเธชเธฑเธเธเธกเธจเธถเธเธฉเธฒเธชเธณเน€เธฃเนเธ!")
        
        # Preview section
        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธณเธ–เธฒเธกเนเธฅเธฐเน€เธเธฅเธข", expanded=True):
            st.markdown("### ๐“ เธเธณเธ–เธฒเธก / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_questions) - 10} เธเนเธญ")
            
            st.markdown("### โ… เน€เธเธฅเธข / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... เนเธฅเธฐเธญเธตเธ {len(st.session_state.preview_answers) - 10} เธเนเธญ")
        
        c1, c2 = st.columns(2)
        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("๐—‘๏ธ เธฅเนเธฒเธเนเธฅเธฐเธชเธฃเนเธฒเธเนเธซเธกเน"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "เนเธเธ—เธขเนเธเธฑเธเธซเธฒ AI" in mode_select:
    st.subheader("๐ค– เธชเธฃเนเธฒเธเนเธเธ—เธขเนเธเธฑเธเธซเธฒเธ”เนเธงเธข AI")
    
    if not st.session_state.api_key:
        show_api_warning()
    else:
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("เธซเธฑเธงเธเนเธญ (เน€เธเนเธ เธญเธงเธเธฒเธจ, เธชเธงเธเธชเธฑเธ•เธงเน, เธ•เธฅเธฒเธ”)", "เธเธฒเธฃเธเธเธเธ เธฑเธขเนเธเธญเธงเธเธฒเธจ")
            grade = st.selectbox("เธฃเธฐเธ”เธฑเธเธเธฑเนเธ", ["เธ.1", "เธ.2", "เธ.3", "เธ.4", "เธ.5", "เธ.6"])
        with col2:
            num_q = st.number_input("เธเธณเธเธงเธเธเนเธญ", min_value=1, max_value=50, value=5)
        
        # Custom Prompt Section
        with st.expander("โ๏ธ เธเธฃเธฑเธเนเธ•เนเธ Prompt (เนเธกเนเธเธฑเธเธเธฑเธ)", expanded=False):
            word_problem_prompt = st.text_area(
                "Prompt เธชเธณเธซเธฃเธฑเธ AI (เธ–เนเธฒเน€เธงเนเธเธงเนเธฒเธเธเธฐเนเธเนเธเนเธฒเน€เธฃเธดเนเธกเธ•เนเธ)",
                value="",
                height=100,
                help="เธเธฃเธฑเธเนเธ•เนเธ prompt เน€เธเธทเนเธญเนเธซเนเนเธ”เนเธเธฅเธฅเธฑเธเธเนเธ•เธฒเธกเธ•เนเธญเธเธเธฒเธฃ"
            )
            
            st.markdown("**๐’ก เธ•เธฑเธงเธญเธขเนเธฒเธ Prompt เธ—เธตเนเธ”เธต:**")
            st.code("เธชเธฃเนเธฒเธเนเธเธ—เธขเนเธเธฑเธเธซเธฒเธเธ“เธดเธ•เธจเธฒเธชเธ•เธฃเน 5 เธเนเธญ เน€เธฃเธทเนเธญเธเธเธฒเธฃเธเธนเธ“เนเธฅเธฐเธเธฒเธฃเธซเธฒเธฃ เธชเธณเธซเธฃเธฑเธเธเธฑเธเน€เธฃเธตเธขเธเธ.3 เนเธซเนเน€เธเนเธเนเธเธ—เธขเนเธชเธ–เธฒเธเธเธฒเธฃเธ“เนเนเธเธเธตเธงเธดเธ•เธเธฃเธดเธ เน€เธเนเธ เธเธฒเธฃเธเธทเนเธญเธเธญเธ เธเธฒเธฃเนเธเนเธเธเธญเธ เนเธเธ—เธขเนเธ•เนเธญเธเธกเธตเธเธงเธฒเธกเธซเธฅเธฒเธเธซเธฅเธฒเธขเนเธฅเธฐเธ—เนเธฒเธ—เธฒเธขเน€เธซเธกเธฒเธฐเธเธฑเธเธงเธฑเธข", language="text")
        
        if st.button("๐€ เนเธซเน AI เธชเธฃเนเธฒเธเนเธเธ—เธขเน", type="primary"):
            with st.spinner("AI เธเธณเธฅเธฑเธเธเธดเธ”เนเธเธ—เธขเน... (เธฃเธญเธชเธฑเธเธเธฃเธนเนเธเธฐเธเธฃเธฑเธ)"):
                grade_map = {"เธ.1": "Grade 1", "เธ.2": "Grade 2", "เธ.3": "Grade 3", "เธ.4": "Grade 4", "เธ.5": "Grade 5", "เธ.6": "Grade 6"}
                questions, answers = generator.generate_ai_word_problems(topic, grade_map.get(grade, "Grade 3"), num_q)
                
                pdf = generator.create_pdf(title, school_name, "AI Word Problems", questions, answers, qr_url, uploaded_logo)
                word = generator.create_word_doc(title, school_name, "AI Word Problems", questions, answers)
                
                # Preview section
                with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธณเธ–เธฒเธกเนเธฅเธฐเน€เธเธฅเธข", expanded=True):
                    st.markdown("### ๐“ เธเธณเธ–เธฒเธก / Questions")
                    for i, q in enumerate(questions[:10], 1):
                        st.write(f"**{i}.** {q}")
                    if len(questions) > 10:
                        st.write(f"... เนเธฅเธฐเธญเธตเธ {len(questions) - 10} เธเนเธญ")
                    
                    st.markdown("### โ… เน€เธเธฅเธข / Answers")
                    for i, a in enumerate(answers[:10], 1):
                        st.write(f"**{i}.** {a}")
                    if len(answers) > 10:
                        st.write(f"... เนเธฅเธฐเธญเธตเธ {len(answers) - 10} เธเนเธญ")
                
                st.success("โ… เธชเธฃเนเธฒเธเนเธเธ—เธขเนเน€เธชเธฃเนเธเนเธฅเนเธง!")
                c1, c2 = st.columns(2)
                c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "ai_worksheet.pdf", "application/pdf")
                c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "ai_worksheet.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "เธเธฃเธดเธจเธเธฒเธซเธฒเธเธณเธจเธฑเธเธ—เน" in mode_select:
    st.subheader("๐” เธชเธฃเนเธฒเธเธเธฃเธดเธจเธเธฒเธซเธฒเธเธณเธจเธฑเธเธ—เน (Word Search)")
    words_input = st.text_area("เนเธชเนเธเธณเธจเธฑเธเธ—เนเธ เธฒเธฉเธฒเธญเธฑเธเธเธคเธฉ (เธเธฑเนเธเธ”เนเธงเธขเธเธธเธฅเธ เธฒเธ ,)", "CAT, DOG, BIRD, LION, TIGER")
    words = [w.strip() for w in words_input.split(",") if w.strip()]
    
    if st.button("๐€ เธชเธฃเนเธฒเธเธเธฃเธดเธจเธเธฒ", type="primary"):
        grid, placed_words = generator.generate_word_search(words)
        pdf = generator.create_pdf(title, school_name, "Word Search", (grid, placed_words), answers=placed_words, qr_link=qr_url, uploaded_logo=uploaded_logo)
        word = generator.create_word_doc(title, school_name, "Word Search", (grid, placed_words), answers=placed_words)
        
        # Preview section
        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธฃเธดเธจเธเธฒ", expanded=True):
            st.markdown("### ๐“ เธเธณเธจเธฑเธเธ—เนเธ—เธตเนเธเนเธญเธเนเธเธเธฃเธดเธจเธเธฒ")
            cols = st.columns(5)
            for i, w in enumerate(placed_words):
                cols[i % 5].write(f"โ€ข {w}")
        
        st.success("โ… เธชเธฃเนเธฒเธเธเธฃเธดเธจเธเธฒเน€เธฃเธตเธขเธเธฃเนเธญเธข!")
        c1, c2 = st.columns(2)
        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "puzzle.pdf", "application/pdf")
        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "puzzle.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "เธเธถเธเธเธฑเธ”เธฅเธฒเธขเธกเธทเธญ" in mode_select:
    st.subheader("โ๏ธ เธชเธฃเนเธฒเธเนเธเธเธเธถเธเธเธฑเธ”เธฅเธฒเธขเธกเธทเธญ")
    text_input = st.text_area("เธเนเธญเธเธงเธฒเธกเธ—เธตเนเธ•เนเธญเธเธเธฒเธฃเนเธซเนเธเธฑเธ” (เธเธฑเนเธเธ”เนเธงเธขเธเธธเธฅเธ เธฒเธ)", "เธชเธงเธฑเธชเธ”เธต, เธเธญเธเธเธธเธ“, เธเธญเนเธ—เธฉ, เธฃเธฑเธเธเธฐ")
    
    if st.button("๐€ เธชเธฃเนเธฒเธเนเธเธเธเธถเธเธซเธฑเธ”", type="primary"):
        lines = generator.generate_tracing_lines(text_input)
        pdf = generator.create_pdf(title, school_name, "Handwriting Practice", lines, uploaded_logo=uploaded_logo)
        word = generator.create_word_doc(title, school_name, "Handwriting Practice", lines)
        
        # Preview section
        with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเนเธญเธเธงเธฒเธก", expanded=True):
            st.markdown("### ๐“ เธเนเธญเธเธงเธฒเธกเธ—เธตเนเธเธฐเธเธถเธเธเธฑเธ”")
            for i, line in enumerate(lines):
                st.write(f"**{i+1}.** {line}")
        
        st.success("โ… เธชเธฃเนเธฒเธเธชเธณเน€เธฃเนเธ!")
        c1, c2 = st.columns(2)
        c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "tracing.pdf", "application/pdf")
        c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "tracing.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "เธชเธฃเนเธฒเธเธเนเธญเธชเธญเธเธเธฒเธเนเธเธฅเน" in mode_select:
    st.subheader("๐“ เธชเธฃเนเธฒเธเธเนเธญเธชเธญเธเธเธฒเธเนเธเธฅเนเน€เธญเธเธชเธฒเธฃ (PDF/Word)")
    
    if not st.session_state.api_key:
        show_api_warning()
    else:
        uploaded_file = st.file_uploader("เธญเธฑเธเนเธซเธฅเธ”เน€เธญเธเธชเธฒเธฃเธเธฃเธฐเธเธญเธเธเธฒเธฃเธชเธญเธ (PDF เธซเธฃเธทเธญ Docx)", type=["pdf", "docx"])
        num_q = st.number_input("เธเธณเธเธงเธเธเนเธญเธชเธญเธเธ—เธตเนเธ•เนเธญเธเธเธฒเธฃ", min_value=1, max_value=50, value=5)
        
        # Custom Prompt Section
        with st.expander("โ๏ธ เธเธฃเธฑเธเนเธ•เนเธ Prompt (เนเธกเนเธเธฑเธเธเธฑเธ)", expanded=False):
            quiz_prompt = st.text_area(
                "Prompt เธชเธณเธซเธฃเธฑเธ AI (เธ–เนเธฒเน€เธงเนเธเธงเนเธฒเธเธเธฐเนเธเนเธเนเธฒเน€เธฃเธดเนเธกเธ•เนเธ)",
                value="",
                height=100,
                help="เธเธฃเธฑเธเนเธ•เนเธ prompt เน€เธเธทเนเธญเนเธซเนเนเธ”เนเธเธฅเธฅเธฑเธเธเนเธ•เธฒเธกเธ•เนเธญเธเธเธฒเธฃ"
            )
            
            st.markdown("**๐’ก เธ•เธฑเธงเธญเธขเนเธฒเธ Prompt เธ—เธตเนเธ”เธต:**")
            st.code("เธชเธฃเนเธฒเธเธเนเธญเธชเธญเธ 10 เธเนเธญ เธเธฒเธเน€เธเธทเนเธญเธซเธฒเธ—เธตเนเนเธซเนเธกเธฒ เนเธซเนเธกเธตเธ—เธฑเนเธเนเธเธเธ–เธนเธ-เธเธดเธ” เธเธฃเธเธฑเธข 4 เธ•เธฑเธงเน€เธฅเธทเธญเธ เนเธฅเธฐเธเธณเธ–เธฒเธกเธ–เธนเธเธเธงเธฒเธกเน€เธเนเธฒเนเธ เธเธฃเนเธญเธกเน€เธเธฅเธขเธฅเธฐเน€เธญเธตเธขเธ”", language="text")
        
        if uploaded_file and st.button("๐€ เธชเธฃเนเธฒเธเธเนเธญเธชเธญเธเธเธฒเธเนเธเธฅเน", type="primary"):
            with st.spinner("AI เธเธณเธฅเธฑเธเธญเนเธฒเธเนเธเธฅเนเนเธฅเธฐเธญเธญเธเธเนเธญเธชเธญเธ..."):
                text = generator.extract_text_from_file(uploaded_file)
                
                if not text or "Error" in text:
                    st.error(f"เธญเนเธฒเธเนเธเธฅเนเธฅเนเธกเน€เธซเธฅเธง: {text}")
                else:
                    questions, answers = generator.generate_quiz_from_text(text, num_q)
                    
                    pdf = generator.create_pdf(title, school_name, "Quiz", questions, answers, qr_url, uploaded_logo)
                    word = generator.create_word_doc(title, school_name, "Quiz", questions, answers)
                    
                    # Preview section
                    with st.expander("๐‘€ เธ”เธนเธ•เธฑเธงเธญเธขเนเธฒเธเธเธณเธ–เธฒเธกเนเธฅเธฐเน€เธเธฅเธข", expanded=True):
                        st.markdown("### ๐“ เธเธณเธ–เธฒเธก / Questions")
                        for i, q in enumerate(questions[:10], 1):
                            st.write(f"**{i}.** {q}")
                        if len(questions) > 10:
                            st.write(f"... เนเธฅเธฐเธญเธตเธ {len(questions) - 10} เธเนเธญ")
                        
                        st.markdown("### โ… เน€เธเธฅเธข / Answers")
                        for i, a in enumerate(answers[:10], 1):
                            st.write(f"**{i}.** {a}")
                        if len(answers) > 10:
                            st.write(f"... เนเธฅเธฐเธญเธตเธ {len(answers) - 10} เธเนเธญ")
                    
                    st.success(f"โ… เธชเธฃเนเธฒเธเธเนเธญเธชเธญเธ {len(questions)} เธเนเธญ เธชเธณเน€เธฃเนเธเนเธฅเนเธง!")
                    c1, c2 = st.columns(2)
                    c1.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” PDF", pdf, "quiz.pdf", "application/pdf")
                    c2.download_button("๐“ เธ”เธฒเธงเธเนเนเธซเธฅเธ” Word", word, "quiz.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.markdown("---")
st.caption("เธเธฑเธ’เธเธฒเนเธ”เธข **Nong Aom & P'Em** | Powered by Google Gemini AI")
