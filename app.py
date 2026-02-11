# app.py
# Frontend Logic: User Interface (Streamlit)
# This handles user input, button clicks, and PDF/Word download

import streamlit as st
import random
import os
import sys

# Add the current directory to path so we can import backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend import WorksheetGenerator

# Initialize Generator (Try to get API Key from secrets or input)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

generator = WorksheetGenerator(ai_api_key=api_key)

st.set_page_config(page_title="โปรแกรมสร้างใบงาน EasyWorksheet", page_icon="🚀", layout="wide")

st.title("🚀 โปรแกรมสร้างใบงาน EasyWorksheet")
st.caption("AI-Powered Worksheet Generator for Modern Teachers (ระบบสร้างใบงานด้วย AI สำหรับครูยุคใหม่)")

# --- Settings Sidebar ---
with st.sidebar:
    st.header("⚙️ แผงควบคุม")
    
    # API Key Input (if not set)
    # API Key Input (if not set)
    if not api_key:
        api_key_input = st.text_input("ใส่ Google AI API Key (สำหรับฟีเจอร์ AI)", type="password")
        if api_key_input:
            generator = WorksheetGenerator(ai_api_key=api_key_input)
    
    school_name = st.text_input("ชื่อโรงเรียน / คุณครู", "โรงเรียนตัวอย่าง")
    title = st.text_input("หัวข้อใบงาน", "แบบฝึกหัดที่ 1")
    
    # Feature Selection
    mode = st.radio("เลือกประเภทใบงาน:", ["ฝึกคณิตศาสตร์ (Math)", "โจทย์ปัญหา AI (AI Word Problems)", "ปริศนาคำศัพท์ (Word Search)", "ฝึกคัดลายมือ (Handwriting)"])
    
    # QR Code Option
    include_qr = st.checkbox("เพิ่ม QR Code เฉลย?", value=True)
    qr_url = st.text_input("ลิงก์เฉลย (เช่น Google Drive)", "https://example.com/answers") if include_qr else None

# --- Main Content Area ---
if mode == "ฝึกคณิตศาสตร์ (Math)":
    st.subheader("🧮 สร้างโจทย์คณิตศาสตร์")
    col1, col2 = st.columns(2)
    with col1:
        op = st.selectbox("เลือกเครื่องหมาย", ["บวก (+)", "ลบ (-)", "คูณ (x)", "หาร (÷)"])
        # Map back to English for logic
        op_map = {"บวก (+)": "Addition (+)", "ลบ (-)": "Subtraction (-)", "คูณ (x)": "Multiplication (x)", "หาร (÷)": "Division (÷)"}
        op = op_map[op]
        num_q = st.slider("จำนวนข้อ", 10, 50, 20)
    with col2:
        min_v = st.number_input("ค่าต่ำสุด", 1, 100, 2)
        max_v = st.number_input("ค่าสูงสุด", 10, 1000, 12)
    
    if st.button("สร้างใบงานคณิตศาสตร์", type="primary"):
        questions, answers = generator.generate_questions(op, num_q, min_v, max_v)
        pdf = generator.create_pdf(title, school_name, "Math Questions", questions, answers, qr_url)
        word = generator.create_word_doc(title, school_name, "Math Questions", questions, answers)
        
        st.success("สร้างสำเร็จ! ดาวน์โหลดได้ที่นี่")
        col1, col2 = st.columns(2)
        col1.download_button("ดาวน์โหลด PDF", pdf, "math_worksheet.pdf", "application/pdf")
        col2.download_button("ดาวน์โหลด Word (.docx)", word, "math_worksheet.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif mode == "โจทย์ปัญหา AI (AI Word Problems)":
    st.subheader("🤖 สร้างโจทย์ปัญหาด้วย AI")
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("หัวข้อ (เช่น ผลไม้, อวกาศ, สัตว์โลก)", "การผจญภัยในอวกาศ")
        grade = st.selectbox("ระดับชั้น", ["ป.1 (Grade 1)", "ป.2 (Grade 2)", "ป.3 (Grade 3)", "ป.4 (Grade 4)"])
    with col2:
        num_q = st.slider("จำนวนข้อ", 5, 20, 5)
    
    if st.button("สร้างใบงานด้วย AI", type="primary"):
        with st.spinner("AI กำลังคิด... (รอสักครู่นะคะ)"):
            questions, answers = generator.generate_ai_word_problems(topic, grade, num_q)
            pdf = generator.create_pdf(title, school_name, "AI Word Problems", questions, answers, qr_url)
            word = generator.create_word_doc(title, school_name, "AI Word Problems", questions, answers)
            
            st.success("AI สร้างเสร็จแล้ว! ดาวน์โหลดได้เลย")
            col1, col2 = st.columns(2)
            col1.download_button("ดาวน์โหลดใบงาน AI (PDF)", pdf, "ai_worksheet.pdf", "application/pdf")
            col2.download_button("ดาวน์โหลดใบงาน AI (Word)", word, "ai_worksheet.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif mode == "ปริศนาคำศัพท์ (Word Search)":
    st.subheader("🔍 สร้างปริศนาคำศัพท์")
    words_input = st.text_area("ใส่คำศัพท์ (คั่นด้วยจุลภาค ,)", "APPLE, BANANA, ORANGE, GRAPE, MANGO")
    words = [w.strip() for w in words_input.split(",") if w.strip()]
    
    if st.button("สร้างปริศนา", type="primary"):
        grid, placed_words = generator.generate_word_search(words)
        # Pass grid and words as data
        pdf = generator.create_pdf(title, school_name, "Word Search", (grid, placed_words), answers=placed_words, qr_link=qr_url)
        word = generator.create_word_doc(title, school_name, "Word Search", (grid, placed_words), answers=placed_words)
        
        st.success("สร้างปริศนาสำเร็จ! ดาวน์โหลดได้เลย")
        col1, col2 = st.columns(2)
        col1.download_button("ดาวน์โหลด PDF", pdf, "word_search.pdf", "application/pdf")
        col2.download_button("ดาวน์โหลด Word", word, "word_search.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif mode == "ฝึกคัดลายมือ (Handwriting)":
    st.subheader("✍️ สร้างแบบฝึกคัดลายมือ")
    text_input = st.text_area("ใส่คำหรือประโยคที่ต้องการฝึก (คั่นด้วยจุลภาค ,)", "แมว, สุนัข, นก, แอปเปิ้ล, กล้วย")
    
    if st.button("สร้างแบบฝึกคัดลายมือ", type="primary"):
        lines = generator.generate_tracing_lines(text_input)
        pdf = generator.create_pdf(title, school_name, "Handwriting Practice", lines)
        word = generator.create_word_doc(title, school_name, "Handwriting Practice", lines)
        
        st.success("สร้างสำเร็จ! ดาวน์โหลดได้เลย")
        col1, col2 = st.columns(2)
        col1.download_button("ดาวน์โหลด PDF (คัดลายมือ)", pdf, "tracing.pdf", "application/pdf")
        col2.download_button("ดาวน์โหลด Word (คัดลายมือ)", word, "tracing.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

st.markdown("---")
st.markdown("Created with ❤️ by **Nong Aom** & **P'Em**")
