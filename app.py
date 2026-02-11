# app.py (EasyWorksheet Pro Max - Thai Version)
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

# Session State for API Key
if "api_key" not in st.session_state:
    st.session_state.api_key = api_key

generator = WorksheetGenerator(ai_api_key=st.session_state.api_key)

st.set_page_config(page_title="โปรแกรมสร้างใบงาน EasyWorksheet", page_icon="🚀", layout="wide")

st.title("🚀 โปรแกรมสร้างใบงาน EasyWorksheet")
st.caption("ระบบสร้างใบงานอัตโนมัติด้วย AI สำหรับคุณครูยุคใหม่ (Created by Nong Aom & P'Em)")

# --- Settings Sidebar ---
with st.sidebar:
    st.header("⚙️ แผงควบคุม (Control Panel)")
    
    # API Key Input
    if not st.session_state.api_key:
        api_input = st.text_input("🔑 ใส่ Google AI API Key (สำหรับฟีเจอร์ AI)", type="password")
        st.markdown("[👉 กดที่นี่เพื่อขอรับ API Key ฟรี (Google AI Studio)](https://aistudio.google.com/app/apikey)")
        
        if api_input:
            clean_key = api_input.strip()
            # Validate Key
            try:
                genai.configure(api_key=clean_key)
                list(genai.list_models()) # Test call
                st.session_state.api_key = clean_key
                st.rerun()
            except:
                st.error("API Key ไม่ถูกต้อง")
    else:
        st.success("✅ เชื่อมต่อระบบ AI แล้ว")
        if st.button("ออกจากระบบ (Clear Key)"):
            st.session_state.api_key = None
            st.rerun()

    # Re-init generator if key is present
    if st.session_state.api_key:
        generator = WorksheetGenerator(ai_api_key=st.session_state.api_key)

    school_name = st.text_input("🏫 ชื่อโรงเรียน / ชื่อคุณครู", "โรงเรียนตัวอย่าง")
    
    uploaded_logo = st.file_uploader("🖼️ อัปโหลดโลโก้โรงเรียน (ถ้ามี)", type=["png", "jpg", "jpeg"])
    
    st.markdown("---")
    
    # Mode Selection (Thai)
    mode_options = [
        "➕ ฝึกทักษะคณิตศาสตร์ (Math)",
        "🤖 โจทย์ปัญหา AI (Word Problems)",
        "🔍 ปริศนาหาคำศัพท์ (Word Search)",
        "✍️ ฝึกคัดลายมือ (Handwriting)",
        "📝 สร้างข้อสอบจากไฟล์ (File to Quiz)"
    ]
    mode_select = st.selectbox("เลือกประเภทใบงาน:", mode_options)
    
    title = st.text_input("หัวข้อใบงาน", "แบบฝึกหัดที่ 1")
    
    include_qr = st.checkbox("เพิ่ม QR Code เฉลย?", value=True)
    qr_url = st.text_input("ลิงก์เฉลย (เช่น Google Drive)", "https://example.com/answers") if include_qr else None

# --- Main Content Area ---

if "คณิตศาสตร์" in mode_select:
    st.subheader("🧮 สร้างโจทย์คณิตศาสตร์")
    
    grade_preset = st.selectbox("เลือกระดับชั้น:", ["กำหนดเอง", "อนุบาล 3", "ป.1", "ป.2", "ป.3", "ป.4-6"])
    
    # Auto-config ranges
    d_min, d_max = 1, 20
    if "อนุบาล" in grade_preset: d_min, d_max = 1, 10
    elif "ป.1" in grade_preset: d_min, d_max = 1, 20
    elif "ป.2" in grade_preset: d_min, d_max = 10, 100
    elif "ป.3" in grade_preset: d_min, d_max = 10, 1000
    elif "ป.4" in grade_preset: d_min, d_max = 100, 10000

    col1, col2 = st.columns(2)
    with col1:
        op_label = st.selectbox("เลือกเครื่องหมาย", ["บวก (+)", "ลบ (-)", "คูณ (x)", "หาร (÷)"])
        # Map Thai label to English key for backend
        op_map = {"บวก (+)": "Addition (+)", "ลบ (-)": "Subtraction (-)", "คูณ (x)": "Multiplication (x)", "หาร (÷)": "Division (÷)"}
        op = op_map[op_label]
        num_q = st.slider("จำนวนข้อ", 10, 50, 20)
    with col2:
        min_v = st.number_input("ค่าต่ำสุด", 1, 100000, d_min)
        max_v = st.number_input("ค่าสูงสุด", 10, 100000, d_max)
    
    if st.button("🚀 สร้างใบงานคณิตศาสตร์", type="primary"):
        questions, answers = generator.generate_questions(op, num_q, min_v, max_v)
        pdf = generator.create_pdf(title, school_name, "Math Questions", questions, answers, qr_url, uploaded_logo)
        word = generator.create_word_doc(title, school_name, "Math Questions", questions, answers)
        
        st.success("สร้างสำเร็จ! ดาวน์โหลดได้ที่ด้านล่าง")
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "math_worksheet.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", word, "math_worksheet.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "โจทย์ปัญหา AI" in mode_select:
    st.subheader("🤖 สร้างโจทย์ปัญหาด้วย AI")
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("หัวข้อ (เช่น อวกาศ, สวนสัตว์, ตลาด)", "การผจญภัยในอวกาศ")
        grade = st.selectbox("ระดับชั้น", ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6"])
    with col2:
        num_q = st.slider("จำนวนข้อ", 3, 15, 5)
    
    if st.button("🚀 ให้ AI สร้างโจทย์", type="primary"):
        if not st.session_state.api_key:
            st.error("กรุณาใส่ API Key ในช่องด้านซ้ายก่อนครับ")
        else:
            with st.spinner("AI กำลังคิดโจทย์... (รอสักครู่นะครับ)"):
                # Map Thai Grade to Eng
                grade_map = {"ป.1": "Grade 1", "ป.2": "Grade 2", "ป.3": "Grade 3", "ป.4": "Grade 4", "ป.5": "Grade 5", "ป.6": "Grade 6"}
                questions, answers = generator.generate_ai_word_problems(topic, grade_map.get(grade, "Grade 3"), num_q)
                
                pdf = generator.create_pdf(title, school_name, "AI Word Problems", questions, answers, qr_url, uploaded_logo)
                word = generator.create_word_doc(title, school_name, "AI Word Problems", questions, answers)
                
                st.success("สร้างโจทย์เสร็จแล้ว!")
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
        
        st.success("สร้างปริศนาเรียบร้อย!")
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
        
        st.success("สร้างสำเร็จ!")
        c1, c2 = st.columns(2)
        c1.download_button("📄 ดาวน์โหลด PDF", pdf, "tracing.pdf", "application/pdf")
        c2.download_button("📝 ดาวน์โหลด Word", word, "tracing.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif "สร้างข้อสอบจากไฟล์" in mode_select:
    st.subheader("📝 สร้างข้อสอบจากไฟล์เอกสาร (PDF/Word)")
    
    uploaded_file = st.file_uploader("อัปโหลดเอกสารประกอบการสอน (PDF หรือ Docx)", type=["pdf", "docx"])
    num_q = st.slider("จำนวนข้อสอบที่ต้องการ", 3, 20, 5)
    
    if uploaded_file and st.button("🚀 สร้างข้อสอบจากไฟล์", type="primary"):
        if not st.session_state.api_key:
             st.error("ฟีเจอร์นี้ต้องใช้ AI กรุณาใส่ API Key ด้านซ้ายครับ")
        else:
            with st.spinner("AI กำลังอ่านไฟล์และออกข้อสอบ..."):
                text = generator.extract_text_from_file(uploaded_file)
                
                if not text or "Error" in text:
                    st.error(f"อ่านไฟล์ล้มเหลว: {text}")
                else:
                    questions, answers = generator.generate_quiz_from_text(text, num_q)
                    
                    pdf = generator.create_pdf(title, school_name, "Quiz", questions, answers, qr_url, uploaded_logo)
                    word = generator.create_word_doc(title, school_name, "Quiz", questions, answers)
                    
                    st.success(f"สร้างข้อสอบ {len(questions)} ข้อ สำเร็จแล้ว!")
                    c1, c2 = st.columns(2)
                    c1.download_button("📄 ดาวน์โหลด PDF", pdf, "quiz.pdf", "application/pdf")
                    c2.download_button("📝 ดาวน์โหลด Word", word, "quiz.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    
                    with st.expander("ดูตัวอย่างข้อสอบ"):
                        for q in questions:
                            st.text(q)
                            st.text("---")

st.markdown("---")
st.caption("พัฒนาโดย **Nong Aom & P'Em** | Powered by Google Gemini AI")
