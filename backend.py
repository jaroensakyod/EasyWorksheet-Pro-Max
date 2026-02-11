# backend.py
# Backend Logic: Generates Questions and PDF using ReportLab
# This separates the "Business Logic" from the "Presentation Layer" (Frontend)

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

class WorksheetGenerator:
    def __init__(self, ai_api_key=None):
        if ai_api_key:
            genai.configure(api_key=ai_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

        # Register Thai Font for PDF
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        self.font_name = 'Helvetica' # Default fallback
        try:
            # Try to register a Thai font available on Windows
            pdfmetrics.registerFont(TTFont('ThaiFont', 'C:/Windows/Fonts/tahoma.ttf'))
            self.font_name = 'ThaiFont'
        except:
            try:
                pdfmetrics.registerFont(TTFont('ThaiFont', 'C:/Windows/Fonts/leelawad.ttf'))
                self.font_name = 'ThaiFont'
            except:
                print("Warning: Thai font not found. Using Helvetica.")

    def generate_questions(self, operation, num_questions, min_val, max_val):
        """Generates a list of math questions and answers."""
        questions = []
        answers = []

        for _ in range(num_questions):
            # Generate numbers
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)

            question_text = ""
            answer_val = 0

            if operation == "Addition (+)":
                question_text = f"{a} + {b} = ____"
                answer_val = a + b
            elif operation == "Subtraction (-)":
                # Ensure positive result for kids
                if a < b: a, b = b, a
                question_text = f"{a} - {b} = ____"
                answer_val = a - b
            elif operation == "Multiplication (x)":
                # Limit multiplication size a bit to keep it reasonable
                question_text = f"{a} x {b} = ____"
                answer_val = a * b
            elif operation == "Division (÷)":
                # Ensure clean division
                answer_val = random.randint(min_val, max_val) # Pick answer first
                a = answer_val * b # Calculate dividend
                question_text = f"{a} ÷ {b} = ____"

            questions.append(question_text)
            answers.append(f"{answer_val}")

        return questions, answers

    def generate_ai_word_problems(self, topic, grade_level, num_questions):
        """Uses AI to generate unique math word problems."""
        if not self.model:
            return ["Error: No AI Key"], ["Please add API Key"]
        
        prompt = f"""
        Generate {num_questions} math word problems for {grade_level} students about '{topic}'.
        Provide the output in this format:
        Q: [Question 1]
        A: [Answer 1]
        Q: [Question 2]
        A: [Answer 2]
        ...
        Make the questions fun and creative!
        """
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            questions = []
            answers = []
            lines = text.strip().split('\n')
            current_q = ""
            for line in lines:
                if line.startswith("Q:"):
                    current_q = line.replace("Q:", "").strip()
                    questions.append(current_q)
                elif line.startswith("A:"):
                    answers.append(line.replace("A:", "").strip())
            # Basic fallback if parsing fails
            if len(questions) == 0:
                 return [text], ["See question"]
            return questions, answers
        except Exception as e:
            return [f"AI Error: {str(e)}"], ["Error"]

    def generate_word_search(self, words):
        """Generates a Word Search puzzle grid."""
        size = 15 # 15x15 grid
        grid = [[' ' for _ in range(size)] for _ in range(size)]
        placed_words = []
        
        # Clean words
        words = [w.strip().upper() for w in words if w.strip()]

        for word in words:
            word_clean = word.replace(" ", "")
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                direction = random.choice([(0, 1), (1, 0), (1, 1)]) # H, V, D
                start_row = random.randint(0, size - 1)
                start_col = random.randint(0, size - 1)
                
                # Check bounds
                end_row = start_row + direction[0] * (len(word_clean) - 1)
                end_col = start_col + direction[1] * (len(word_clean) - 1)
                
                if 0 <= end_row < size and 0 <= end_col < size:
                    # Check collision
                    can_place = True
                    for i in range(len(word_clean)):
                        r, c = start_row + direction[0]*i, start_col + direction[1]*i
                        if grid[r][c] != ' ' and grid[r][c] != word_clean[i]:
                            can_place = False
                            break
                    if can_place:
                        for i in range(len(word_clean)):
                            r, c = start_row + direction[0]*i, start_col + direction[1]*i
                            grid[r][c] = word_clean[i]
                        placed_words.append(word)
                        placed = True
                attempts += 1

        # Fill empty spaces
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        for r in range(size):
            for c in range(size):
                if grid[r][c] == ' ':
                    grid[r][c] = random.choice(letters)
        
        return grid, placed_words

    def create_qr_code(self, data):
        """Generates a QR Code image."""
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    def create_pdf(self, title, school_name, content_type, data, answers=None, qr_link=None):
        """Creates a PDF file in memory."""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Header & Border
        self._draw_header(c, width, height, title, school_name)
        
        # QR Code (Optional)
        if qr_link:
            qr_img = self.create_qr_code(qr_link)
            c.drawImage(ImageReader(qr_img), width - 4*cm, height - 3.5*cm, width=2.5*cm, height=2.5*cm)
            c.setFont("Helvetica", 8)
            c.drawCentredString(width - 2.75*cm, height - 3.7*cm, "Scan for Answers")

        # Content Logic
        y_start = height - 6 * cm
        
        if content_type == "Math Questions" or content_type == "AI Word Problems":
            self._draw_questions(c, data, y_start)
        elif content_type == "Word Search":
            grid, words = data
            self._draw_word_search(c, grid, words, y_start)
        elif content_type == "Handwriting Practice":
            self._draw_handwriting(c, data, y_start, width)

        # Footer
        c.setFont(self.font_name, 10)
        c.setFillColor(lightgrey)
        c.drawCentredString(width / 2, 1.5 * cm, f"Generated by EasyWorksheet Pro")
        c.showPage() # End Page 1

        # Answer Key Page
        if answers:
            self._draw_answer_key(c, width, height, title, answers)

        c.save()
        buffer.seek(0)
        return buffer
    
    def generate_tracing_lines(self, text_input): 
        """Generates content for handwriting practice."""
        lines = []
        words = text_input.split(",")
        for word in words:
            clean_word = word.strip()
            # Repeat word to fill line (approx 3 times for phrases, 5 for words)
            if len(clean_word) > 10:
                 line_content = (clean_word + "   ") * 2
            else:
                 line_content = (clean_word + "   ") * 5
            lines.append(line_content)
        return lines

    def _draw_handwriting(self, c, lines, y_start, width):
        c.setFont("Courier", 30) # Use Courier as placeholder for dotted font
        c.setFillColor(lightgrey) 
        
        line_height = 2.5*cm 
        
        current_y = y_start
        for line in lines:
            # Draw guidelines first
            c.setLineWidth(1)
            c.setStrokeColor(black)
            # Top line
            c.line(2*cm, current_y + 10, width - 2*cm, current_y + 10) 
            # Bottom line
            c.line(2*cm, current_y - 10, width - 2*cm, current_y - 10) 
            
            # Middle Dashed line
            c.setDash(3, 3) 
            c.line(2*cm, current_y, width - 2*cm, current_y) 
            c.setDash([]) 
            
            # Text
            c.drawString(2*cm, current_y - 8, line) # Adjust y slightly for baseline
            
            current_y -= line_height
            
            if current_y < 3*cm:
                c.showPage()
                current_y = height - 5*cm

    def _draw_header(self, c, w, h, title, school):
        c.setStrokeColor(blue)
        c.setLineWidth(2)
        c.setDash(6, 3)
        c.rect(1*cm, 1*cm, w-2*cm, h-2*cm)
        c.setDash([])
        c.setStrokeColor(black)
        
        c.setFont(self.font_name, 24)
        c.drawCentredString(w/2, h-2.5*cm, title)
        c.setFont(self.font_name, 14)
        c.setFillColor(blue)
        c.drawCentredString(w/2, h-3.5*cm, school)
        c.setFillColor(black)
        c.setFont(self.font_name, 12)
        c.drawString(2*cm, h-4.5*cm, "Name: __________________________")
        c.drawString(13*cm, h-4.5*cm, "Date: ______________")

    def _draw_questions(self, c, questions, y_start):
        c.setFont(self.font_name, 14) 
        current_y = y_start
        # If questions list is short (e.g. word problems), give more space
        is_word_problem = len(questions) <= 10
        
        for i, q in enumerate(questions):
            text_object = c.beginText(2.5*cm, current_y)
            text_object.setFont(self.font_name, 14)
            
            # Simple word wrapping
            words = q.split()
            line = []
            for word in words:
                line.append(word)
                if len(" ".join(line)) > 50: # approx char limit
                    text_object.textLine(" ".join(line[:-1]))
                    line = [word]
            text_object.textLine(" ".join(line))
            c.drawText(text_object)
            
            space_needed = 3*cm if is_word_problem else 1.5*cm
            current_y -= space_needed
            
            if current_y < 3*cm:
                c.showPage()
                current_y = 25*cm 

    def _draw_word_search(self, c, grid, words, y_start):
        c.setFont("Courier-Bold", 14) 
        grid_start_y = y_start
        grid_start_x = 3*cm # Centered roughly
        cell_size = 0.8*cm
        
        for r, row in enumerate(grid):
            for col, char in enumerate(row):
                c.drawString(grid_start_x + (col * cell_size), grid_start_y - (r * cell_size), char)
        
        word_list_y = grid_start_y - (len(grid) * cell_size) - 1*cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, word_list_y, "Find these words:")
        c.setFont("Helvetica", 12)
        
        col_count = 0
        current_y = word_list_y - 1*cm
        x_pos = 2*cm
        for word in words:
            c.drawString(x_pos, current_y, f"- {word}")
            col_count += 1
            if col_count % 4 == 0: 
                x_pos += 4.5*cm
                current_y = word_list_y - 1*cm
            else:
                current_y -= 0.7*cm

    def _draw_answer_key(self, c, w, h, title, answers):
        c.setFont(self.font_name, 20)
        c.drawCentredString(w/2, h-2.5*cm, f"ANSWER KEY: {title}")
        y = h-4*cm
        c.setFont(self.font_name, 12)
        for i, ans in enumerate(answers):
            c.drawString(3*cm, y, f"{i+1}) {ans}")
            y -= 0.8*cm
            if y < 2*cm:
                c.showPage()
                y = h-3*cm
        c.showPage()
    
    def create_word_doc(self, title, school_name, content_type, data, answers=None):
        """Creates a Word (.docx) file."""
        doc = Document()
        
        # --- Page Setup (A4) ---
        section = doc.sections[0]
        section.page_height = Cm(29.7)
        section.page_width = Cm(21.0)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)

        # --- Header ---
        header = section.header
        htable = header.add_table(1, 2, width=Cm(17))
        htable.autofit = False
        htable.columns[0].width = Cm(8.5)
        htable.columns[1].width = Cm(8.5)
        
        # Left Header (School Name)
        cell_left = htable.cell(0, 0)
        p_left = cell_left.paragraphs[0]
        p_left.text = school_name
        p_left.style.font.name = 'Arial'
        p_left.style.font.size = Pt(14)
        p_left.style.font.bold = True
        
        # Right Header (Title)
        cell_right = htable.cell(0, 1)
        p_right = cell_right.paragraphs[0]
        p_right.text = title
        p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_right.style.font.name = 'Arial'
        p_right.style.font.size = Pt(14)

        # --- Title ---
        h1 = doc.add_heading(title, level=1)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # --- Student Info ---
        p_info = doc.add_paragraph()
        p_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p_info.add_run(f"Name: __________________________  Date: ______________  Score: ____")
        run.font.size = Pt(12)
        
        doc.add_paragraph() # Spacer

        # --- Content Logic ---
        if content_type == "Math Questions" or content_type == "AI Word Problems":
            if content_type == "Math Questions":
                table = doc.add_table(rows=(len(data)//2) + 1, cols=2)
                table.autofit = True
                for i, q in enumerate(data):
                    row = i // 2
                    col = i % 2
                    cell = table.cell(row, col)
                    cell.text = f"{i+1}) {q}"
                    cell.paragraphs[0].paragraph_format.space_after = Pt(24) 
            else: 
                for i, q in enumerate(data):
                    p = doc.add_paragraph(f"{i+1}. {q}")
                    p.paragraph_format.space_after = Pt(36) 

        elif content_type == "Word Search":
            grid, words = data
            # Draw Grid (Table)
            table = doc.add_table(rows=len(grid), cols=len(grid[0]))
            table.style = 'Table Grid'
            table.autofit = False 
            
            for r, row in enumerate(grid):
                for c, char in enumerate(row):
                    cell = table.cell(r, c)
                    cell.text = char
                    cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cell.width = Cm(0.8)
                    cell.height = Cm(0.8)
            
            doc.add_paragraph() 
            doc.add_heading("Find these words:", level=2)
            p_words = doc.add_paragraph(", ".join(words))

        elif content_type == "Handwriting Practice":
            for line in data:
                p = doc.add_paragraph(line)
                p.style.font.name = 'Courier New' # Placeholder
                p.style.font.size = Pt(24)
                p.style.font.color.rgb = None # Default black
                p.paragraph_format.space_after = Pt(24)

        # --- Answer Key (New Page) ---
        if answers:
            doc.add_page_break()
            doc.add_heading(f"Answer Key: {title}", level=1)
            if isinstance(answers, list):
                for i, ans in enumerate(answers):
                    doc.add_paragraph(f"{i+1}) {ans}")

        # Save to Buffer
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
