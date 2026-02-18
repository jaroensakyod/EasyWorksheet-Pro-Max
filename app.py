# app.py (EasyWorksheet Pro Max - Thai Version with Full IPST Curriculum)
import streamlit as st
import os
import sys
from PIL import Image
from google import genai

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

st.set_page_config(page_title="โปรแกรมสร้างใบงาน EasyWorksheet", page_icon="🚀", layout="wide")

st.title("🚀 โปรแกรมสร้างใบงาน EasyWorksheet")
st.caption("ระบบสร้างใบงานอัตโนมัติด้วย AI สำหรับคุณครูยุคใหม่ (Created by Nong Aom & P'Em)")

# --- API Key Section (Always Visible) ---
with st.expander("🔑 ตั้งค่า API Key", expanded=not st.session_state.api_key):
    # Provider Selection Dropdown
    provider_options = ["Google Gemini", "Groq", "OpenRouter"]
    selected_provider = st.selectbox(
        "🔽 เลือกผู้ให้บริการ AI:",
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
            api_input = st.text_input("🔑 ใส่ Google Gemini API Key", type="password", placeholder="AIza...")
            st.markdown("[👉 กดที่นี่เพื่อขอรับ API Key ฟรี (Google AI Studio)](https://aistudio.google.com/app/apikey)")
        elif selected_provider == "Groq":
            api_input = st.text_input("🔑 ใส่ Groq API Key", type="password", placeholder="gsk_...")
            st.markdown("[👉 กดที่นี่เพื่อขอรับ API Key (Groq Console)](https://console.groq.com)")
        elif selected_provider == "OpenRouter":
            api_input = st.text_input("🔑 ใส่ OpenRouter API Key", type="password", placeholder="sk-or-v1-...")
            st.markdown("[👉 กดที่นี่เพื่อขอรับ API Key (OpenRouter)](https://openrouter.ai)")
        
        if api_input:
            clean_key = api_input.strip()
            try:
                # Configure and test based on provider
                if selected_provider == "Google Gemini":
                    client = genai.Client(api_key=clean_key)
                    # Test call - list models
                    list(client.models.list())
                # For Groq and OpenRouter, we'll test through the generator
                
                st.session_state.api_key = clean_key
                st.session_state.api_provider = selected_provider
                st.success(f"✅ เชื่อมต่อกับ {selected_provider} สำเร็จ!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ API Key ไม่ถูกต้อง: {e}")
    else:
        st.success(f"✅ เชื่อมต่อกับ {st.session_state.api_provider} แล้ว")
        if st.button("🗑️ ลบ API Key"):
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
    st.header("⚙️ แผงควบคุม (Control Panel)")
    
    school_name = st.text_input("🏫 ชื่อโรงเรียน / ชื่อคุณครู", "โรงเรียนตัวอย่าง")
    
    uploaded_logo = st.file_uploader("🖼️ อัปโหลดโลโก้โรงเรียน (ถ้ามี)", type=["png", "jpg", "jpeg"])
    
    st.markdown("---")
    
    # Mode Selection (Thai)
    mode_options = [
        "🧪 ทดสอบ AI (Test AI)",
        "📐 ฝึกทักษะคณิตศาสตร์ (Math)",
        "🔬 วิทยาศาสตร์ (Science)",
        "📚 ภาษาไทย (Thai Language)",
        "🌏 ภาษาอังกฤษ (English Language)",
        "📖 สังคมศึกษา (Social Studies)",
        "🤖 โจทย์ปัญหา AI (Word Problems)",
        "🔍 ปริศนาหาคำศัพท์ (Word Search)",
        "✍️ ฝึกคัดลายมือ (Handwriting)",
        "📝 สร้างข้อสอบจากไฟล์ (File to Quiz)"
    ]
    mode_select = st.selectbox("เลือกประเภทใบงาน:", mode_options)
    
    title = st.text_input("หัวข้อใบงาน", "แบบฝึกหัดที่ 1")
    
    include_qr = st.checkbox("เพิ่ม QR Code เฉลย?", value=True)
    qr_url = st.text_input("ลิงก์เฉลย (เช่น Google Drive)", "https://example.com/answers") if include_qr else None

# --- API Check Function ---
def check_api_required():
    """Check if API key is required for current selection"""
    if st.session_state.api_key:
        return False  # API is available
    
    # List of modes/topics that require API
    ai_required_modes = [
        "โจทย์ปัญหา AI",
        "สร้างข้อสอบจากไฟล์"
    ]
    
    # Check mode first
    for mode in ai_required_modes:
        if mode in mode_select:
            return True
    
    # Check if topic requires AI
    if "🌟" in mode_select:
        return True
    
    return False

def show_api_warning():
    """Show yellow warning popup for missing or non-working API"""
    provider_name = st.session_state.api_provider if st.session_state.api_provider else "AI"
    st.warning(f"⚠️ **ต้องใช้ {provider_name} API Key** สำหรับฟีเจอร์นี้ค่ะ!", icon="🔑")
    st.info("📌 กรอก API Key ได้ที่ด้านบนของหน้าจอนี้เลยค่ะ")
    
    # Show appropriate link based on provider
    if st.session_state.api_provider == "Google Gemini":
        st.markdown("[👉 ขอ API Key ฟรีที่นี่ (Google AI Studio)](https://aistudio.google.com/app/apikey)")
    elif st.session_state.api_provider == "Groq":
        st.markdown("[👉 ขอ API Key ที่นี่ (Groq Console)](https://console.groq.com)")
    elif st.session_state.api_provider == "OpenRouter":
        st.markdown("[👉 ขอ API Key ที่นี่ (OpenRouter)](https://openrouter.ai)")

def check_ai_and_generate(generator, generate_func, *args, **kwargs):
    """Check if AI is working, if not use template generation"""
    if generator.is_ai_working():
        # AI is working, use AI generation
        return generate_func(*args, **kwargs)
    else:
        # AI not working, show warning and use fallback
        st.warning("⚠️ **AI ไม่ทำงาน กำลังใช้แบบตัวอย่างแทนค่ะ**")
        st.info("💡 หากต้องการใช้ AI กรุณาตรวจสอบ API Key ที่ด้านบนนะคะ")
        return None  # Will be handled by caller

# --- Main Content Area ---

if "ทดสอบ AI" in mode_select:
    st.subheader("🧪 ทดสอบการเชื่อมต่อ AI และ Prompt")
    
    # Check AI connection
    if not st.session_state.api_key:
        st.warning("⚠️ กรุณาใส่ API Key ที่ด้านบนก่อนนะคะ!")
    else:
        # Initialize generator to test
        test_generator = WorksheetGenerator(
            ai_api_key=st.session_state.api_key, 
            provider=st.session_state.api_provider
        )
        
        # Connection Status
        st.markdown("### 🔌 สถานะการเชื่อมต่อ")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Provider:** {st.session_state.api_provider}")
        
        with col2:
            if test_generator.is_ai_working():
                st.success("**Status:** ✅ เชื่อมต่อสำเร็จ!")
            else:
                st.error("**Status:** ❌ ไม่สามารถเชื่อมต่อได้")
        
        with col3:
            if test_generator.ai and hasattr(test_generator.ai, 'model_name'):
                st.info(f"**Model:** {test_generator.ai.model_name}")
        
        st.markdown("---")
        
        # Custom Prompt Section
        st.markdown("### 🤖 ทดสอบ Prompt กับ AI")
        
        # Pre-made prompt templates
        prompt_templates = {
            "ทั่วไป": "สร้างแบบฝึกหัดคณิตศาสตร์ 5 ข้อ เรื่องการบวกสำหรับนักเรียนประถม",
            "คณิต": "สร้างโจทย์คณิตศาสตร์ 3 ข้อ เรื่องการคูณ สำหรับ ป.3",
            "วิทย์": "สร้างคำถามวิทยาศาสตร์ 5 ข้อ เรื่องระบบร่างกายมนุษย์",
            "ไทย": "สร้างแบบฝึกหัดภาษาไทย 5 ข้อ เรื่องคำนาม",
            "อังกฤษ": "สร้างแบบฝึกหัดภาษาอังกฤษ 5 ข้อ เรื่อง Tenses",
        }
        
        template_choice = st.selectbox("📝 เลือก Template:", list(prompt_templates.keys()), index=0)
        
        # Custom prompt input
        custom_prompt = st.text_area(
            "✏️ Prompt ของคุณ (เขียนเองได้):",
            value=prompt_templates[template_choice],
            height=150
        )
        
        # Number of questions
        test_num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=5)
        
        # Test button
        if st.button("🚀 ทดสอบ AI", type="primary"):
            if not test_generator.is_ai_working():
                st.error("❌ AI ไม่ทำงาน! กรุณาตรวจสอบ API Key ที่ด้านบนนะคะ")
                st.info(f"💡 Provider ที่ใช้: {st.session_state.api_provider}")
            else:
                with st.spinner("🤖 AI กำลังประมวลผล..."):
                    try:
                        # Create a simple prompt for testing
                        test_prompt = f"""{custom_prompt}

ให้คำตอบในรูปแบบนี้:
Questions:
1. [คำถามที่ 1]
2. [คำถามที่ 2]
...

Answers:
1. [คำตอบที่ 1]
2. [คำตอบที่ 2]
..."""
                        
                        result = test_generator.ai.generate(test_prompt)
                        
                        if result:
                            st.markdown("### ✅ ผลลัพธ์จาก AI")
                            st.markdown(result)
                            
                            # Parse and show in nice format
                            st.markdown("### 📋 ผลลัพธ์ในรูปแบบตาราง")
                            
                            # Try to parse the response
                            try:
                                parts = result.split("Answers:")
                                if len(parts) >= 2:
                                    questions = [q.strip() for q in parts[0].split("\n") if q.strip() and (q[0].isdigit() or q.startswith("-"))][-5:]
                                    answers = [a.strip() for a in parts[1].split("\n") if a.strip() and (a[0].isdigit() or a.startswith("-"))][-5:]
                                    
                                    if questions and answers:
                                        for i, (q, a) in enumerate(zip(questions, answers), 1):
                                            st.write(f"**{i}.** {q} → {a}")
                            except:
                                st.info("📝 (ดูผลลัพธ์ด้านบนเป็นหลัก)")
                        else:
                            st.error("❌ AI ไม่ได้ส่งคำตอบกลับมา")
                            
                    except Exception as e:
                        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        
        # Tips section
        st.markdown("---")
        st.markdown("""
        ### 💡 เคล็ดลับการเขียน Prompt ที่ดี
        
        1. **ระบุวิชา/หัวข้อชัดเจน** เช่น "คณิตศาสตร์ เรื่องการบวก"
        2. **ระบุระดับชั้น** เช่น "สำหรับนักเรียน ป.3"
        3. **ระบุจำนวนข้อ** เช่น "สร้าง 5 ข้อ"
        4. **ระบุรูปแบบคำตอบ** เช่น "ให้คำตอบพร้อมเฉลย"
        5. **ระบุภาษา** เช่น "คำถามเป็นภาษาไทย"
        """)

if "คณิตศาสตร์" in mode_select:
    st.subheader("📐 สร้างใบงานคณิตศาสตร์ (ตามหลักสูตร สสวท.)")
    
    # Grade Selection
    grade_options = ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6", "ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
    grade_select = st.selectbox("📚 เลือกระดับชั้น:", grade_options)
    
    # Full IPST Curriculum by Grade
    ipst_topics = {
        # ===== ระดับประถมศึกษา =====
        "ป.1": [
            ("1️⃣", "จำนวนนับ 1 ถึง 5 และ 0", "calculation"),
            ("2️⃣", "จำนวนนับ 6 ถึง 9", "calculation"),
            ("3️⃣", "การบวกจำนวนสองจำนวนที่ผลบวกไม่เกิน 9", "calculation"),
            ("4️⃣", "การลบจำนวนสองจำนวนที่ตัวตั้งไม่เกิน 9", "calculation"),
            ("5️⃣", "จำนวนนับ 10 ถึง 20", "calculation"),
            ("6️⃣", "การบวกและการลบจำนวนที่ผลลัพธ์และตัวตั้งไม่เกิน 20", "calculation"),
            ("7️⃣", "การวัดความยาว 🌟", "ai"),
            ("8️⃣", "การชั่ง 🌟", "ai"),
            ("9️⃣", "การตวง 🌟", "ai"),
            ("🔟", "จำนวนนับ 21 ถึง 100", "calculation"),
            ("1️⃣1️⃣", "รูปเรขาคณิต 🌟", "ai"),
            ("1️⃣2️⃣", "เวลา 🌟", "ai"),
            ("1️⃣3️⃣", "การบวกและการลบจำนวนที่ผลลัพธ์และตัวตั้งไม่เกิน 100", "calculation"),
            ("1️⃣4️⃣", "การบวก ลบระคน", "calculation"),
        ],
        "ป.2": [
            ("1️⃣", "จำนวนนับไม่เกิน 1,000", "calculation"),
            ("2️⃣", "การบวกและการลบจำนวนนับที่ผลลัพธ์และตัวตั้งไม่เกิน 100", "calculation"),
            ("3️⃣", "การวัดความยาว 🌟", "ai"),
            ("4️⃣", "การบวกและการลบจำนวนนับที่ผลลัพธ์และตัวตั้งไม่เกิน 1,000", "calculation"),
            ("5️⃣", "การชั่ง 🌟", "ai"),
            ("6️⃣", "การคูณ", "calculation"),
            ("7️⃣", "เวลา 🌟", "ai"),
            ("8️⃣", "เงิน 🌟", "ai"),
            ("9️⃣", "การหาร", "calculation"),
            ("🔟", "การตวง 🌟", "ai"),
            ("1️⃣1️⃣", "รูปเรขาคณิต 🌟", "ai"),
            ("1️⃣2️⃣", "การบวก ลบ คูณ หารระคน", "calculation"),
        ],
        "ป.3": [
            ("1️⃣", "จำนวนนับไม่เกิน 100,000", "calculation"),
            ("2️⃣", "การบวกและการลบจำนวนนับที่ผลลัพธ์และตัวตั้งไม่เกิน 100,000", "calculation"),
            ("3️⃣", "แผนภูมิรูปภาพและแผนภูมิแท่ง 🌟", "ai"),
            ("4️⃣", "การวัดความยาว 🌟", "ai"),
            ("5️⃣", "เวลา 🌟", "ai"),
            ("6️⃣", "การชั่ง การตวง 🌟", "ai"),
            ("7️⃣", "การคูณ", "calculation"),
            ("8️⃣", "การหาร", "calculation"),
            ("9️⃣", "เงินและการบันทึกรายรับรายจ่าย 🌟", "ai"),
            ("🔟", "จุด เส้นตรง รังสี ส่วนของเส้นตรง มุม 🌟", "ai"),
            ("1️⃣1️⃣", "รูปเรขาคณิต 🌟", "ai"),
            ("1️⃣2️⃣", "การบวก ลบ คูณ หารระคน", "calculation"),
        ],
        "ป.4": [
            ("1️⃣", "จำนวนนับที่มากกว่า 100,000", "calculation"),
            ("2️⃣", "การบวกและการลบ", "calculation"),
            ("3️⃣", "เรขาคณิต 🌟", "ai"),
            ("4️⃣", "การคูณ", "calculation"),
            ("5️⃣", "การหาร", "calculation"),
            ("6️⃣", "แผนภูมิรูปภาพ แผนภูมิแท่ง และตาราง 🌟", "ai"),
            ("7️⃣", "การวัด 🌟", "ai"),
            ("8️⃣", "พื้นที่ 🌟", "ai"),
            ("9️⃣", "เงิน 🌟", "ai"),
            ("🔟", "เศษส่วน", "calculation"),
            ("1️⃣1️⃣", "เวลา 🌟", "ai"),
            ("1️⃣2️⃣", "ทศนิยม", "calculation"),
            ("1️⃣3️⃣", "การบวก ลบ คูณ หารระคน", "calculation"),
        ],
        "ป.5": [
            ("1️⃣", "จำนวนนับ และการบวก การลบ การคูณ การหาร", "calculation"),
            ("2️⃣", "มุม 🌟", "ai"),
            ("3️⃣", "เส้นขนาน 🌟", "ai"),
            ("4️⃣", "สถิติและความน่าจะเป็นเบื้องต้น 🌟", "ai"),
            ("5️⃣", "เศษส่วน", "calculation"),
            ("6️⃣", "การบวก การลบ การคูณ การหารเศษส่วน", "calculation"),
            ("7️⃣", "ทศนิยม", "calculation"),
            ("8️⃣", "การบวก การลบ การคูณทศนิยม", "calculation"),
            ("9️⃣", "บทประยุกต์ 🌟", "ai"),
            ("🔟", "รูปสี่เหลี่ยม 🌟", "ai"),
            ("1️⃣1️⃣", "รูปสามเหลี่ยม 🌟", "ai"),
            ("1️⃣2️⃣", "รูปวงกลม 🌟", "ai"),
            ("1️⃣3️⃣", "รูปเรขาคณิตสามมิติและปริมาตรของทรงสี่เหลี่ยมมุมฉาก 🌟", "ai"),
        ],
        "ป.6": [
            ("1️⃣", "จำนวนนับ และการบวก การลบ การคูณ การหาร", "calculation"),
            ("2️⃣", "ตัวประกอบของจำนวนนับ 🌟", "ai"),
            ("3️⃣", "เศษส่วน และการบวก การลบ การคูณ การหาร", "calculation"),
            ("4️⃣", "ทศนิยม", "calculation"),
            ("5️⃣", "การบวก การลบ การคูณ และการหารทศนิยม", "calculation"),
            ("6️⃣", "เส้นขนาน 🌟", "ai"),
            ("7️⃣", "สมการและการแก้สมการ 🌟", "ai"),
            ("8️⃣", "ทิศ แผนที่และแผนผัง 🌟", "ai"),
            ("9️⃣", "รูปสี่เหลี่ยม 🌟", "ai"),
            ("🔟", "รูปวงกลม 🌟", "ai"),
            ("1️⃣1️⃣", "บทประยุกต์ 🌟", "ai"),
            ("1️⃣2️⃣", "รูปเรขาคณิตสามมิติและปริมาตรของทรงสี่เหลี่ยมมุมฉาก 🌟", "ai"),
            ("1️⃣3️⃣", "สถิติและความน่าจะเป็นเบื้องต้น 🌟", "ai"),
        ],
        
        # ===== ระดับมัธยมศึกษาตอนต้น =====
        "ม.1": {
            "เทอม 1": [
                ("1️⃣", "จำนวนเต็ม", "calculation"),
                ("2️⃣", "การสร้างทางเรขาคณิต 🌟", "ai"),
                ("3️⃣", "เลขยกกำลัง", "calculation"),
                ("4️⃣", "ทศนิยมและเศษส่วน", "calculation"),
                ("5️⃣", "รูปเรขาคณิต 2 มิติและ 3 มิติ 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "สมการเชิงเส้นตัวแปรเดียว 🌟", "ai"),
                ("2️⃣", "อัตราส่วน สัดส่วน และร้อยละ", "calculation"),
                ("3️⃣", "กราฟและความสัมพันธ์เชิงเส้น 🌟", "ai"),
                ("4️⃣", "สถิติ (1) 🌟", "ai"),
            ]
        },
        "ม.2": {
            "เทอม 1": [
                ("1️⃣", "ทฤษฎีบทพีทาโกรัส 🌟", "ai"),
                ("2️⃣", "ความรู้เบื้องต้นเกี่ยวกับจำนวนจริง 🌟", "ai"),
                ("3️⃣", "ปริซึมและทรงกระบอก 🌟", "ai"),
                ("4️⃣", "การแปลงทางเรขาคณิต 🌟", "ai"),
                ("5️⃣", "สมบัติของเลขยกกำลัง", "calculation"),
                ("6️⃣", "พหุนาม 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "สถิติ (2) 🌟", "ai"),
                ("2️⃣", "ความเท่ากันทุกประการ 🌟", "ai"),
                ("3️⃣", "เส้นขนาน 🌟", "ai"),
                ("4️⃣", "การให้เหตุผลทางเรขาคณิต 🌟", "ai"),
                ("5️⃣", "การแยกตัวประกอบของพหุนามดีกรีสอง 🌟", "ai"),
            ]
        },
        "ม.3": {
            "เทอม 1": [
                ("1️⃣", "อสมการเชิงเส้นตัวแปรเดียว 🌟", "ai"),
                ("2️⃣", "การแยกตัวประกอบของพหุนามที่มีดีกรีสูงกว่าสอง 🌟", "ai"),
                ("3️⃣", "สมการกำลังสองตัวแปรเดียว 🌟", "ai"),
                ("4️⃣", "ความคล้าย 🌟", "ai"),
                ("5️⃣", "กราฟของฟังก์ชันกำลังสอง 🌟", "ai"),
                ("6️⃣", "สถิติ (3) 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "ระบบสมการเชิงเส้นสองตัวแปร 🌟", "ai"),
                ("2️⃣", "วงกลม 🌟", "ai"),
                ("3️⃣", "พีระมิด กรวย และทรงกลม 🌟", "ai"),
                ("4️⃣", "ความน่าจะเป็น 🌟", "ai"),
                ("5️⃣", "อัตราส่วนตรีโกณมิติ 🌟", "ai"),
            ]
        },
        
        # ===== ระดับมัธยมศึกษาตอนปลาย =====
        "ม.4": {
            "เทอม 1": [
                ("1️⃣", "เซต 🌟", "ai"),
                ("2️⃣", "ตรรกศาสตร์ 🌟", "ai"),
                ("3️⃣", "จำนวนจริง 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "ความสัมพันธ์และฟังก์ชัน 🌟", "ai"),
                ("2️⃣", "ฟังก์ชันเอกซ์โพเนนเชียลและฟังก์ชันลอการิทึม 🌟", "ai"),
                ("3️⃣", "เรขาคณิตวิเคราะห์และภาคตัดกรวย 🌟", "ai"),
            ]
        },
        "ม.5": {
            "เทอม 1": [
                ("1️⃣", "ฟังก์ชันตรีโกณมิติ 🌟", "ai"),
                ("2️⃣", "เมทริกซ์ 🌟", "ai"),
                ("3️⃣", "เวกเตอร์ 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "จำนวนเชิงซ้อน 🌟", "ai"),
                ("2️⃣", "หลักการนับเบื้องต้น 🌟", "ai"),
                ("3️⃣", "ความน่าจะเป็น 🌟", "ai"),
            ]
        },
        "ม.6": {
            "เทอม 1": [
                ("1️⃣", "ลำดับและอนุกรม 🌟", "ai"),
                ("2️⃣", "แคลคูลัสเบื้องต้น 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "ความหมายของสถิติศาสตร์และข้อมูล 🌟", "ai"),
                ("2️⃣", "การวิเคราะห์และนำเสนอข้อมูลเชิงคุณภาพ 🌟", "ai"),
                ("3️⃣", "การวิเคราะห์และนำเสนอข้อมูลเชิงปริมาณ 🌟", "ai"),
                ("4️⃣", "ตัวแปรสุ่มและการแจกแจงความน่าจะเป็น 🌟", "ai"),
            ]
        },
    }
    
    # Check if grade is ม.1-6 (has terms)
    if grade_select in ["ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]:
        # Select term first
        term_options = list(ipst_topics[grade_select].keys())
        term_select = st.selectbox("📅 เลือกเทอม:", term_options)
        topics = ipst_topics[grade_select][term_select]
    else:
        # Primary school grades
        topics = ipst_topics.get(grade_select, [])
    
    # Topic selection with display names
    topic_options = [f"{prefix} {name}" for prefix, name, _ in topics]
    topic_select = st.selectbox("📖 เลือกหัวข้อ:", topic_options)
    
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
        if "การคูณ" in selected_topic:
            op_label = "คูณ (x)"
        elif "การหาร" in selected_topic:
            op_label = "หาร (÷)"
        elif "การลบ" in selected_topic or "ลบระคน" in selected_topic:
            op_label = "ลบ (-)"
        elif "บวก" in selected_topic or "ระคน" in selected_topic:
            op_label = "บวก (+)"
        else:
            op_label = st.selectbox("เลือกเครื่องหมาย", ["บวก (+)", "ลบ (-)", "คูณ (x)", "หาร (÷)"])
        
        # Map Thai label to English key for backend
        op_map = {"บวก (+)": "Addition (+)", "ลบ (-)": "Subtraction (-)", "คูณ (x)": "Multiplication (x)", "หาร (÷)": "Division (÷)"}
        op = op_map.get(op_label, "Addition (+)")
        
        # Auto-config ranges based on grade
        d_min, d_max = 1, 20
        if grade_select == "ป.1":
            if "10 ถึง 20" in selected_topic:
                d_min, d_max = 10, 20
            elif "21 ถึง 100" in selected_topic:
                d_min, d_max = 21, 100
            else:
                d_min, d_max = 1, 20
        elif grade_select == "ป.2":
            if "1,000" in selected_topic:
                d_min, d_max = 100, 1000
            else:
                d_min, d_max = 1, 100
        elif grade_select == "ป.3":
            d_min, d_max = 10, 100000
        elif grade_select in ["ป.4", "ป.5", "ป.6"]:
            d_min, d_max = 100, 100000
        
        num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=20)
        
    # ==== DROPDOWN STRUCTURE ====
    # Create type dropdown
    create_options = [
        "📝 ใบงาน / แบบฝึกหัด (Worksheet)",
        "📚 สรุปเนื้อหา (Summary)",
        "📋 โจทย์ข้อสอบ (Quiz)"
    ]
    create_type = st.selectbox("เลือกประเภทที่ต้องการ:", create_options, key="math_create_type")
    
    # Source dropdown
    source_options = [
        "🤖 AI สร้างให้ (จากหัวข้อ)",
        "📁 จากไฟล์ (PDF/Word)",
        "✏️ จาก Prompt (เขียนเอง)"
    ]
    source_type = st.selectbox("เลือกวิธีสร้าง:", source_options, key="math_source")
    
    # ==== AI SOURCE (TOPIC) ====
    if "AI สร้างให้" in source_type:
        # Custom Prompt Section (for AI topics)
        if selected_type == "ai":
            with st.expander("✏️ ปรับแต่ง Prompt (ไม่บังคับ)", expanded=False):
                custom_prompt = st.text_area(
                    "Prompt สำหรับ AI (ถ้าเว้นว่างจะใช้ค่าเริ่มต้น)",
                    value="",
                    height=100,
                    help="ปรับแต่ง prompt เพื่อให้ได้ผลลัพธ์ตามต้องการ"
                )
                
                st.markdown("**💡 ตัวอย่าง Prompt ที่ดี:**")
                st.code("สร้างโจทย์คณิตศาสตร์ 10 ข้อ เรื่องการบวก สำหรับนักเรียนประถมป.2 ให้โจทย์มีความหลากหลาย เช่น สถานการณ์ในชีวิตจริง ปัญหาที่ต้องคิดวิเคราะห์ และมีเฉลยพร้อมวิธีทำ", language="text")
        
        # Show num_q only if not summary
        num_q = 10
        if "สรุป" not in create_type:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10, key="math_num")
        
        if st.button("🚀 สร้างจาก AI", type="primary", key="math_ai_gen"):
            if selected_type == "ai" and not st.session_state.api_key:
                st.warning("⚠️ ต้องใช้ API Key ค่ะ!")
            else:
                with st.spinner("🤖 AI กำลังสร้าง..."):
                    if "สรุป" in create_type:
                        # Generate summary
                        summary_prompt = f"สรุปเนื้อหาคณิตศาสตร์เรื่อง {selected_topic} สำหรับนักเรียนระดับ {grade_select}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        # Create PDF and Word for summary
                        pdf = generator.create_summary_pdf(title, school_name, "สรุปเนื้อหา", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "สรุปเนื้อหา", summary_result)
                        
                        # Preview section
                        with st.expander("👀 ดูตัวอย่างสรุป", expanded=True):
                            st.markdown("### 📚 สรุปเนื้อหา")
                            st.write(summary_result)
                        
                        st.success("✅ สร้างสรุปสำเร็จ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        # Generate worksheet/quiz
                        if selected_type == "ai":
                            questions, answers = generator.generate_ai_worksheet(selected_topic, grade_select, num_q)
                        else:
                            questions, answers = generator.generate_questions(op, num_q, d_min, d_max)
                        
                        pdf = generator.create_pdf(title, school_name, selected_topic, questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, selected_topic, questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "worksheet"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    
    # ==== FILE SOURCE ====
    elif "ไฟล์" in source_type:
        uploaded_file = st.file_uploader("📁 อัปโหลดไฟล์ (PDF หรือ Word)", type=["pdf", "docx", "doc"], key="math_file")
        
        if uploaded_file:
            with st.spinner("📖 กำลังอ่านไฟล์..."):
                file_content = generator.extract_text_from_file(uploaded_file)
                if file_content and "Error" not in file_content:
                    st.success(f"✅ อ่านไฟล์สำเร็จ! ({len(file_content)} ตัวอักษร)")
        
        num_q = 10
        if "สรุป" not in create_type:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10, key="math_file_num")
        
        if st.button("🚀 สร้างจากไฟล์", type="primary", key="math_file_gen"):
            if not uploaded_file:
                st.warning("⚠️ กรุณาอัปโหลดไฟล์ก่อนค่ะ!")
            else:
                with st.spinner("🤖 AI กำลังสร้าง..."):
                    summarized = generator.summarize_text(file_content, max_length=2000)
                    
                    if "สรุป" in create_type:
                        pdf = generator.create_summary_pdf(title, school_name, "สรุปเนื้อหา", summarized, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "สรุปเนื้อหา", summarized)
                        
                        with st.expander("👀 ดูตัวอย่างสรุป", expanded=True):
                            st.markdown("### 📚 สรุปเนื้อหา")
                            st.write(summarized)
                        
                        st.success("✅ สร้างสรุปสำเร็จ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_quiz_from_text(summarized, num_q)
                        
                        pdf = generator.create_pdf(title, school_name, "Quiz from File", questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, "Quiz from File", questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "math_quiz"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    
    # ==== PROMPT SOURCE ====
    elif "Prompt" in source_type:
        prompt_input = st.text_area("📝 เขียนหัวข้อหรือเนื้อหาที่ต้องการ:", height=100, key="math_prompt")
        
        num_q = 10
        if "สรุป" not in create_type:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10, key="math_prompt_num")
        
        if st.button("🚀 สร้างจาก Prompt", type="primary", key="math_prompt_gen"):
            if not prompt_input:
                st.warning("⚠️ กรุณาเขียนหัวข้อก่อนค่ะ!")
            else:
                with st.spinner("🤖 AI กำลังสร้าง..."):
                    if "สรุป" in create_type:
                        summary_prompt = f"สรุปเนื้อหาคณิตศาสตร์สำหรับนักเรียนระดับ {grade_select}\n\nเนื้อหา:\n{prompt_input}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        pdf = generator.create_summary_pdf(title, school_name, "สรุปเนื้อหา", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "สรุปเนื้อหา", summary_result)
                        
                        with st.expander("👀 ดูตัวอย่างสรุป", expanded=True):
                            st.markdown("### 📚 สรุปเนื้อหา")
                            st.write(summary_result)
                        
                        st.success("✅ สร้างสรุปสำเร็จ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_quiz_from_text(prompt_input, num_q)
                        
                        pdf = generator.create_pdf(title, school_name, "Quiz from Prompt", questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, "Quiz from Prompt", questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "math_quiz"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers

    # Skip the old generation code - handled above
        if st.session_state.generated_pdf is not None:
            st.success("✅ สร้างสำเร็จ!")
            
            # Preview section
            with st.expander("👀 ดูตัวอย่างคำถามและเฉลย", expanded=True):
                st.markdown("### 📝 คำถาม / Questions")
                for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                    st.write(f"**{i}.** {q}")
                if len(st.session_state.preview_questions) > 10:
                    st.write(f"... และอีก {len(st.session_state.preview_questions) - 10} ข้อ")
                
                st.markdown("### ✅ เฉลย / Answers")
                for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                    st.write(f"**{i}.** {a}")
                if len(st.session_state.preview_answers) > 10:
                    st.write(f"... และอีก {len(st.session_state.preview_answers) - 10} ข้อ")
            
            c1, c2 = st.columns(2)
            c1.download_button("📄 ดาวน์โหลด PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
            c2.download_button("📝 ดาวน์โหลด Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            if st.button("🗑️ ล้างและสร้างใหม่"):
                st.session_state.generated_pdf = None
                st.session_state.generated_word = None
                st.session_state.preview_questions = None
                st.session_state.preview_answers = None
                st.rerun()
    
    else:  # AI required topic
        st.info(f"📌 หัวข้อนี้ต้องใช้ AI ในการสร้างแบบฝึกหัดค่ะ")
        st.markdown("ℹ️ **หมายเหตุ:** หัวข้อที่มี 🌟 จะใช้ Google AI ในการสร้างโจทย์และแบบฝึกหัดที่หลากหลาย")
        
        num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=20)
        
        if st.button("🚀 สร้างใบงาน", type="primary"):
            if not st.session_state.api_key:
                st.info("🔑 ต้องใช้ API Key สำหรับหัวข้อนี้ค่ะ กรอก API Key ได้ที่ด้านบนนะคะ")
            else:
                with st.spinner("🤖 AI กำลังสร้างแบบฝึกหัด..."):
                    questions, answers = generator.generate_ai_worksheet(selected_topic, grade_select, num_q)
                    pdf = generator.create_pdf(title, school_name, selected_topic, questions, answers, qr_url, uploaded_logo)
                    word = generator.create_word_doc(title, school_name, selected_topic, questions, answers)
                    
                    st.session_state.generated_pdf = pdf
                    st.session_state.generated_word = word
                    st.session_state.generated_filename = "worksheet"
        
        # Show download buttons if content is generated
        if st.session_state.generated_pdf is not None:
            st.success("สร้างสำเร็จ! ดาวน์โหลดได้ที่ด้านล่าง")
            c1, c2 = st.columns(2)
            c1.download_button("📄 ดาวน์โหลด PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
            c2.download_button("📝 ดาวน์โหลด Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            
            if st.button("🗑️ ล้างและสร้างใหม่"):
                st.session_state.generated_pdf = None
                st.session_state.generated_word = None
                st.rerun()

elif "วิทยาศาสตร์" in mode_select:
    st.subheader("🔬 สร้างใบงานวิทยาศาสตร์ (ตามหลักสูตร สสวท.)")
    
    # Science Curriculum Data
    science_topics = {
        # ===== ระดับประถมศึกษา =====
        "ป.1": [
            ("1️⃣", "สิ่งต่างรอบตัวเรา (สิ่งมีชีวิต, สิ่งไม่มีชีวิต, สมบัติของวัสดุ) 🌟", "ai"),
            ("2️⃣", "พืชรอบตัวเรา (ส่วนประกอบของพืช, การเจริญเติบโต) 🌟", "ai"),
            ("3️⃣", "สัตว์รอบตัวเรา (สัตว์หลากหลายชนิด, การดูแลสัตว์) 🌟", "ai"),
            ("4️⃣", "ดวงดาวและท้องฟ้า (ดวงอาทิตย์, ดวงจันทร์, ดวงดาว) 🌟", "ai"),
            ("5️⃣", "สภาพอากาศ (หนาว, ร้อน, ฝน, ลม) 🌟", "ai"),
        ],
        "ป.2": [
            ("1️⃣", "สิ่งมีชีวิตกับการดำรงชีวิต (อาหาร, ที่อยู่อาศัย, การสืบพันธุ์) 🌟", "ai"),
            ("2️⃣", "สิ่งแวดล้อม (แสง, เสียง, ความร้อน) 🌟", "ai"),
            ("3️⃣", "น้ำและอากาศ (สถานะของน้ำ, การเกิดฝน) 🌟", "ai"),
            ("4️⃣", "ดิน (องค์ประกอบของดิน, ชนิดของดิน) 🌟", "ai"),
            ("5️⃣", "ท้องฟ้าและการพยากรณ์อากาศ (การสังเกตเมฆ, การพยากรณ์อากาศ) 🌟", "ai"),
        ],
        "ป.3": [
            ("1️⃣", "ร่างกายของเรา (ระบบย่อยอาหาร, ระบบหายใจ) 🌟", "ai"),
            ("2️⃣", "พืชกับการดำรงชีวิต (การสังเคราะห์ด้วยแสง, การขยายพันธุ์) 🌟", "ai"),
            ("3️⃣", "สิ่งมีชีวิตกับสิ่งแวดล้อม (ห่วงโซ่อาหาร, สมดุลในธรรมชาติ) 🌟", "ai"),
            ("4️⃣", "วัสดุรอบตัว (โลหะ, ไม้, พลาสติก) 🌟", "ai"),
            ("5️⃣", "แรงและการเคลื่อนที่ (แรงผลัก, แรงดึง, แรงเสียดทาน) 🌟", "ai"),
            ("6️⃣", "พลังงาน (ความร้อน, แสง, เสียง) 🌟", "ai"),
        ],
        "ป.4": [
            ("1️⃣", "ระบบร่างกาย (ระบบหมุนเวียนเลือด, ระบบขับถ่าย) 🌟", "ai"),
            ("2️⃣", "พืชที่หลากหลาย (การจำแนกพืช, การสืบพันธุ์พืช) 🌟", "ai"),
            ("3️⃣", "สิ่งมีชีวิตกับสิ่งแวดล้อม (แหล่งน้ำ, ห่วงโซ่อาหาร) 🌟", "ai"),
            ("4️⃣", "สสาร (สถานะ, การเปลี่ยนแปลง) 🌟", "ai"),
            ("5️⃣", "แรงและความดัน (แรงในธรรมชาติ, ความดันอากาศ) 🌟", "ai"),
            ("6️⃣", "พลังงานไฟฟ้า (ไฟฟ้าพื้นฐาน, วงจรไฟฟ้า) 🌟", "ai"),
        ],
        "ป.5": [
            ("1️⃣", "ระบบสุขภาพ (ฮอร์โมน, การเจริญเติบโต) 🌟", "ai"),
            ("2️⃣", "การสืบพันธุ์ (การสืบพันธุ์สัตว์, การสืบพันธุ์พืช) 🌟", "ai"),
            ("3️⃣", "สิ่งแวดล้อม (การถ่ายทอดพลังงาน, สิ่งมีชีวิตกับสิ่งแวดล้อม) 🌟", "ai"),
            ("4️⃣", "สสาร (อะตอม, ธาตุ, สารประกอบ) 🌟", "ai"),
            ("5️⃣", "แรงและการเคลื่อนที่ (แรงโน้มถ่วง, แรงเสียดทาน) 🌟", "ai"),
            ("6️⃣", "คลื่น (คลื่นเสียง, คลื่นแสง) 🌟", "ai"),
        ],
        "ป.6": [
            ("1️⃣", "ระบบต่อมไร้ท่อ (ฮอร์โมน, ต่อมไร้ท่อสำคัญ) 🌟", "ai"),
            ("2️⃣", "พันธุศาสตร์เบื้องต้น (ลักษณะทางพันธุกรรม, การถ่ายทอดลักษณะ) 🌟", "ai"),
            ("3️⃣", "วิวัฒนาการ (การเปลี่ยนแปลงของสิ่งมีชีวิต) 🌟", "ai"),
            ("4️⃣", "สสารและพลังงาน (กฎทรงพลังงาน, การถ่ายโอนพลังงาน) 🌟", "ai"),
            ("5️⃣", "ระบบสุริยะ (ดาวเคราะห์, การเกิดกลางวัน-กลางคืน) 🌟", "ai"),
            ("6️⃣", "สิ่งแวดล้อม (ทรัพยากรธรรมชาติ, การอนุรักษ์) 🌟", "ai"),
        ],
        
        # ===== ระดับมัธยมศึกษาตอนต้น =====
        "ม.1": {
            "เทอม 1": [
                ("1️⃣", "สารบริสุทธิ์ 🌟", "ai"),
                ("2️⃣", "หน่วยพื้นฐานของสิ่งมีชีวิต 🌟", "ai"),
                ("3️⃣", "หน่วยพื้นฐานของการดำรงชีวิตของพืช 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "พลังงานความร้อน 🌟", "ai"),
                ("2️⃣", "กระบวนการเปลี่ยนแปลงลมฟ้าอากาศ 🌟", "ai"),
            ]
        },
        "ม.2": {
            "เทอม 1": [
                ("1️⃣", "สารละลาย 🌟", "ai"),
                ("2️⃣", "ร่างกายมนุษย์ 🌟", "ai"),
                ("3️⃣", "การเคลื่อนที่และแรง 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "งานและพลังงาน 🌟", "ai"),
                ("2️⃣", "การแยกสาร 🌟", "ai"),
                ("3️⃣", "โลกและการเปลี่ยนแปลง 🌟", "ai"),
            ]
        },
        "ม.3": {
            "เทอม 1": [
                ("1️⃣", "พันธุศาสตร์ 🌟", "ai"),
                ("2️⃣", "คลื่นและแสง 🌟", "ai"),
                ("3️⃣", "ระบบสุริยะของเรา 🌟", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "ปฏิกิริยาเคมีและวัสดุในชีวิตประจำวัน 🌟", "ai"),
                ("2️⃣", "ไฟฟ้า 🌟", "ai"),
                ("3️⃣", "ระบบนิเวศและความหลากหลายทางชีวภาพ 🌟", "ai"),
            ]
        },
    }
    
    # Grade Selection
    science_grade_options = ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6", "ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
    science_grade = st.selectbox("📚 เลือกระดับชั้น:", science_grade_options)
    
    # ม.4-6 Subject Selector (เคมี ฟิสิกส์ ชีวะ)
    if science_grade in ["ม.4", "ม.5", "ม.6"]:
        subject_options = ["เคมี (Chemistry)", "ฟิสิกส์ (Physics)", "ชีววิทยา (Biology)"]
        science_subject = st.selectbox("🧪 เลือกวิชา:", subject_options)
        
        # Get subject key
        subject_key = science_subject.split(" (")[0]  # "เคมี", "ฟิสิกส์", or "ชีววิทยา"
    
    # Check if grade is ม.1-3 (has terms) or ม.4-6 (has subjects)
    if science_grade in ["ม.1", "ม.2", "ม.3"]:
        # Select term first
        science_term_options = list(science_topics[science_grade].keys())
        science_term = st.selectbox("📅 เลือกเทอม:", science_term_options)
        science_topics_list = science_topics[science_grade][science_term]
        selected_grade_level = science_grade
    elif science_grade in ["ม.4", "ม.5", "ม.6"]:
        # ม.4-6: Select term first
        science_term_options = ["เทอม 1", "เทอม 2"]
        science_term = st.selectbox("📅 เลือกเทอม:", science_term_options)
        
        # Get topics based on subject and grade
        science_topics_list = []
        
        # ===== เคมี (Chemistry) ม.4-6 =====
        if subject_key == "เคมี":
            if science_grade == "ม.4":
                science_topics_list = [
                    ("1️⃣", "อะตอมและสมบัติของธาตุ 🌟", "ai"),
                    ("2️⃣", "พันธะเคมี 🌟", "ai"),
                    ("3️⃣", "ปริมาณสัมพันธ์ในปฏิกิริยาเคมี 🌟", "ai"),
                ]
            elif science_grade == "ม.5":
                science_topics_list = [
                    ("1️⃣", "สมบัติของก๊าซและสมการเคมี 🌟", "ai"),
                    ("2️⃣", "อัตราการเกิดปฏิกิริยาเคมี 🌟", "ai"),
                    ("3️⃣", "สมดุลเคมี 🌟", "ai"),
                    ("4️⃣", "กรด-เบส 🌟", "ai"),
                ]
            elif science_grade == "ม.6":
                science_topics_list = [
                    ("1️⃣", "ไฟฟ้าเคมี 🌟", "ai"),
                    ("2️⃣", "ธาตุอินทรีย์และสารชีวโมเลกุล 🌟", "ai"),
                    ("3️⃣", "เคมีอินทรีย์ 🌟", "ai"),
                ]
        
        # ===== ฟิสิกส์ (Physics) ม.4-6 =====
        elif subject_key == "ฟิสิกส์":
            if science_grade == "ม.4":
                science_topics_list = [
                    ("1️⃣", "การเคลื่อนที่แนวตรง 🌟", "ai"),
                    ("2️⃣", "แรงและกฎการเคลื่อนที่ 🌟", "ai"),
                    ("3️⃣", "งานและพลังงาน 🌟", "ai"),
                    ("4️⃣", "โมเมนตัมและการชน 🌟", "ai"),
                ]
            elif science_grade == "ม.5":
                science_topics_list = [
                    ("1️⃣", "การเคลื่อนที่ในระบบต่างๆ (วงกลม, โค้ง, สั่น) 🌟", "ai"),
                    ("2️⃣", "แรงในธรรมชาติ 🌟", "ai"),
                    ("3️⃣", "คลื่น 🌟", "ai"),
                    ("4️⃣", "เสียง 🌟", "ai"),
                    ("5️⃣", "แสง 🌟", "ai"),
                ]
            elif science_grade == "ม.6":
                science_topics_list = [
                    ("1️⃣", "ไฟฟ้าสถิตและไฟฟ้ากระแส 🌟", "ai"),
                    ("2️⃣", "แม่เหล็กไฟฟ้า 🌟", "ai"),
                    ("3️⃣", "ฟิสิกส์อะตอม 🌟", "ai"),
                    ("4️⃣", "ฟิสิกส์นิวเคลียร์ 🌟", "ai"),
                ]
        
        # ===== ชีววิทยา (Biology) ม.4-6 =====
        elif subject_key == "ชีววิทยา":
            if science_grade == "ม.4":
                science_topics_list = [
                    ("1️⃣", "ระบบย่อยอาหาร 🌟", "ai"),
                    ("2️⃣", "ระบบหายใจ 🌟", "ai"),
                    ("3️⃣", "ระบบหมุนเวียนเลือด 🌟", "ai"),
                    ("4️⃣", "ระบบขับถ่าย 🌟", "ai"),
                    ("5️⃣", "ระบบประสาท 🌟", "ai"),
                    ("6️⃣", "ระบบต่อมไร้ท่อ 🌟", "ai"),
                ]
            elif science_grade == "ม.5":
                science_topics_list = [
                    ("1️⃣", "การถ่ายทอดสารภายในร่างกาย 🌟", "ai"),
                    ("2️⃣", "ระบบภูมิคุ้มกัน 🌟", "ai"),
                    ("3️⃣", "การสืบพันธุ์และพัฒนาการ 🌟", "ai"),
                    ("4️⃣", "การถ่ายทอดลักษณะทางพันธุกรรม 🌟", "ai"),
                ]
            elif science_grade == "ม.6":
                science_topics_list = [
                    ("1️⃣", "พันธุศาสตร์ 🌟", "ai"),
                    ("2️⃣", "พันธุกรรมเทคโนโลยี 🌟", "ai"),
                    ("3️⃣", "วิวัฒนาการ 🌟", "ai"),
                    ("4️⃣", "นิเวศวิทยา 🌟", "ai"),
                    ("5️⃣", "สิ่งแวดล้อม 🌟", "ai"),
                ]
        
        selected_grade_level = f"{science_grade} {subject_key}"
    else:
        # Primary school grades
        science_topics_list = science_topics.get(science_grade, [])
        selected_grade_level = science_grade
    
    # Topic selection with display names
    science_topic_options = [f"{prefix} {name}" for prefix, name, _ in science_topics_list]
    science_topic_select = st.selectbox("📖 เลือกหัวข้อ:", science_topic_options)
    
    # Get selected topic details
    selected_science_topic = None
    for prefix, name, topic_type in science_topics_list:
        full_name = f"{prefix} {name}"
        if full_name == science_topic_select:
            # Remove 🌟 for backend
            clean_name = name.replace(" 🌟", "")
            selected_science_topic = clean_name
            selected_science_type = topic_type
            break
    
    # Show AI requirement message only once
    st.info("📌 หัวข้อวิทยาศาสตร์ทั้งหมดต้องใช้ AI ในการสร้างแบบฝึกหัดค่ะ")
    st.markdown("ℹ️ **หมายเหตุ:** วิทยาศาสตร์ใช้ AI ในการสร้างโจทย์และแบบฝึกหัดที่หลากหลาย")
    
    # ==== Create Type Dropdown ====
    create_options = [
        "📝 ใบงาน / แบบฝึกหัด (Worksheet)",
        "📚 สรุปเนื้อหา (Summary)",
        "📋 โจทย์ข้อสอบ (Quiz)"
    ]
    create_type = st.selectbox("เลือกประเภทที่ต้องการ:", create_options, key="science_create_type")
    
    # ==== Source Dropdown ====
    source_options = [
        "🤖 AI สร้างให้ (จากหัวข้อ)",
        "📁 จากไฟล์ (PDF/Word)",
        "✏️ จาก Prompt (เขียนเอง)"
    ]
    source_type = st.selectbox("เลือกวิธีสร้าง:", source_options, key="science_source")
    
    # ==== Handle Source Types ====
    
    # ==== AI SOURCE (TOPIC) ====
    if "AI สร้างให้" in source_type:
        # Show num_q only if not summary
        num_q = 10
        if "สรุป" not in create_type:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10, key="science_num")
        
        if st.button("🚀 สร้างจาก AI", type="primary", key="science_ai_gen"):
            if not st.session_state.api_key:
                st.warning("⚠️ ต้องใช้ API Key ค่ะ!")
            else:
                with st.spinner("🤖 AI กำลังสร้าง..."):
                    if "สรุป" in create_type:
                        # Generate summary
                        summary_prompt = f"สรุปเนื้อหาวิทยาศาสตร์เรื่อง {selected_science_topic} สำหรับนักเรียนระดับ {science_grade}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        # Create PDF and Word for summary
                        pdf = generator.create_summary_pdf(title, school_name, "สรุปเนื้อหา", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "สรุปเนื้อหา", summary_result)
                        
                        # Preview section
                        with st.expander("👀 ดูตัวอย่างสรุป", expanded=True):
                            st.markdown("### 📚 สรุปเนื้อหา")
                            st.write(summary_result)
                        
                        st.success("✅ สร้างสรุปสำเร็จ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        # Generate worksheet/quiz
                        grade_context = {
                            "ป.1": "Grade 1", "ป.2": "Grade 2", "ป.3": "Grade 3",
                            "ป.4": "Grade 4", "ป.5": "Grade 5", "ป.6": "Grade 6",
                            "ม.1": "Grade 7", "ม.2": "Grade 8", "ม.3": "Grade 9",
                        }
                        
                        if science_grade in ["ม.4", "ม.5", "ม.6"]:
                            if subject_key == "เคมี":
                                questions, answers = generator.generate_chemistry_worksheet(selected_science_topic, science_grade, num_q)
                            elif subject_key == "ฟิสิกส์":
                                questions, answers = generator.generate_physics_worksheet(selected_science_topic, science_grade, num_q)
                            elif subject_key == "ชีววิทยา":
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
    elif "ไฟล์" in source_type:
        uploaded_file = st.file_uploader("📁 อัปโหลดไฟล์ (PDF หรือ Word)", type=["pdf", "docx", "doc"], key="science_file")
        
        if uploaded_file:
            with st.spinner("📖 กำลังอ่านไฟล์..."):
                file_content = generator.extract_text_from_file(uploaded_file)
                if file_content and "Error" not in file_content:
                    st.success(f"✅ อ่านไฟล์สำเร็จ! ({len(file_content)} ตัวอักษร)")
        
        num_q = 10
        if "สรุป" not in create_type:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10, key="science_file_num")
        
        if st.button("🚀 สร้างจากไฟล์", type="primary", key="science_file_gen"):
            if not uploaded_file:
                st.warning("⚠️ กรุณาอัปโหลดไฟล์ก่อนค่ะ!")
            else:
                with st.spinner("🤖 AI กำลังสร้าง..."):
                    summarized = generator.summarize_text(file_content, max_length=2000)
                    
                    if "สรุป" in create_type:
                        pdf = generator.create_summary_pdf(title, school_name, "สรุปเนื้อหา", summarized, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "สรุปเนื้อหา", summarized)
                        
                        with st.expander("👀 ดูตัวอย่างสรุป", expanded=True):
                            st.markdown("### 📚 สรุปเนื้อหา")
                            st.write(summarized)
                        
                        st.success("✅ สร้างสรุปสำเร็จ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
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
        prompt_input = st.text_area("📝 เขียนหัวข้อหรือเนื้อหาที่ต้องการ:", height=100, key="science_prompt")
        
        num_q = 10
        if "สรุป" not in create_type:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10, key="science_prompt_num")
        
        if st.button("🚀 สร้างจาก Prompt", type="primary", key="science_prompt_gen"):
            if not prompt_input:
                st.warning("⚠️ กรุณาเขียนหัวข้อก่อนค่ะ!")
            else:
                with st.spinner("🤖 AI กำลังสร้าง..."):
                    if "สรุป" in create_type:
                        summary_prompt = f"สรุปเนื้อหาวิทยาศาสตร์สำหรับนักเรียนระดับ {science_grade}\n\nเนื้อหา:\n{prompt_input}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        pdf = generator.create_summary_pdf(title, school_name, "สรุปเนื้อหา", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "สรุปเนื้อหา", summary_result)
                        
                        with st.expander("👀 ดูตัวอย่างสรุป", expanded=True):
                            st.markdown("### 📚 สรุปเนื้อหา")
                            st.write(summary_result)
                        
                        st.success("✅ สร้างสรุปสำเร็จ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    else:
                        questions, answers = generator.generate_quiz_from_text(prompt_input, num_q)
                        
                        pdf = generator.create_pdf(title, school_name, "Quiz from Prompt", questions, answers, qr_url, uploaded_logo)
                        word = generator.create_word_doc(title, school_name, "Quiz from Prompt", questions, answers)
                        
                        st.session_state.generated_pdf = pdf
                        st.session_state.generated_word = word
                        st.session_state.generated_filename = "science_quiz"
                        st.session_state.preview_questions = questions
                        st.session_state.preview_answers = answers
    # Show preview and download buttons if content is generated
    if st.session_state.generated_pdf is not None and st.session_state.get("generated_filename") == "science_worksheet":
        st.success("✅ สร้างใบงานวิทยาศาสตร์สำเร็จ!")
        
        # Preview section
        with st.expander("👀 ดูตัวอย่างคำถามและเฉลย", expanded=True):
            st.markdown("### 📝 คำถาม / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_questions) - 10} ข้อ")
            
            st.markdown("### ✅ เฉลย / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_answers) - 10} ข้อ")
        
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("🗑️ ล้างและสร้างใหม่"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "ภาษาไทย" in mode_select:
    st.subheader("📚 สร้างใบงานภาษาไทย (ตามหลักสูตรกระทรวงศึกษาธิการ)")
    
    # Thai Language Curriculum Data
    thai_topics = {
        # ===== ระดับประถมศึกษา =====
        "ป.1": [
            ("1️⃣", "ตัวอักษรไทย (พยัญชนะไทย 44 ตัว, สระ 32 รูป)", "ai"),
            ("2️⃣", "สระในภาษาไทย (สระเดี่ยว, สระประสม)", "ai"),
            ("3️⃣", "การอ่านออกเสียง (อ่านคาบวรรณยุกต์)", "ai"),
            ("4️⃣", "คำศัพท์พื้นฐาน (คำสิ่งของ, คำสัตว์, คำครอบครัว)", "ai"),
            ("5️⃣", "ประโยคและเรื่องสั้น (ประโยคสั้น, นิทานสั้น)", "ai"),
        ],
        "ป.2": [
            ("1️⃣", "คำและความหมาย (คำซ้ำ, คำตรงข้าม, คำพ้อง)", "ai"),
            ("2️⃣", "หน่วยคำสรรพนาม (สรรพนาม, คำสรรพนามสรรพบุรณ)", "ai"),
            ("3️⃣", "การเขียน (เขียนตามคำบอก, เขียนประโยค)", "ai"),
            ("4️⃣", "นิทานพื้นบ้าน (นิทานชาดก, นิทานพื้นบ้านไทย)", "ai"),
            ("5️⃣", "การอ่านจับใจความ (อ่านเรื่องสั้น, ตอบคำถาม)", "ai"),
        ],
        "ป.3": [
            ("1️⃣", "ชนิดของคำ (คำนาม, คำกริยา, คำคุณศัพท์)", "ai"),
            ("2️⃣", "กลอนแปด (โครงสร้างกลอนแปด, คำครุ-ลหุ)", "ai"),
            ("3️⃣", "การเขียนเรียงความ (เขียนเรียงความสั้น)", "ai"),
            ("4️⃣", "คำราชาศัพท์เบื้องต้น (คำขึ้นต้น-ลงท้าย)", "ai"),
            ("5️⃣", "วรรณคดีไทย (ขุนช้างขุนแผน, สุภาษิตไทย)", "ai"),
        ],
        "ป.4": [
            ("1️⃣", "หน่วยคำและความหมาย (คำภาษาต่างประเทศ, คำยืม)", "ai"),
            ("2️⃣", "ชนิดของคำ (คำสรรพนาม, คำสันธาน, คำบุพบท)", "ai"),
            ("3️⃣", "การอ่านตีความ (อ่านบทความ, อ่านข่าว)", "ai"),
            ("4️⃣", "การเขียนจดหมาย (จดหมายขอบคุณ, จดหมายเชิญ)", "ai"),
            ("5️⃣", "กลอนสุภาพ (โครงสร้างกลอนสุภาพ)", "ai"),
        ],
        "ป.5": [
            ("1️⃣", "ประโยคและองค์ประกอบ (องค์ประโยค, ชนิดของประโยค)", "ai"),
            ("2️⃣", "วลีและอนุประโยค (วลีนาม, วลีกริยา)", "ai"),
            ("3️⃣", "การเขียนรายงาน (รายงานการศึกษา, รายงานข่าว)", "ai"),
            ("4️⃣", "วรรณคดีสุนทรียภาพ (กาพย์กลอนบทร้อยกรอง)", "ai"),
            ("5️⃣", "ภาษาถิ่น (ภาษาอีสาน, ภาษาเหนือ, ภาษาใต้)", "ai"),
        ],
        "ป.6": [
            ("1️⃣", "หลักการใช้คำ (คำราชาศัพท์, คำสุภาพ)", "ai"),
            ("2️⃣", "การเขียนเชิงสร้างสรรค์ (เรียงความ, นิทานสั้น)", "ai"),
            ("3️⃣", "การอ่านวิเคราะห์ (วิเคราะห์เรื่อง, วิเคราะห์ข่าว)", "ai"),
            ("4️⃣", "วรรณคดีวรรณกรรม (วรรณกรรมระดับชาติ)", "ai"),
            ("5️⃣", "การนำเสนอ (การพูด, การนำเสนอข้อมูล)", "ai"),
        ],
        
        # ===== ระดับมัธยมศึกษาตอนต้น =====
        "ม.1": {
            "เทอม 1": [
                ("1️⃣", "หน่วยคำสรรพนาม (การใช้สรรพนามในบริบทต่างๆ)", "ai"),
                ("2️⃣", "การเปลี่ยนรูปคำ (การผันคำกริยา, การลดรูปคำ)", "ai"),
                ("3️⃣", "วลีและอนุประโยค (วลีขยาย, อนุประโยค)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "วรรณคดี (ร้อยกรองไทย, กาพย์ยานเอก)", "ai"),
                ("2️⃣", "การอ่าน-เขียน (อ่านบทความ, เขียนเรียงความ)", "ai"),
            ]
        },
        "ม.2": {
            "เทอม 1": [
                ("1️⃣", "คำและประโยคซ้อน (ประโยคซ้อน, ประโยคซ้อนกลบ)", "ai"),
                ("2️⃣", "กลอนแปด-กลอนสุภาพ (การแต่งกลอน, สัมผัสกลอน)", "ai"),
                ("3️⃣", "วรรณคดีอีสาน (ลิเก, โขน, หนังใหญ่)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "การเขียนเชิงสร้างสรรค์ (เขียนนิยายสั้น, บทละคร)", "ai"),
                ("2️⃣", "ภาษาถิ่นและภาษากลาง (ความแตกต่าง, การใช้)", "ai"),
            ]
        },
        "ม.3": {
            "เทอม 1": [
                ("1️⃣", "ภาษากับสังคม (ภาษาและอำนาจ, ภาษาและเพศสภาพ)", "ai"),
                ("2️⃣", "วรรณคดีไทย (นิทานรามเกียรติ์, ขุนช้างขุนแผน)", "ai"),
                ("3️⃣", "การอ่านวิพากษ์ (วิพากษ์บทความ, วิพากษ์ข่าว)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "การเขียนวิชาการ (รายงานวิจัย, บทความวิชาการ)", "ai"),
                ("2️⃣", "วาทีวิทยา (การโต้แย้ง, การเขียนข้อเสนอ)", "ai"),
            ]
        },
        
        # ===== ระดับมัธยมศึกษาตอนปลาย =====
        "ม.4": {
            "เทอม 1": [
                ("1️⃣", "ภาษากับการสื่อสาร (ภาษาในองค์กร, ภาษาธุรกิจ)", "ai"),
                ("2️⃣", "หลักภาษาไทย (ทฤษฎีภาษา, ภาษากับความคิด)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "วรรณคดีร่วมสมัย (นิยายไทยร่วมสมัย)", "ai"),
                ("2️⃣", "การเขียนเชิงวิชาการ (บทความวิเคราะห์)", "ai"),
                ("3️⃣", "สื่อและภาษา (ภาษาโฆษณา, ภาษาสื่อ)", "ai"),
            ]
        },
        "ม.5": {
            "เทอม 1": [
                ("1️⃣", "วรรณคดีไทยและอาเซียน (วรรณคดีอาเซียน)", "ai"),
                ("2️⃣", "ภาษาและวัฒนธรรม (ภาษากับวัฒนธรรมไทย)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "การนำเสนอ (การพูดในที่สาธารณะ)", "ai"),
                ("2️⃣", "การเขียนสร้างสรรค์ (บทละคร, บทภาพยนตร์)", "ai"),
                ("3️⃣", "วาทีวิทยา (การโต้วาที, การเขียนข้อเสนอ)", "ai"),
            ]
        },
        "ม.6": {
            "เทอม 1": [
                ("1️⃣", "ภาษากับเทคโนโลยี (ภาษาอินเทอร์เน็ต, ภาษาโซเชียล)", "ai"),
                ("2️⃣", "ภาษาและอาชีพ (ภาษาสำหรับอาชีพต่างๆ)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "วรรณคดีและภาพยนตร์ (การดัดแปลงวรรณคดี)", "ai"),
                ("2️⃣", "การเขียนเพื่อสื่อสาร (บทความสารคดี)", "ai"),
                ("3️⃣", "การประเมินผลงานภาษา (การวิจารณ์, การประเมิน)", "ai"),
            ]
        },
    }
    
    # Grade Selection
    thai_grade_options = ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6", "ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
    thai_grade_select = st.selectbox("📚 เลือกระดับชั้น:", thai_grade_options)
    
    # Check if grade is ม.1-6 (has terms)
    if thai_grade_select in ["ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]:
        # Select term first
        thai_term_options = list(thai_topics[thai_grade_select].keys())
        thai_term_select = st.selectbox("📅 เลือกเทอม:", thai_term_options)
        thai_topics_list = thai_topics[thai_grade_select][thai_term_select]
        selected_thai_grade = thai_grade_select
    else:
        # Primary school grades
        thai_topics_list = thai_topics.get(thai_grade_select, [])
        selected_thai_grade = thai_grade_select
    
    # Topic selection with display names
    thai_topic_options = [f"{prefix} {name}" for prefix, name, _ in thai_topics_list]
    thai_topic_select = st.selectbox("📖 เลือกหัวข้อ:", thai_topic_options)
    
    # Get selected topic details
    selected_thai_topic = None
    for prefix, name, topic_type in thai_topics_list:
        full_name = f"{prefix} {name}"
        if full_name == thai_topic_select:
            selected_thai_topic = name
            break
    
    # Show AI requirement message only once
    st.info("📌 หัวข้อภาษาไทยทั้งหมดต้องใช้ AI ในการสร้างแบบฝึกหัดค่ะ")
    
    # Exercise type selector
    exercise_types = [
        "ทั้งหมด (ผสมผสาน)",
        "การเขียน (Writing Exercises)",
        "การอ่าน (Reading Comprehension)",
        "หลักภาษา (Grammar Exercises)",
        "คำศัพท์ (Vocabulary)",
        "วรรณคดี (Literature)"
    ]
    exercise_type = st.selectbox("📝 เลือกประเภทแบบฝึกหัด:", exercise_types)
    
    num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=20)
    
    # Custom Prompt Section
    with st.expander("✏️ ปรับแต่ง Prompt (ไม่บังคับ)", expanded=False):
        thai_prompt = st.text_area(
            "Prompt สำหรับ AI (ถ้าเว้นว่างจะใช้ค่าเริ่มต้น)",
            value="",
            height=100,
            help="ปรับแต่ง prompt เพื่อให้ได้ผลลัพธ์ตามต้องการ"
        )
        
        st.markdown("**💡 ตัวอย่าง Prompt ที่ดี:**")
        st.code("สร้างแบบฝึกหัดภาษาไทย 10 ข้อ เรื่องคำนาม สำหรับนักเรียนป.2 ให้มีคำถามหลากหลายรูปแบบ ทั้งเติมคำในช่องว่าง จับคู่คำนามกับคำอธิบาย และแบบถูก-ผิด", language="text")
    
    if st.button("🚀 สร้างใบงานภาษาไทย", type="primary"):
        if not st.session_state.api_key:
            st.info("🔑 ต้องใช้ API Key สำหรับหัวข้อภาษาไทยค่ะ กรอก API Key ได้ที่ด้านบนนะคะ")
        else:
            with st.spinner("🤖 AI กำลังสร้างแบบฝึกหัดภาษาไทย..."):
                # Map exercise type to prompt
                exercise_mapping = {
                    "ทั้งหมด (ผสมผสาน)": "mix",
                    "การเขียน (Writing Exercises)": "writing",
                    "การอ่าน (Reading Comprehension)": "reading",
                    "หลักภาษา (Grammar Exercises)": "grammar",
                    "คำศัพท์ (Vocabulary)": "vocabulary",
                    "วรรณคดี (Literature)": "literature"
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
        st.success("✅ สร้างใบงานภาษาไทยสำเร็จ!")
        
        # Preview section
        with st.expander("👀 ดูตัวอย่างคำถามและเฉลย", expanded=True):
            st.markdown("### 📝 คำถาม / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_questions) - 10} ข้อ")
            
            st.markdown("### ✅ เฉลย / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_answers) - 10} ข้อ")
        
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("🗑️ ล้างและสร้างใหม่"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "ภาษาอังกฤษ" in mode_select:
    st.subheader("🌏 สร้างใบงานภาษาอังกฤษ (English Language)")
    
    # English Language Curriculum Data
    english_topics = {
        # ===== ระดับประถมศึกษา =====
        "ป.1": [
            ("1️⃣", "Alphabet (A-Z uppercase/lowercase)", "ai"),
            ("2️⃣", "Phonics (Aa-Zz sounds)", "ai"),
            ("3️⃣", "Numbers 1-10 (counting)", "ai"),
            ("4️⃣", "Colors (Red, blue, green, yellow, etc.)", "ai"),
            ("5️⃣", "Shapes (Circle, square, triangle, etc.)", "ai"),
            ("6️⃣", "Body Parts (Head, eyes, ears, nose, etc.)", "ai"),
            ("7️⃣", "Family (Mother, father, sister, brother)", "ai"),
            ("8️⃣", "Animals (Cat, dog, bird, fish, etc.)", "ai"),
        ],
        "ป.2": [
            ("1️⃣", "Numbers 11-100 (counting)", "ai"),
            ("2️⃣", "Days & Months (Monday-Sunday, Jan-Dec)", "ai"),
            ("3️⃣", "Time (O'clock, half past)", "ai"),
            ("4️⃣", "Food & Drinks (Rice, bread, water, milk)", "ai"),
            ("5️⃣", "Clothing (Shirt, pants, dress, shoes)", "ai"),
            ("6️⃣", "Weather (Hot, cold, rainy, sunny)", "ai"),
            ("7️⃣", "Places (School, home, market, hospital)", "ai"),
            ("8️⃣", "Greetings (Hello, goodbye, thank you)", "ai"),
        ],
        "ป.3": [
            ("1️⃣", "Present Simple (I am, you are, he/she is)", "ai"),
            ("2️⃣", "This-That-These-Those", "ai"),
            ("3️⃣", "Have-Has (possession)", "ai"),
            ("4️⃣", "Prepositions (In, on, under, behind)", "ai"),
            ("5️⃣", "WH-Questions (What, Where, When, Why, Who)", "ai"),
            ("6️⃣", "Daily Routines (Wake up, eat breakfast)", "ai"),
            ("7️⃣", "Occupations (Doctor, teacher, farmer)", "ai"),
            ("8️⃣", "Adjectives (Big, small, tall, beautiful)", "ai"),
        ],
        "ป.4": [
            ("1️⃣", "Past Simple (was/were)", "ai"),
            ("2️⃣", "Regular Verbs (Played, watched, cleaned)", "ai"),
            ("3️⃣", "Irregular Verbs (Went, ate, drank, saw)", "ai"),
            ("4️⃣", "Object Pronouns (Me, him, her, us, them)", "ai"),
            ("5️⃣", "There is-There are", "ai"),
            ("6️⃣", "Commands (Open the door, close the window)", "ai"),
            ("7️⃣", "Descriptions (Describing people/things)", "ai"),
            ("8️⃣", "School Subjects (Math, English, Science, Art)", "ai"),
        ],
        "ป.5": [
            ("1️⃣", "Future Will-Going to", "ai"),
            ("2️⃣", "Present Continuous (am/is/are + verb-ing)", "ai"),
            ("3️⃣", "Can-Could (ability, permission)", "ai"),
            ("4️⃣", "Some-Any", "ai"),
            ("5️⃣", "Telling Time (Quarter past, quarter to)", "ai"),
            ("6️⃣", "Giving Directions (Turn left, turn right)", "ai"),
            ("7️⃣", "Invitations (Would you like...?, Let's...)", "ai"),
            ("8️⃣", "Letter Writing (Formal and informal)", "ai"),
        ],
        "ป.6": [
            ("1️⃣", "Tenses Review (Present, Past, Future)", "ai"),
            ("2️⃣", "Modal Verbs (Must, should, have to, may)", "ai"),
            ("3️⃣", "Passive Voice (is/are + verb3)", "ai"),
            ("4️⃣", "If Clauses (Conditionals type 1)", "ai"),
            ("5️⃣", "Reported Speech (Said, told, asked)", "ai"),
            ("6️⃣", "Conjunctions (And, but, or, because, so)", "ai"),
            ("7️⃣", "Reading Comprehension (Passages, questions)", "ai"),
            ("8️⃣", "Paragraph Writing (3-5 sentences)", "ai"),
        ],
        
        # ===== ระดับมัธยมศึกษาตอนต้น =====
        "ม.1": {
            "เทอม 1": [
                ("1️⃣", "Present Perfect (have/has + verb3)", "ai"),
                ("2️⃣", "Since-For (time expressions)", "ai"),
                ("3️⃣", "Tag Questions (aren't you?, isn't it?)", "ai"),
                ("4️⃣", "Relative Clauses (Who, which, that)", "ai"),
                ("5️⃣", "Gerunds & Infinitives", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "Making Suggestions (Let's, Why don't we)", "ai"),
                ("2️⃣", "Phone Conversations", "ai"),
                ("3️⃣", "Shopping & Money", "ai"),
                ("4️⃣", "Travel & Transportation 🌟", "ai"),
                ("5️⃣", "Health & Fitness 🌟", "ai"),
            ]
        },
        "ม.2": {
            "เทอม 1": [
                ("1️⃣", "Past Continuous (was/were + verb-ing)", "ai"),
                ("2️⃣", "Future Continuous (will be + verb-ing)", "ai"),
                ("3️⃣", "Conditionals Type 2 (If I were, I would)", "ai"),
                ("4️⃣", "Reported Questions", "ai"),
                ("5️⃣", "Quantifiers (Much, many, a few, a little)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "Comparison (Adjectives, adverbs)", "ai"),
                ("2️⃣", "Wish Sentences (I wish I could...)", "ai"),
                ("3️⃣", "Email Writing (Formal and informal)", "ai"),
                ("4️⃣", "News Writing 🌟", "ai"),
                ("5️⃣", "Story Writing 🌟", "ai"),
            ]
        },
        "ม.3": {
            "เทอม 1": [
                ("1️⃣", "Conditionals All Types (Type 1, 2, 3)", "ai"),
                ("2️⃣", "Passive Voice (All tenses)", "ai"),
                ("3️⃣", "Reported Speech (All reporting verbs)", "ai"),
                ("4️⃣", "Gerunds & Infinitives (Special uses)", "ai"),
                ("5️⃣", "Modal Perfects (Should have, could have)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "Articles (A, an, the, zero article)", "ai"),
                ("2️⃣", "Essay Writing (Opinion, comparison)", "ai"),
                ("3️⃣", "O-NET Preparation (Grammar, vocabulary)", "ai"),
                ("4️⃣", "Critical Reading 🌟", "ai"),
                ("5️⃣", "Creative Writing 🌟", "ai"),
            ]
        },
        
        # ===== ระดับมัธยมศึกษาตอนปลาย =====
        "ม.4": {
            "เทอม 1": [
                ("1️⃣", "Narrative Tenses (Past perfect)", "ai"),
                ("2️⃣", "Future Perfect (will have + verb3)", "ai"),
                ("3️⃣", "Mixed Conditionals", "ai"),
                ("4️⃣", "Wish-Remorse (I wish I had...)", "ai"),
                ("5️⃣", "Linking Words (However, although, despite)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "Paragraph Development", "ai"),
                ("2️⃣", "Speaking: Opinions (I think, In my opinion)", "ai"),
                ("3️⃣", "Vocabulary 1500 (Word families, synonyms)", "ai"),
                ("4️⃣", "Academic Vocabulary 🌟", "ai"),
                ("5️⃣", "Debating Skills 🌟", "ai"),
            ]
        },
        "ม.5": {
            "เทอม 1": [
                ("1️⃣", "Mixed Tenses Review", "ai"),
                ("2️⃣", "Modal Verbs Review (Must, have to, should)", "ai"),
                ("3️⃣", "Participle Clauses", "ai"),
                ("4️⃣", "Passive Voice Review", "ai"),
                ("5️⃣", "Essay Types (Argumentative, descriptive)", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "Speaking: Debating (Agree/disagree)", "ai"),
                ("2️⃣", "Listening Skills (News, interviews)", "ai"),
                ("3️⃣⃣", "Vocabulary 2000 (Idioms, phrasal verbs)", "ai"),
                ("4️⃣", "Academic Writing 🌟", "ai"),
                ("5️⃣", "Presentation Skills 🌟", "ai"),
            ]
        },
        "ม.6": {
            "เทอม 1": [
                ("1️⃣", "Advanced Grammar (Inversion, emphasis)", "ai"),
                ("2️⃣", "Academic Writing (Research, citations)", "ai"),
                ("3️⃣", "Critical Reading (Analysis, inference)", "ai"),
                ("4️⃣", "Presentation Skills", "ai"),
            ],
            "เทอม 2": [
                ("1️⃣", "Test Preparation (O-NET, University entrance)", "ai"),
                ("2️⃣", "Career English (Resume, interview)", "ai"),
                ("3️⃣", "Global Issues (Environment, technology)", "ai"),
                ("4️⃣", "Literature (Poems, short stories)", "ai"),
            ]
        },
    }
    
    # Grade Selection
    english_grade_options = ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6", "ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
    english_grade_select = st.selectbox("📚 เลือกระดับชั้น:", english_grade_options)
    
    # Check if grade is ม.1-6 (has terms)
    if english_grade_select in ["ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]:
        # Select term first
        english_term_options = list(english_topics[english_grade_select].keys())
        english_term_select = st.selectbox("📅 เลือกเทอม:", english_term_options)
        english_topics_list = english_topics[english_grade_select][english_term_select]
        selected_english_grade = english_grade_select
    else:
        # Primary school grades
        english_topics_list = english_topics.get(english_grade_select, [])
        selected_english_grade = english_grade_select
    
    # Topic selection with display names
    english_topic_options = [f"{prefix} {name}" for prefix, name, _ in english_topics_list]
    english_topic_select = st.selectbox("📖 เลือกหัวข้อ:", english_topic_options)
    
    # Get selected topic details
    selected_english_topic = None
    for prefix, name, topic_type in english_topics_list:
        full_name = f"{prefix} {name}"
        if full_name == english_topic_select:
            # Remove 🌟 for backend
            clean_name = name.replace(" 🌟", "")
            selected_english_topic = clean_name
            break
    
    # Show AI requirement message only once
    st.info("📌 หัวข้อภาษาอังกฤษทั้งหมดต้องใช้ AI ในการสร้างแบบฝึกหัดค่ะ")
    
    # Exercise type selector
    exercise_types = [
        "ทั้งหมด (ผสมผสาน - All Types)",
        "ไวยากรณ์ (Grammar Exercises)",
        "คำศัพท์ (Vocabulary)",
        "การอ่าน (Reading Comprehension)",
        "การเขียน (Writing)",
        "การฟัง (Listening Scripts)",
        "การพูด (Speaking Prompts)"
    ]
    exercise_type = st.selectbox("📝 เลือกประเภทแบบฝึกหัด:", exercise_types)
    
    num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=20)
    
    # Custom Prompt Section
    with st.expander("✏️ ปรับแต่ง Prompt (ไม่บังคับ)", expanded=False):
        english_prompt = st.text_area(
            "Prompt สำหรับ AI (ถ้าเว้นว่างจะใช้ค่าเริ่มต้น)",
            value="",
            height=100,
            help="ปรับแต่ง prompt เพื่อให้ได้ผลลัพธ์ตามต้องการ"
        )
        
        st.markdown("**💡 ตัวอย่าง Prompt ที่ดี:**")
        st.code("Create 10 English grammar exercises about Past Tense for Prathom 3 students. Include fill-in-the-blank, multiple choice, and sentence transformation exercises with answers.", language="text")
    
    if st.button("🚀 สร้างใบงานภาษาอังกฤษ", type="primary"):
        if not st.session_state.api_key:
            st.info("🔑 ต้องใช้ API Key สำหรับหัวข้อภาษาอังกฤษค่ะ กรอก API Key ได้ที่ด้านบนนะคะ")
        else:
            with st.spinner("🤖 AI กำลังสร้างแบบฝึกหัดภาษาอังกฤษ..."):
                # Map exercise type to prompt
                exercise_mapping = {
                    "ทั้งหมด (ผสมผสาน - All Types)": "mix",
                    "ไวยากรณ์ (Grammar Exercises)": "grammar",
                    "คำศัพท์ (Vocabulary)": "vocabulary",
                    "การอ่าน (Reading Comprehension)": "reading",
                    "การเขียน (Writing)": "writing",
                    "การฟัง (Listening Scripts)": "listening",
                    "การพูด (Speaking Prompts)": "speaking"
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
        st.success("✅ สร้างใบงานภาษาอังกฤษสำเร็จ!")
        
        # Preview section
        with st.expander("👀 ดูตัวอย่างคำถามและเฉลย", expanded=True):
            st.markdown("### 📝 คำถาม / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_questions) - 10} ข้อ")
            
            st.markdown("### ✅ เฉลย / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_answers) - 10} ข้อ")
        
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("🗑️ ล้างและสร้างใหม่"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "สังคมศึกษา" in mode_select:
    st.subheader("📖 สร้างใบงานสังคมศึกษา (ตามหลักสูตร สสวท.)")
    
    # Social Studies Curriculum Data
    social_studies_topics = {
        # ===== ระดับประถมศึกษา =====
        "ป.1": [
            ("1️⃣", "ตัวเราและครอบครัว", "ai"),
            ("2️⃣", "บ้านและที่อยู่อาศัย", "ai"),
            ("3️⃣", "โรงเรียนและเพื่อน", "ai"),
            ("4️⃣", "ชุมชนและละแวกบ้าน", "ai"),
            ("5️⃣", "สถานที่สำคัญในชุมชน", "ai"),
            ("6️⃣", "อาชีพในชุมชน", "ai"),
            ("7️⃣", "การใช้จ่ายเงิน", "ai"),
            ("8️⃣", "ทิศทางและแผนที่ง่ายๆ", "ai"),
            ("9️⃣", "วันสำคัญและเทศกาล", "ai"),
            ("🔟", "ศาสนาและความเชื่อพื้นบ้าน", "ai"),
            ("1️⃣1️⃣", "ประวัติตัวเรา", "ai"),
            ("1️⃣2️⃣", "ธรรมชาติรอบตัว", "ai"),
        ],
        "ป.2": [
            ("1️⃣", "ครอบครัวและความสัมพันธ์", "ai"),
            ("2️⃣", "โรงเรียนกับการเรียนรู้", "ai"),
            ("3️⃣", "เพื่อนและการอยู่ร่วมกัน", "ai"),
            ("4️⃣", "ชุมชนและท้องถิ่น", "ai"),
            ("5️⃣", "สิทธิและหน้าที่ของเด็ก", "ai"),
            ("6️⃣", "กฎหมายในชีวิตประจำวัน", "ai"),
            ("7️⃣", "เงินตราและการซื้อขาย", "ai"),
            ("8️⃣", "การออมเงิน", "ai"),
            ("9️⃣", "แผนที่และทิศทาง", "ai"),
            ("🔟", "ทรัพยากรในชุมชน", "ai"),
            ("1️⃣1️⃣", "ประวัติศาสตร์ท้องถิ่น", "ai"),
            ("1️⃣2️⃣", "วัฒนธรรมประเพณีไทย", "ai"),
        ],
        "ป.3": [
            ("1️⃣", "การปกครองในครอบครัว", "ai"),
            ("2️⃣", "การปกครองในโรงเรียน", "ai"),
            ("3️⃣", "การปกครองในชุมชน", "ai"),
            ("4️⃣", "ท้องถิ่นของเรา", "ai"),
            ("5️⃣", "การเปลี่ยนแปลงของชุมชน", "ai"),
            ("6️⃣", "ภูมิภาคในประเทศไทย", "ai"),
            ("7️⃣", "ลักษณะภูมิประเทศไทย", "ai"),
            ("8️⃣", "เศรษฐกิจในชุมชน", "ai"),
            ("9️⃣", "การผลิต การบริโภค", "ai"),
            ("🔟", "พุทธประวัติและพุทธศาสนา", "ai"),
            ("1️⃣1️⃣", "วัฒนธรรมประเพณีไทย", "ai"),
            ("1️⃣2️⃣", "ความรักชาติไทย", "ai"),
        ],
        "ป.4": [
            ("1️⃣", "การปกครองท้องถิ่น", "ai"),
            ("2️⃣", "การเลือกตั้งในโรงเรียน", "ai"),
            ("3️⃣", "หน้าที่พลเมือง", "ai"),
            ("4️⃣", "สิทธิของเด็ก", "ai"),
            ("5️⃣", "ภูมิภาคอาเซียน", "ai"),
            ("6️⃣", "ประเทศเพื่อนบ้านไทย", "ai"),
            ("7️⃣", "เศรษฐกิจในชุมชน", "ai"),
            ("8️⃣", "การผลิตและการบริโภค", "ai"),
            ("9️⃣", "การบริหารเงินและการออม", "ai"),
            ("🔟", "ประวัติศาสตร์ไทยสมัยสุโขทัย", "ai"),
            ("1️⃣1️⃣", "การสูญเสียดินแดน", "ai"),
            ("1️⃣2️⃣", "บุคคลสำคัญในประวัติศาสตร์ไทย", "ai"),
        ],
        "ป.5": [
            ("1️⃣", "การปกครองระบอบประชาธิปไตย", "ai"),
            ("2️⃣", "สถาบันพระมหากษัตริย์ไทย", "ai"),
            ("3️⃣", "สิทธิมนุษยชน", "ai"),
            ("4️⃣", "หน้าที่พลเมืองไทย", "ai"),
            ("5️⃣", "เศรษฐกิจในระดับประเทศ", "ai"),
            ("6️⃣", "การค้าระหว่างประเทศ", "ai"),
            ("7️⃣", "ภูมิศาสตร์เอเชีย", "ai"),
            ("8️⃣", "ทรัพยากรธรรมชาติ", "ai"),
            ("9️⃣", "สิ่งแวดล้อมและการอนุรักษ์", "ai"),
            ("🔟", "ประวัติศาสตร์อาเซียน", "ai"),
            ("1️⃣1️⃣", "ความร่วมมือในอาเซียน", "ai"),
            ("1️⃣2️⃣", "เศรษฐกิจอาเซียน", "ai"),
        ],
        "ป.6": [
            ("1️⃣", "การปกครองระบอบประชาธิปไตยในไทย", "ai"),
            ("2️⃣", "รัฐธรรมนูญและการมีส่วนร่วม", "ai"),
            ("3️⃣", "สิทธิหน้าที่พลเมือง", "ai"),
            ("4️⃣", "เศรษฐกิจโลก", "ai"),
            ("5️⃣", "เทคโนโลยีกับเศรษฐกิจ", "ai"),
            ("6️⃣", "ภูมิศาสตร์โลก", "ai"),
            ("7️⃣", "สภาพภูมิอากาศและภูมิประเทศโลก", "ai"),
            ("8️⃣", "ประวัติศาสตร์โลก", "ai"),
            ("9️⃣", "มรดกทางวัฒนธรรมโลก", "ai"),
            ("🔟", "ความสัมพันธ์ระหว่างประเทศ", "ai"),
            ("1️⃣1️⃣", "องค์กรระหว่างประเทศ", "ai"),
            ("1️⃣2️⃣", "ความมั่นคงและสันติภาพโลก", "ai"),
        ],
        # ===== ระดับมัธยมศึกษา =====
        "ม.1": [
            ("1️⃣", "ศาสนากับวิถีชีวิต", "ai"),
            ("2️⃣", "คุณค่าของศาสนา", "ai"),
            ("3️⃣", "สิทธิหน้าที่พลเมือง", "ai"),
            ("4️⃣", "กฎหมายในสังคม", "ai"),
            ("5️⃣", "การบริหารทรัพยากร", "ai"),
            ("6️⃣", "ระบบเศรษฐกิจ", "ai"),
            ("7️⃣", "ภูมิศาสตร์กับชีวิตประจำวัน", "ai"),
            ("8️⃣", "แผนที่และการอ่านข้อมูลภูมิ", "ai"),
            ("9️⃣", "ประวัติศาสตร์สู่ปัจจุบัน", "ai"),
            ("🔟", "อาชีพและการทำงาน", "ai"),
        ],
        "ม.2": [
            ("1️⃣", "ศาสนาสากลและการอยู่ร่วมกัน", "ai"),
            ("2️⃣", "ความหลากหลายทางศาสนา", "ai"),
            ("3️⃣", "ประชาธิปไตยและการมีส่วนร่วม", "ai"),
            ("4️⃣", "การเลือกตั้งและการลงคะแนน", "ai"),
            ("5️⃣", "การตลาดและการเงิน", "ai"),
            ("6️⃣", "การลงทุนและการออม", "ai"),
            ("7️⃣", "ภูมิศาสตร์ในภูมิภาคอาเซียน", "ai"),
            ("8️⃣", "ความสัมพันธ์ระหว่างประเทศ", "ai"),
            ("9️⃣", "ประวัติศาสตร์อาเซียน", "ai"),
            ("🔟", "วัฒนธรรมอาเซียน", "ai"),
        ],
        "ม.3": [
            ("1️⃣", "ศาสนากับการพัฒนาประเทศ", "ai"),
            ("2️⃣", "ศีลธรรมในยุคโลกาภิวัตน์", "ai"),
            ("3️⃣", "การเมืองในประเทศไทย", "ai"),
            ("4️⃣", "การเลือกตั้งและพรรคการเมือง", "ai"),
            ("5️⃣", "เศรษฐกิจไทยและการเปลี่ยนแปลง", "ai"),
            ("6️⃣", "เศรษฐกิจโลกและการค้าระหว่างประเทศ", "ai"),
            ("7️⃣", "ภูมิศาสตร์โลก", "ai"),
            ("8️⃣", "สิ่งแวดล้อมและความยั่งยืน", "ai"),
            ("9️⃣", "ประวัติศาสตร์โลกสมัยใหม่", "ai"),
            ("🔟", "ยุคสงครามโลกครั้งที่ 1-2", "ai"),
        ],
        "ม.4": [
            ("1️⃣", "ศาสนากับสังคม", "ai"),
            ("2️⃣", "ศาสนาเปรียบเทียบ", "ai"),
            ("3️⃣", "สิทธิมนุษยชนสากล", "ai"),
            ("4️⃣", "กฎหมายระหว่างประเทศ", "ai"),
            ("5️⃣", "เศรษฐศาสตร์ธุรกิจ", "ai"),
            ("6️⃣", "การตลาดและการจัดการ", "ai"),
            ("7️⃣", "ภูมิศาสตร์การเมือง", "ai"),
            ("8️⃣", "ทรัพยากรและสิ่งแวดล้อมโลก", "ai"),
            ("9️⃣", "ประวัติศาสตร์สังคม", "ai"),
            ("🔟", "วัฒนธรรมและอารยธรรมโลก", "ai"),
        ],
        "ม.5": [
            ("1️⃣", "ศาสนากับความขัดแย้ง", "ai"),
            ("2️⃣", "ศาสนาในยุคโลกาภิวัตน์", "ai"),
            ("3️⃣", "ประชาธิปไตยและระบอบการปกครอง", "ai"),
            ("4️⃣", "การเมืองระหว่างประเทศ", "ai"),
            ("5️⃣", "เศรษฐศาสตร์การพัฒนา", "ai"),
            ("6️⃣", "ความมั่นคงทางเศรษฐกิจ", "ai"),
            ("7️⃣", "ภูมิศาสตร์เศรษฐกิจโลก", "ai"),
            ("8️⃣", "การทูตและความสัมพันธ์ระหว่างชาติ", "ai"),
            ("9️⃣", "ประวัติศาสตร์เศรษฐกิจ", "ai"),
            ("🔟", "เทคโนโลยีกับการเปลี่ยนแปลงทางสังคม", "ai"),
        ],
        "ม.6": [
            ("1️⃣", "ศาสนา คุณธรรม และจริยธรรม", "ai"),
            ("2️⃣", "สังคมและวัฒนธรรมร่วมสมัย", "ai"),
            ("3️⃣", "สิทธิมนุษยชนในประเทศไทย", "ai"),
            ("4️⃣", "การเมืองและการปกครองในอนาคต", "ai"),
            ("5️⃣", "เศรษฐกิจไทยในบริบทโลก", "ai"),
            ("6️⃣", "ความมั่นคงระหว่างประเทศ", "ai"),
            ("7️⃣", "อาเซียนในศตวรรษที่ 21", "ai"),
            ("8️⃣", "โลกาภิวัตน์และความท้าทาย", "ai"),
            ("9️⃣", "อาชีพในอนาคตและทักษะศตวรรษที่ 21", "ai"),
            ("🔟", "การเป็นพลเมืองโลก", "ai"),
        ],
    }
    
    # Grade Selection
    social_grade_options = ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6", "ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
    social_grade_select = st.selectbox("📚 เลือกระดับชั้น:", social_grade_options)
    
    # Topic selection with display names
    social_topics_list = social_studies_topics.get(social_grade_select, [])
    social_topic_options = [f"{prefix} {name}" for prefix, name, _ in social_topics_list]
    social_topic_select = st.selectbox("📖 เลือกหัวข้อ:", social_topic_options)
    
    # Get selected topic details
    selected_social_topic = None
    for prefix, name, topic_type in social_topics_list:
        full_name = f"{prefix} {name}"
        if full_name == social_topic_select:
            selected_social_topic = name
            break
    
    # Show AI requirement message
    st.info("📌 หัวข้อสังคมศึกษาทั้งหมดต้องใช้ AI ในการสร้างแบบฝึกหัดค่ะ")
    
    # Exercise type selector
    exercise_types = [
        "ทั้งหมด (ผสมผสาน)",
        "ความรู้พื้นฐาน (Knowledge)",
        "ความเข้าใจ (Comprehension)",
        "การวิเคราะห์ (Analysis)",
        "การประเมินค่า (Evaluation)",
        "การสร้างสรรค์ (Creation)"
    ]
    exercise_type = st.selectbox("📝 เลือกประเภทแบบฝึกหัด:", exercise_types)
    
    num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=20)
    
    # Custom Prompt Section
    with st.expander("✏️ ปรับแต่ง Prompt (ไม่บังคับ)", expanded=False):
        social_prompt = st.text_area(
            "Prompt สำหรับ AI (ถ้าเว้นว่างจะใช้ค่าเริ่มต้น)",
            value="",
            height=100,
            help="ปรับแต่ง prompt เพื่อให้ได้ผลลัพธ์ตามต้องการ"
        )
        
        st.markdown("**💡 ตัวอย่าง Prompt ที่ดี:**")
        st.code("สร้างแบบฝึกหัดสังคมศึกษา 10 ข้อ เรื่องการปกครองระบอบประชาธิปไตย สำหรับนักเรียน ป.5 ให้มีทั้งคำถามถูก-ผิด ปรนัย และคำถามเปิด พร้อมเฉลยละเอียด", language="text")
    
    if st.button("🚀 สร้างใบงานสังคมศึกษา", type="primary"):
        if not st.session_state.api_key:
            st.info("🔑 ต้องใช้ API Key สำหรับหัวข้อสังคมศึกษาค่ะ กรอก API Key ได้ที่ด้านบนนะคะ")
        else:
            with st.spinner("🤖 AI กำลังสร้างแบบฝึกหัดสังคมศึกษา..."):
                # Map exercise type to prompt
                exercise_mapping = {
                    "ทั้งหมด (ผสมผสาน)": "mix",
                    "ความรู้พื้นฐาน (Knowledge)": "knowledge",
                    "ความเข้าใจ (Comprehension)": "comprehension",
                    "การวิเคราะห์ (Analysis)": "analysis",
                    "การประเมินค่า (Evaluation)": "evaluation",
                    "การสร้างสรรค์ (Creation)": "creation"
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
        st.success("✅ สร้างใบงานสังคมศึกษาสำเร็จ!")
        
        # Preview section
        with st.expander("👀 ดูตัวอย่างคำถามและเฉลย", expanded=True):
            st.markdown("### 📝 คำถาม / Questions")
            for i, q in enumerate(st.session_state.preview_questions[:10], 1):
                st.write(f"**{i}.** {q}")
            if len(st.session_state.preview_questions) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_questions) - 10} ข้อ")
            
            st.markdown("### ✅ เฉลย / Answers")
            for i, a in enumerate(st.session_state.preview_answers[:10], 1):
                st.write(f"**{i}.** {a}")
            if len(st.session_state.preview_answers) > 10:
                st.write(f"... และอีก {len(st.session_state.preview_answers) - 10} ข้อ")
        
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", st.session_state.generated_pdf, f"{st.session_state.generated_filename}.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", st.session_state.generated_word, f"{st.session_state.generated_filename}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        if st.button("🗑️ ล้างและสร้างใหม่"):
            st.session_state.generated_pdf = None
            st.session_state.generated_word = None
            st.session_state.preview_questions = None
            st.session_state.preview_answers = None
            st.rerun()

elif "โจทย์ปัญหา AI" in mode_select:
    st.subheader("🤖 สร้างโจทย์ปัญหาด้วย AI")
    
    if not st.session_state.api_key:
        show_api_warning()
    else:
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("หัวข้อ (เช่น อวกาศ, สวนสัตว์, ตลาด)", "การผจญภัยในอวกาศ")
            grade = st.selectbox("ระดับชั้น", ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6"])
        with col2:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=5)
        
        # Custom Prompt Section
        with st.expander("✏️ ปรับแต่ง Prompt (ไม่บังคับ)", expanded=False):
            word_problem_prompt = st.text_area(
                "Prompt สำหรับ AI (ถ้าเว้นว่างจะใช้ค่าเริ่มต้น)",
                value="",
                height=100,
                help="ปรับแต่ง prompt เพื่อให้ได้ผลลัพธ์ตามต้องการ"
            )
            
            st.markdown("**💡 ตัวอย่าง Prompt ที่ดี:**")
            st.code("สร้างโจทย์ปัญหาคณิตศาสตร์ 5 ข้อ เรื่องการคูณและการหาร สำหรับนักเรียนป.3 ให้เป็นโจทย์สถานการณ์ในชีวิตจริง เช่น การซื้อของ การแบ่งของ โจทย์ต้องมีความหลากหลายและท้าทายเหมาะกับวัย", language="text")
        
        if st.button("🚀 ให้ AI สร้างโจทย์", type="primary"):
            with st.spinner("AI กำลังคิดโจทย์... (รอสักครู่นะครับ)"):
                grade_map = {"ป.1": "Grade 1", "ป.2": "Grade 2", "ป.3": "Grade 3", "ป.4": "Grade 4", "ป.5": "Grade 5", "ป.6": "Grade 6"}
                questions, answers = generator.generate_ai_word_problems(topic, grade_map.get(grade, "Grade 3"), num_q)
                
                pdf = generator.create_pdf(title, school_name, "AI Word Problems", questions, answers, qr_url, uploaded_logo)
                word = generator.create_word_doc(title, school_name, "AI Word Problems", questions, answers)
                
                # Preview section
                with st.expander("👀 ดูตัวอย่างคำถามและเฉลย", expanded=True):
                    st.markdown("### 📝 คำถาม / Questions")
                    for i, q in enumerate(questions[:10], 1):
                        st.write(f"**{i}.** {q}")
                    if len(questions) > 10:
                        st.write(f"... และอีก {len(questions) - 10} ข้อ")
                    
                    st.markdown("### ✅ เฉลย / Answers")
                    for i, a in enumerate(answers[:10], 1):
                        st.write(f"**{i}.** {a}")
                    if len(answers) > 10:
                        st.write(f"... และอีก {len(answers) - 10} ข้อ")
                
                st.success("✅ สร้างโจทย์เสร็จแล้ว!")
                c1, c2 = st.columns(2)
                c1.download_button("📄 ดาวน์โหลด PDF", pdf, "ai_worksheet.pdf", "application/pdf")
                c2.download_button("📝 ดาวน์โหลด Word", word, "ai_worksheet.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "ปริศนาหาคำศัพท์" in mode_select:
    st.subheader("🔍 สร้างปริศนาหาคำศัพท์ (Word Search)")
    words_input = st.text_area("ใส่คำศัพท์ภาษาอังกฤษ (คั่นด้วยจุลภาค ,)", "CAT, DOG, BIRD, LION, TIGER")
    words = [w.strip() for w in words_input.split(",") if w.strip()]
    
    if st.button("🚀 สร้างปริศนา", type="primary"):
        grid, placed_words = generator.generate_word_search(words)
        pdf = generator.create_pdf(title, school_name, "Word Search", (grid, placed_words), answers=placed_words, qr_link=qr_url, uploaded_logo=uploaded_logo)
        word = generator.create_word_doc(title, school_name, "Word Search", (grid, placed_words), answers=placed_words)
        
        # Preview section
        with st.expander("👀 ดูตัวอย่างปริศนา", expanded=True):
            st.markdown("### 📝 คำศัพท์ที่ซ่อนในปริศนา")
            cols = st.columns(5)
            for i, w in enumerate(placed_words):
                cols[i % 5].write(f"• {w}")
        
        st.success("✅ สร้างปริศนาเรียบร้อย!")
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "puzzle.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", word, "puzzle.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "ฝึกคัดลายมือ" in mode_select:
    st.subheader("✍️ สร้างแบบฝึกคัดลายมือ")
    text_input = st.text_area("ข้อความที่ต้องการให้คัด (คั่นด้วยจุลภาค)", "สวัสดี, ขอบคุณ, ขอโทษ, รักนะ")
    
    if st.button("🚀 สร้างแบบฝึกหัด", type="primary"):
        lines = generator.generate_tracing_lines(text_input)
        pdf = generator.create_pdf(title, school_name, "Handwriting Practice", lines, uploaded_logo=uploaded_logo)
        word = generator.create_word_doc(title, school_name, "Handwriting Practice", lines)
        
        # Preview section
        with st.expander("👀 ดูตัวอย่างข้อความ", expanded=True):
            st.markdown("### 📝 ข้อความที่จะฝึกคัด")
            for i, line in enumerate(lines):
                st.write(f"**{i+1}.** {line}")
        
        st.success("✅ สร้างสำเร็จ!")
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "tracing.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", word, "tracing.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "สร้างข้อสอบจากไฟล์" in mode_select:
    st.subheader("📝 สร้างข้อสอบจากไฟล์เอกสาร (PDF/Word)")
    
    if not st.session_state.api_key:
        show_api_warning()
    else:
        uploaded_file = st.file_uploader("อัปโหลดเอกสารประกอบการสอน (PDF หรือ Docx)", type=["pdf", "docx"])
        num_q = st.number_input("จำนวนข้อสอบที่ต้องการ", min_value=1, max_value=50, value=5)
        
        # Custom Prompt Section
        with st.expander("✏️ ปรับแต่ง Prompt (ไม่บังคับ)", expanded=False):
            quiz_prompt = st.text_area(
                "Prompt สำหรับ AI (ถ้าเว้นว่างจะใช้ค่าเริ่มต้น)",
                value="",
                height=100,
                help="ปรับแต่ง prompt เพื่อให้ได้ผลลัพธ์ตามต้องการ"
            )
            
            st.markdown("**💡 ตัวอย่าง Prompt ที่ดี:**")
            st.code("สร้างข้อสอบ 10 ข้อ จากเนื้อหาที่ให้มา ให้มีทั้งแบบถูก-ผิด ปรนัย 4 ตัวเลือก และคำถามถูกความเข้าใจ พร้อมเฉลยละเอียด", language="text")
        
        if uploaded_file and st.button("🚀 สร้างข้อสอบจากไฟล์", type="primary"):
            with st.spinner("AI กำลังอ่านไฟล์และออกข้อสอบ..."):
                text = generator.extract_text_from_file(uploaded_file)
                
                if not text or "Error" in text:
                    st.error(f"อ่านไฟล์ล้มเหลว: {text}")
                else:
                    questions, answers = generator.generate_quiz_from_text(text, num_q)
                    
                    pdf = generator.create_pdf(title, school_name, "Quiz", questions, answers, qr_url, uploaded_logo)
                    word = generator.create_word_doc(title, school_name, "Quiz", questions, answers)
                    
                    # Preview section
                    with st.expander("👀 ดูตัวอย่างคำถามและเฉลย", expanded=True):
                        st.markdown("### 📝 คำถาม / Questions")
                        for i, q in enumerate(questions[:10], 1):
                            st.write(f"**{i}.** {q}")
                        if len(questions) > 10:
                            st.write(f"... และอีก {len(questions) - 10} ข้อ")
                        
                        st.markdown("### ✅ เฉลย / Answers")
                        for i, a in enumerate(answers[:10], 1):
                            st.write(f"**{i}.** {a}")
                        if len(answers) > 10:
                            st.write(f"... และอีก {len(answers) - 10} ข้อ")
                    
                    st.success(f"✅ สร้างข้อสอบ {len(questions)} ข้อ สำเร็จแล้ว!")
                    c1, c2 = st.columns(2)
                    c1.download_button("📄 ดาวน์โหลด PDF", pdf, "quiz.pdf", "application/pdf")
                    c2.download_button("📝 ดาวน์โหลด Word", word, "quiz.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.markdown("---")
st.caption("พัฒนาโดย **Nong Aom & P'Em** | Powered by Google Gemini AI")
