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

st.set_page_config(page_title="โปรแกรมสร้างใบงาน EasyWorksheet", page_icon="🚀", layout="wide")
# Full IPST Curriculum by Grade (Dictionary format)
ipst_topics = {
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
    ],
    "ป.4": [
        ("1️⃣", "จำนวนนับที่มากกว่า 100,000", "calculation"),
        ("2️⃣", "การบวกและการลบ", "calculation"),
        ("3️⃣", "เรขาคณิต 🌟", "ai"),
        ("4️⃣", "การคูณ", "calculation"),
        ("5️⃣", "การหาร", "calculation"),
        ("6️⃣", "แผนภูมิรูปภาพ แผนภูมิแท่งและตาราง 🌟", "ai"),
        ("7️⃣", "การวัด 🌟", "ai"),
        ("8️⃣", "พื้นที่ 🌟", "ai"),
        ("9️⃣", "เงิน 🌟", "ai"),
        ("🔟", "เศษส่วน", "calculation"),
    ],
    "ป.5": [
        ("1️⃣", "การคูณและการหารทศนิยม", "calculation"),
        ("2️⃣", "เศษส่วนและการเปรียบเทียบ", "calculation"),
        ("3️⃣", "ร้อยละและสัดส่วน", "calculation"),
        ("4️⃣", "การบวกลบคูณหารระคน", "calculation"),
        ("5️⃣", "รูปเรขาคณิตและปริมาตร 🌟", "ai"),
        ("6️⃣", "แผนภูมิ 🌟", "ai"),
    ],
    "ป.6": [
        ("1️⃣", "ทศนิยมและเศษส่วน", "calculation"),
        ("2️⃣", "อัตราส่วน", "calculation"),
        ("3️⃣", "ร้อยละ", "calculation"),
        ("4️⃣", "ปริมาตรและความจุ", "calculation"),
        ("5️⃣", "รูปเรขาคณิตและการนึกภาพ 🌟", "ai"),
    ],
    "ม.1": [
        ("1️⃣", "จำนวนเต็ม", "calculation"),
        ("2️⃣", "เลขยกกำลัง", "calculation"),
        ("3️⃣", "พหุนาม", "calculation"),
        ("4️⃣", "สมการเชิงเส้นตัวเดียว", "calculation"),
        ("5️⃣", "อัตราส่วนและร้อยละ", "calculation"),
    ],
    "ม.2": [
        ("1️⃣", "อัตราส่วน", "calculation"),
        ("2️⃣", "ร้อยละ", "calculation"),
        ("3️⃣", "กราฟ 🌟", "ai"),
        ("4️⃣", "การแปรผกผัน", "calculation"),
        ("5️⃣", "ความเท่ากันทุกประการ", "calculation"),
    ],
    "ม.3": [
        ("1️⃣", "สมการเชิงเส้น", "calculation"),
        ("2️⃣", "อสมการ", "calculation"),
        ("3️⃣", "ความน่าจะเป็น", "calculation"),
        ("4️⃣", "สถิติ 🌟", "ai"),
        ("5️⃣", "กรณฑ์ที่สอง", "calculation"),
    ],
    "ม.4": [
        ("1️⃣", "จำนวนจริง", "calculation"),
        ("2️⃣", "เลขยกกำลัง", "calculation"),
        ("3️⃣", "รากที่สอง", "calculation"),
        ("4️⃣", "พหุนาม 🌟", "ai"),
        ("5️⃣", "ฟังก์ชัน 🌟", "ai"),
    ],
    "ม.5": [
        ("1️⃣", "ฟังก์ชัน", "calculation"),
        ("2️⃣", "อัตราส่วนตรีโกณ", "calculation"),
        ("3️⃣", "สถิติ", "calculation"),
        ("4️⃣", "ลำดับและอนุกรม", "calculation"),
        ("5️⃣", "ความน่าจะเป็น", "calculation"),
    ],
    "ม.6": [
        ("1️⃣", "แคลคูลัสเบื้องต้น", "calculation"),
        ("2️⃣", "ความน่าจะเป็น", "calculation"),
        ("3️⃣", "สถิติขั้นสูง", "calculation"),
        ("4️⃣", "ลำดับอนุกรมอนันต์", "calculation"),
        ("5️⃣", "กำหนดการเชิงเส้น 🌟", "ai"),
    ],
}


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
                    genai.configure(api_key=clean_key)
                    list(genai.list_models())  # Test call
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
    
    # Mode Selection (Thai) - Categorized
    # Mode Selection (Thai) - Categorized
    mode_options = [
        "🧪 ทดสอบ AI (Test AI)",
        "---",
        "📐 วิชาหลัก สสวท.",
        "📐 คณิตศาสตร์ (Math)",
        "🔬 วิทยาศาสตร์ (Science)",
        "📚 ภาษาไทย (Thai Language)",
        "🌏 ภาษาอังกฤษ (English Language)",
        "📖 สังคมศึกษา (Social Studies)",
        "---",
        "💪 ส่วนเสริม",
        "🤖 โจทย์ปัญหา AI (Word Problems)",
        "✍️ ฝึกคัดลายมือ (Handwriting)",
        "🔍 ปริศนาหาคำศัพท์ (Word Search)",
        "---",
        "📤 สร้างข้อสอบจากไฟล์ (Upload & Generate)"
    ]
    mode_select = st.selectbox("เลือกประเภทใบงาน:", mode_options, key="mode_select")
    
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
    st.subheader("📐 วิชาคณิตศาสตร์ (สสวท.)")
    
    # Create type dropdown
    create_type = st.selectbox(
        "เลือกประเภทที่ต้องการ:",
        ["📝 สร้างใบงาน / แบบฝึกหัด", "📚 สรุปเนื้อหา", "❓ สร้างโจทย์ข้อสอบ"],
        key="math_create_type"
    )
    
    # Source dropdown
    if "สร้างใบงาน" in create_type or "แบบฝึกหัด" in create_type:
        source_options = [
            "🤖 AI สร้างให้ (จากหัวข้อ)",
            "📁 จากไฟล์ Word/PDF",
            "✏️ จาก Prompt (เขียนเอง)"
        ]
    elif "สรุป" in create_type:
        source_options = [
            "📁 จากไฟล์ Word/PDF",
            "✏️ จาก Prompt (เขียนเอง)"
        ]
    else:
        source_options = [
            "🤖 AI สร้างให้ (จากหัวข้อ)",
            "📁 จากไฟล์ Word/PDF",
            "✏️ จาก Prompt (เขียนเอง)"
        ]
    
    source_type = st.selectbox("เลือกวิธีสร้าง:", source_options, key="math_source")
    
    # Grade Selection
    grade_options = ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6", "ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
    grade_select = st.selectbox("📚 เลือกระดับชั้น:", grade_options, key="math_grade")
    
    # Get topics for selected grade from ipst_topics
    math_topics = ipst_topics.get(grade_select, [])
    math_topic_names = [f"{t[0]} {t[1]}" for t in math_topics]
    
    # ===== AI สร้างให้ (จากหัวข้อ) =====
    if "AI สร้างให้" in source_type:
        topic_select = st.selectbox("📝 เลือกหัวข้อในหลักสูตร:", math_topic_names, key="math_topic")
        
        # Extract topic name
        selected_math_topic = ""
        for prefix, name, type_info in math_topics:
            if f"{prefix} {name}" == topic_select:
                selected_math_topic = name
                break
        
        # Show num_q only if not summary
        num_q = 10
        if "สรุป" not in create_type:
            num_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10, key="math_num")
        
        # Generate button
        if st.button("🚀 สร้างใบงาน", type="primary", key="math_gen"):
            # Check if AI required
            requires_ai = any("🌟" in t[1] for t in math_topics)
            if requires_ai and not st.session_state.api_key:
                show_api_warning()
            else:
                with st.spinner("🤖 AI กำลังสร้าง..."):
                    if "สรุป" in create_type:
                        summary_prompt = f"สรุปเนื้อหาคณิตศาสตร์เรื่อง {selected_math_topic} สำหรับนักเรียนระดับ {grade_select}"
                        summary_result = generator.ai.generate(summary_prompt)
                        
                        # Create PDF and Word for summary
                        pdf = generator.create_summary_pdf(title, school_name, "สรุปเนื้อหา", summary_result, qr_url=qr_url, logo=uploaded_logo)
                        word = generator.create_summary_word_doc(title, school_name, "สรุปเนื้อหา", summary_result)
                        
                        # Preview section
                        with st.expander("👀 ดูตัวอย่างสรุป", expanded=True):
                            st.markdown("### 📚 สรุปเนื้อหา")
                            st.write(summary_result)
                        
                        # Download buttons
                        st.success("✅ สร้างสรุปสำเร็จ!")
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "summary.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "summary.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                        
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


if "สร้างเนื้อหา" in mode_select:
    st.subheader("📤 สร้างข้อสอบจากไฟล์ / เนื้อหา")
    
    if not st.session_state.api_key:
        show_api_warning()
    else:
        # Method selection: Upload file or Prompt
        method = st.radio(
            "เลือกวิธีสร้าง:",
            ["📁 Upload ไฟล์ (PDF/Word)", "🤖 ให้ AI สร้างจาก Prompt"],
            horizontal=True
        )
        
        source_content = ""
        
        if "Upload" in method:
            # File upload section with clear button
            c1, c2 = st.columns([3, 1])
            with c1:
                uploaded_content_file = st.file_uploader(
                    "📁 อัปโหลดไฟล์เนื้อหา (PDF หรือ Word)", 
                    type=["pdf", "docx", "doc"]
                )
            with c2:
                if uploaded_content_file:
                    if st.button("🗑️ ล้าง", use_container_width=True):
                        st.session_state.uploaded_content_file = None
                        st.rerun()
            
            # Show file info and content
            if uploaded_content_file:
                # Save to session state
                st.session_state.uploaded_content_file = uploaded_content_file
                
                with st.spinner("📖 AI กำลังอ่านไฟล์..."):
                    source_content = generator.extract_text_from_file(uploaded_content_file)
                    
                    if source_content and "Error" not in source_content:
                        st.success(f"✅ อ่านไฟล์สำเร็จ! ({len(source_content)} ตัวอักษร)")
                        # Show snippet
                        with st.expander("👀 ดูเนื้อหาที่อ่านได้", expanded=False):
                            st.text(source_content[:500] + "..." if len(source_content) > 500 else source_content)
                    else:
                        st.error("❌ ไม่สามารถอ่านไฟล์ได้")
        else:
            # Prompt input section
            source_content = st.text_area(
                "📝 หัวข้อหรือเนื้อหาที่ต้องการให้ AI สร้าง:",
                placeholder="เช่น: ระบบร่างกายมนุษย์, การคูณและการหาร, Tenses ในภาษาอังกฤษ",
                height=100
            )
        
        # Content type selection
        st.markdown("### 📋 เลือกประเภทที่ต้องการ")
        content_type = st.selectbox(
            "ต้องการให้ AI สร้าง:",
            ["📝 ใบงาน / แบบฝึกหัด", "📚 สรุปเนื้อหา", "❓ โจทย์ข้อสอบ"]
        )
        
        # Grade level
        content_grade = st.selectbox(
            "📚 ระดับชั้น:",
            ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6", "ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]
        )
        
        # Number of questions (if creating worksheet/quiz)
        num_content_q = 10
        if "ใบงาน" in content_type or "โจทย์" in content_type:
            num_content_q = st.number_input("จำนวนข้อ", min_value=1, max_value=50, value=10)
        
        # Generate button
        if st.button("🚀 สร้างเนื้อหา", type="primary"):
            if not source_content:
                st.warning("⚠️ กรุณา Upload ไฟล์ หรือ เขียน Prompt ก่อนนะคะ!")
            else:
                # Summarize long content first
                summarized_content = generator.summarize_text(source_content, max_length=3000)
                
                if summarized_content != source_content:
                    with st.expander("👀 เนื้อหาที่สรุป", expanded=False):
                        st.write(summarized_content)
                
                with st.spinner("🤖 AI กำลังสร้างเนื้อหา..."):
                    try:
                        # Generate content based on type
                        if "ใบงาน" in content_type:
                            questions, answers = generator.generate_quiz_from_text(summarized_content, num_content_q)
                            content_title = "ใบงาน"
                        elif "สรุป" in content_type:
                            summary_prompt = f"""สรุปเนื้อหาต่อไปนี้ให้กระชับเข้าใจง่าย สำหรับนักเรียนระดับ {content_grade}

เนื้อหา:
{summarized_content}

ให้สรุปในรูปแบบ:
- สาระสำคัญ
- หัวข้อหลัก
- ตัวอย่างประกอบ
- แบบทดสอบความเข้าใจ 3 ข้อ"""
                            summary_result = generator.ai.generate(summary_prompt.format(content=summarized_content))
                            questions = [summary_result] if summary_result else ["ไม่สามารถสร้างสรุปได้"]
                            answers = ["-"]
                            content_title = "สรุปเนื้อหา"
                        else:
                            questions, answers = generator.generate_quiz_from_text(summarized_content, num_content_q)
                            content_title = "โจทย์ข้อสอบ"
                        
                        # Create outputs
                        pdf = generator.create_content_pdf(
                            title, school_name, content_title, 
                            questions, answers, 
                            qr_url=qr_url, 
                            logo=uploaded_logo,
                            summary=summary_result if "สรุป" in content_type else None
                        )
                        word = generator.create_content_word_doc(
                            title, school_name, content_title,
                            questions, answers,
                            summary=summary_result if "สรุป" in content_type else None
                        )
                        
                        # Preview section
                        with st.expander("👀 ดูตัวอย่างเนื้อหา", expanded=True):
                            if "สรุป" in content_type:
                                st.markdown("### 📚 สรุปเนื้อหา")
                                st.write(summary_result)
                            else:
                                st.markdown("### 📝 คำถาม")
                                for i, q in enumerate(questions[:10], 1):
                                    st.write(f"**{i}.** {q}")
                                if len(questions) > 10:
                                    st.write(f"... และอีก {len(questions) - 10} ข้อ")
                            
                            st.markdown("### ✅ เฉลย")
                            for i, a in enumerate(answers[:10], 1):
                                st.write(f"**{i}.** {a}")
                            if len(answers) > 10:
                                st.write(f"... และอีก {len(answers) - 10} ข้อ")
                        
                        st.success(f"✅ สร้าง{content_title}สำเร็จ!")
                        
                        c1, c2 = st.columns(2)
                        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "content.pdf", "application/pdf")
                        c2.download_button("📝 ดาวน์โหลด Word", word, "content.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                        
                    except Exception as e:
                        st.error(f"❌ เกิดข้อผิดพลาด: {e}")


st.caption("พัฒนาโดย **Nong Aom & P'Em** | Powered by Google Gemini AI")
