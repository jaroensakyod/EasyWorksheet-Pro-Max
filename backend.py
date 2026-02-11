# backend.py (Updated with PDF/Docx Extraction and Quiz Gen)
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import black, lightgrey, blue
import io
import qrcode
from reportlab.lib.utils import ImageReader
import google.generativeai as genai
import os
from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
from pypdf import PdfReader

class WorksheetGenerator:
    def __init__(self, ai_api_key=None):
        if ai_api_key:
            genai.configure(api_key=ai_api_key)
            
            # Smart Model Detection (Try multiple models until one works)
            model_priority = [
                'gemini-1.5-flash',
                'gemini-1.5-pro', 
                'gemini-pro',
                'gemini-1.0-pro'
            ]
            
            self.model = None
            self.model_name = None
            
            try:
                # List available models
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Find first matching model
                for model_name in model_priority:
                    for available in available_models:
                        if model_name in available:
                            self.model = genai.GenerativeModel(available)
                            self.model_name = available
                            print(f"✅ Using AI Model: {available}")
                            break
                    if self.model:
                        break
                
                # If still no model, use first available
                if not self.model and available_models:
                    self.model = genai.GenerativeModel(available_models[0])
                    self.model_name = available_models[0]
                    print(f"✅ Using AI Model: {available_models[0]}")
                    
            except Exception as e:
                print(f"⚠️ Model detection failed: {e}")
                # Last resort fallback
                try:
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.model_name = 'gemini-pro'
                except:
                    self.model = None
        else:
            self.model = None
            self.model_name = None

        # Register Thai Font for PDF (Fallback logic)
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        self.font_name = 'Helvetica'
        try:
            pdfmetrics.registerFont(TTFont('ThaiFont', 'C:/Windows/Fonts/tahoma.ttf'))
            self.font_name = 'ThaiFont'
        except:
            try:
                pdfmetrics.registerFont(TTFont('ThaiFont', 'C:/Windows/Fonts/leelawad.ttf'))
                self.font_name = 'ThaiFont'
            except:
                pass

    def extract_text_from_file(self, uploaded_file):
        """Extracts text from PDF or Docx."""
        text = ""
        try:
            if uploaded_file.name.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            elif uploaded_file.name.endswith(".docx"):
                doc = Document(uploaded_file)
                for para in doc.paragraphs:
                    text += para.text + "\n"
        except Exception as e:
            return f"Error extracting text: {e}"
        return text

    def generate_quiz_from_text(self, text, num_questions=5, grade="General"):
        """Generates a multiple choice quiz from text using AI."""
        if not self.model:
            return ["Error: No AI Key"], ["Please add API Key"]
        
        # Limit text to avoid token limits (approx first 2000 chars)
        context_text = text[:3000] 
        
        prompt = f"""
        Create a {num_questions}-question multiple choice quiz (in Thai) based on this text:
        "{context_text}"
        
        Target audience: {grade}
        Format exactly like this for each question:
        Q: [Question]
        A: [Option A]
        B: [Option B]
        C: [Option C]
        D: [Option D]
        Ans: [Correct Letter]
        """
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            # Parse is tricky, let's keep it simple string list for PDF now
            # We will split by "Q:"
            questions = []
            answers = [] # We can store correct answers separately if needed
            
            raw_qs = content.split("Q:")
            for raw in raw_qs:
                if not raw.strip(): continue
                lines = raw.strip().split('\n')
                q_text = lines[0].strip()
                options = []
                correct = ""
                for line in lines[1:]:
                    if line.startswith("Ans:"): correct = line.replace("Ans:", "").strip()
                    elif line.strip(): options.append(line.strip())
                
                if q_text:
                    full_q = q_text + "\n" + "\n".join(options)
                    questions.append(full_q)
                    answers.append(correct)
            
            return questions, answers
        except Exception as e:
            return [f"AI Error: {str(e)}"], ["Error"]

    def generate_questions(self, operation, num_questions, min_val, max_val):
        # ... (Existing Math Logic) ...
        questions = []
        answers = []
        for _ in range(num_questions):
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            question_text = ""
            answer_val = 0
            if operation == "Addition (+)":
                question_text = f"{a} + {b} = ____"
                answer_val = a + b
            elif operation == "Subtraction (-)":
                if a < b: a, b = b, a
                question_text = f"{a} - {b} = ____"
                answer_val = a - b
            elif operation == "Multiplication (x)":
                question_text = f"{a} x {b} = ____"
                answer_val = a * b
            elif operation == "Division (÷)":
                answer_val = random.randint(min_val, max_val)
                a = answer_val * b
                question_text = f"{a} ÷ {b} = ____"
            questions.append(question_text)
            answers.append(str(answer_val))
        return questions, answers

    def generate_ai_word_problems(self, topic, grade_level, num_questions):
        # ... (Existing AI Logic) ...
        if not self.model: return ["No Key"], ["No Key"]
        prompt = f"Generate {num_questions} math word problems (Thai) for {grade_level} about '{topic}'. Output format:\nQ: [Question]\nA: [Answer]"
        try:
            resp = self.model.generate_content(prompt)
            qs, ans = [], []
            for line in resp.text.split('\n'):
                if line.startswith("Q:"): qs.append(line.replace("Q:", "").strip())
                elif line.startswith("A:"): ans.append(line.replace("A:", "").strip())
            return qs, ans
        except: return ["Error"], ["Error"]

    def generate_word_search(self, words, grid_size=15):
        # ... (Existing Word Search Logic with grid_size) ...
        size = grid_size
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        placed_words = []
        words = [w.strip().upper() for w in words if w.strip()]
        for word in words:
            word_clean = word.replace(" ", "")
            if len(word_clean) > size: continue
            placed = False; attempts = 0
            while not placed and attempts < 100:
                d = random.choice([(0,1),(1,0),(1,1)])
                r = random.randint(0,size-1); c = random.randint(0,size-1)
                er = r + d[0]*(len(word_clean)-1); ec = c + d[1]*(len(word_clean)-1)
                if 0<=er<size and 0<=ec<size:
                    can = True
                    for i in range(len(word_clean)):
                        if grid[r+d[0]*i][c+d[1]*i] not in [' ', word_clean[i]]: can = False; break
                    if can:
                        for i in range(len(word_clean)): grid[r+d[0]*i][c+d[1]*i] = word_clean[i]
                        placed_words.append(word); placed = True
                attempts += 1
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for r in range(size):
            for c in range(size):
                if grid[r][c] == ' ': grid[r][c] = random.choice(letters)
        return grid, placed_words

    def generate_tracing_lines(self, text_input):
        lines = []
        words = text_input.split(",")
        for word in words:
            w = word.strip()
            lines.append((w + "   ") * (5 if len(w)<10 else 2))
        return lines

    # --- PDF Creation ---
    def create_qr_code(self, data):
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(data); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        b = io.BytesIO(); img.save(b, format="PNG"); b.seek(0)
        return b

    def create_pdf(self, title, school_name, content_type, data, answers=None, qr_link=None, uploaded_logo=None):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        w, h = A4
        
        # Header
        c.setStrokeColor(blue); c.setLineWidth(2); c.setDash(6,3)
        c.rect(1*cm, 1*cm, w-2*cm, h-2*cm); c.setDash([]); c.setStrokeColor(black)
        
        if uploaded_logo:
            try:
                logo = Image.open(uploaded_logo)
                c.drawImage(ImageReader(logo), 2*cm, h-4*cm, width=2.5*cm, height=2.5*cm, mask='auto')
            except: pass

        c.setFont(self.font_name, 24); c.drawCentredString(w/2, h-2.5*cm, title)
        c.setFont(self.font_name, 14); c.setFillColor(blue); c.drawCentredString(w/2, h-3.5*cm, school_name); c.setFillColor(black)
        c.setFont(self.font_name, 12)
        c.drawString(2*cm, h-4.5*cm, "Name: __________________________  Date: ______________")

        if qr_link:
            qr = self.create_qr_code(qr_link)
            c.drawImage(ImageReader(qr), w-4*cm, h-3.5*cm, width=2.5*cm, height=2.5*cm)

        # Body
        y = h - 6*cm
        if content_type in ["Math Questions", "AI Word Problems", "Quiz"]:
            c.setFont(self.font_name, 14)
            for i, q in enumerate(data):
                # Basic wrapping logic
                text = c.beginText(2.5*cm, y)
                text.setFont(self.font_name, 14)
                # Split newlines for Quiz
                lines = q.split('\n')
                for line in lines:
                    text.textLine(line)
                c.drawText(text)
                
                # Dynamic spacing
                height_needed = len(lines) * 0.7*cm + 1*cm
                y -= height_needed
                if y < 3*cm: c.showPage(); y = h-4*cm
        
        elif content_type == "Word Search":
            grid, words = data
            c.setFont("Courier-Bold", 14)
            start_x = 3*cm
            cell = 0.8*cm
            for r, row in enumerate(grid):
                for col, char in enumerate(row):
                    c.drawString(start_x + col*cell, y - r*cell, char)
            
            y_words = y - len(grid)*cell - 1*cm
            c.setFont(self.font_name, 12)
            c.drawString(2*cm, y_words, "Find: " + ", ".join(words))

        elif content_type == "Handwriting Practice":
            c.setFont("Courier", 30); c.setFillColor(lightgrey)
            for line in data:
                c.setLineWidth(1); c.setStrokeColor(black)
                c.line(2*cm, y+10, w-2*cm, y+10)
                c.line(2*cm, y-10, w-2*cm, y-10)
                c.setDash(3,3); c.line(2*cm, y, w-2*cm, y); c.setDash([])
                c.drawString(2*cm, y-8, line)
                y -= 2.5*cm
                if y < 3*cm: c.showPage(); y = h-5*cm

        c.showPage()
        
        # Answers
        if answers:
            c.setFont(self.font_name, 20); c.drawCentredString(w/2, h-2.5*cm, f"ANSWER KEY: {title}")
            y = h-4*cm; c.setFont(self.font_name, 12)
            for i, ans in enumerate(answers):
                c.drawString(3*cm, y, f"{i+1}) {ans}"); y -= 0.8*cm
                if y < 2*cm: c.showPage(); y = h-4*cm
            c.showPage()

        c.save(); buffer.seek(0)
        return buffer

    # --- Word Doc ---
    def create_word_doc(self, title, school_name, content_type, data, answers=None):
        doc = Document()
        # Header/Setup skipped for brevity (keeping core logic)
        doc.add_heading(title, 0)
        doc.add_paragraph(f"{school_name}\nName: ________________ Date: _________")
        
        if content_type in ["Math Questions", "AI Word Problems", "Quiz"]:
            for i, q in enumerate(data):
                doc.add_paragraph(f"{i+1}. {q}")
                doc.add_paragraph("_"*20)
        elif content_type == "Word Search":
            grid, words = data
            table = doc.add_table(len(grid), len(grid[0]))
            for r, row in enumerate(grid):
                for c, char in enumerate(row):
                    table.cell(r,c).text = char
            doc.add_paragraph("Find: " + ", ".join(words))
        elif content_type == "Handwriting Practice":
            for line in data: doc.add_paragraph(line)
            
        if answers:
            doc.add_page_break(); doc.add_heading("Answers", 1)
            for i, a in enumerate(answers): doc.add_paragraph(f"{i+1}) {a}")
            
        b = io.BytesIO(); doc.save(b); b.seek(0)
        return b
