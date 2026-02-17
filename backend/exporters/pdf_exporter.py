# pdf_exporter.py - PDF generation using ReportLab
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import black, lightgrey, blue
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
import os

# Register Thai font
FONT_DIR = os.path.dirname(__file__)
THAI_FONT_PATH = os.path.join(FONT_DIR, "fonts", "NotoSansThai.ttf")

# Register font if file exists
if os.path.exists(THAI_FONT_PATH):
    pdfmetrics.registerFont(TTFont('ThaiFont', THAI_FONT_PATH))
    DEFAULT_FONT = 'ThaiFont'
else:
    DEFAULT_FONT = 'Helvetica'

class PDFExporter:
    """Export worksheets to PDF format"""
    
    def __init__(self):
        self.font_name = DEFAULT_FONT
    
    def create_worksheet_pdf(self, title, school_name, topic, questions, answers, qr_url=None, uploaded_logo=None):
        """Create a PDF worksheet"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Margins
        left_margin = 1.5 * cm
        right_margin = width - 1.5 * cm
        top_margin = height - 2 * cm
        bottom_margin = 2 * cm
        
        # Header with school name
        if school_name:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin, top_margin, school_name)
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, top_margin - 1 * cm, title)
        
        # Topic
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, top_margin - 1.8 * cm, f"หัวข้อ: {topic}")
        
        # Line separator
        c.line(left_margin, top_margin - 2.3 * cm, right_margin, top_margin - 2.3 * cm)
        
        # Questions
        c.setFont("Helvetica", 12)
        y_position = top_margin - 3 * cm
        line_height = 0.8 * cm
        
        for i, question in enumerate(questions, 1):
            if y_position < bottom_margin:
                c.showPage()
                y_position = top_margin - 1 * cm
            
            c.drawString(left_margin, y_position, f"{i}. {question}")
            y_position -= line_height
        
        # Answer section on new page
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, top_margin, "เฉลย / Answer Key")
        c.setFont("Helvetica", 12)
        y_position = top_margin - 1.5 * cm
        
        for i, answer in enumerate(answers, 1):
            c.drawString(left_margin, y_position, f"{i}. {answer}")
            y_position -= 0.6 * cm
        
        # QR Code for answers
        if qr_url:
            qr = qrcode.QRCode(box_size=10, border=1)
            qr.add_data(qr_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            qr_buffer = io.BytesIO()
            qr_img.save(qr_buffer)
            qr_buffer.seek(0)
            
            qr_size = 3 * cm
            qr_image = ImageReader(qr_buffer)
            c.drawImage(qr_image, right_margin - qr_size, bottom_margin + 1 * cm, width=qr_size, height=qr_size)
            c.setFont("Helvetica", 8)
            c.drawCentredString(right_margin - qr_size / 2, bottom_margin + 0.5 * cm, "Scan for Answers")
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, 0.7 * cm, f"สร้างโดย EasyWorksheet Pro Max")
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def create_wordsearch_pdf(self, title, school_name, topic, grid, placed_words, answers=None, qr_link=None, uploaded_logo=None):
        """Create a word search PDF"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Similar structure to worksheet but with word search grid
        left_margin = 1.5 * cm
        
        if school_name:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin, height - 2 * cm, school_name)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 2.5 * cm, title)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 3 * cm, f"หัวข้อ: {topic}")
        
        # Draw grid
        cell_size = 0.8 * cm
        grid_start_y = height - 4 * cm
        
        for row_idx, row in enumerate(grid):
            for col_idx, letter in enumerate(row):
                x = left_margin + col_idx * cell_size
                y = grid_start_y - row_idx * cell_size
                c.rect(x, y, cell_size, cell_size)
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(x + cell_size / 2, y + cell_size / 2, letter)
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def create_tracing_pdf(self, title, school_name, topic, lines, uploaded_logo=None):
        """Create a tracing/handwriting practice PDF"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        left_margin = 1.5 * cm
        
        if school_name:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin, height - 2 * cm, school_name)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 2.5 * cm, title)
        
        y_position = height - 3.5 * cm
        
        for text in lines:
            # Draw lines for tracing
            for _ in range(3):
                c.setFont("Helvetica", 16)
                c.drawString(left_margin, y_position, text)
                c.setFont("Helvetica", 8)
                c.drawString(left_margin - 0.5 * cm, y_position - 0.2 * cm, "คัดลายมือ / Trace:")
                
                # Light gray line for tracing
                c.setStrokeColor(lightgrey)
                c.line(left_margin + 2 * cm, y_position - 0.3 * cm, right_margin, y_position - 0.3 * cm)
                c.setStrokeColor(black)
                y_position -= 1 * cm
            
            y_position -= 0.5 * cm
        
        c.save()
        buffer.seek(0)
        return buffer


    def create_content_pdf(self, title, school_name, content_type, questions, answers, qr_url=None, logo=None, summary=None, image=None):
        """Create a PDF with worksheet, summary, or quiz content"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        left_margin = 1.5 * cm
        right_margin = width - 1.5 * cm
        top_margin = height - 2 * cm
        bottom_margin = 2 * cm
        
        # Header
        if school_name:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin, top_margin, school_name)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, top_margin - 1 * cm, title)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, top_margin - 1.8 * cm, content_type)
        c.line(left_margin, top_margin - 2.3 * cm, right_margin, top_margin - 2.3 * cm)
        
        y_position = top_margin - 3 * cm
        
        # If summary, show it first
        if summary:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(left_margin, y_position, "สรุปเนื้อหา / Summary")
            y_position -= 0.8 * cm
            
            c.setFont("Helvetica", 11)
            # Wrap summary text
            import textwrap
            wrapper = textwrap.TextWrapper(width=70)
            wrapped_summary = wrapper.wrap(summary)
            
            for line in wrapped_summary:
                if y_position < bottom_margin:
                    c.showPage()
                    y_position = top_margin - 1 * cm
                c.drawString(left_margin, y_position, line)
                y_position -= 0.5 * cm
            
            y_position -= 0.5 * cm
        
        # Show questions
        c.setFont("Helvetica-Bold", 14)
        if "สรุป" in content_type:
            c.drawString(left_margin, y_position, "แบบทดสอบความเข้าใจ")
        else:
            c.drawString(left_margin, y_position, content_type)
        y_position -= 0.8 * cm
        
        c.setFont("Helvetica", 12)
        line_height = 0.7 * cm
        
        for i, question in enumerate(questions, 1):
            if y_position < bottom_margin:
                c.showPage()
                y_position = top_margin - 1 * cm
            
            question_text = f"{i}. {question}" if len(str(i)) == 1 else f"{i}. {question}"
            # Wrap long questions
            import textwrap
            wrapper = textwrap.TextWrapper(width=65)
            wrapped = wrapper.wrap(question_text)
            
            for line in wrapped:
                if y_position < bottom_margin:
                    c.showPage()
                    y_position = top_margin - 1 * cm
                c.drawString(left_margin + (0.5 * cm if str(i) else 0), y_position, line)
                y_position -= line_height
        
        # Answer key on new page
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, top_margin, "เฉลย / Answer Key")
        c.setFont("Helvetica", 12)
        y_position = top_margin - 1.5 * cm
        
        for i, answer in enumerate(answers, 1):
            if y_position < bottom_margin:
                c.showPage()
                y_position = top_margin - 1 * cm
            c.drawString(left_margin, y_position, f"{i}. {answer}")
            y_position -= 0.6 * cm
        
        c.save()
        buffer.seek(0)
        return buffer


    def create_summary_pdf(self, title, school_name, content_type, summary, qr_url=None, logo=None):
        """Create a PDF with summary content"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        left_margin = 1.5 * cm
        right_margin = width - 1.5 * cm
        top_margin = height - 2 * cm
        bottom_margin = 2 * cm
        
        # Header
        if school_name:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin, top_margin, school_name)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, top_margin - 1 * cm, title)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, top_margin - 1.8 * cm, content_type)
        c.line(left_margin, top_margin - 2.3 * cm, right_margin, top_margin - 2.3 * cm)
        
        y_position = top_margin - 3 * cm
        
        # Show summary
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, y_position, "สรุปเนื้อหา / Summary")
        y_position -= 0.8 * cm
        
        c.setFont("Helvetica", 11)
        # Wrap summary text
        import textwrap
        wrapper = textwrap.TextWrapper(width=65)
        wrapped_summary = wrapper.wrap(summary)
        
        for line in wrapped_summary:
            if y_position < bottom_margin:
                c.showPage()
                y_position = top_margin - 1 * cm
            c.drawString(left_margin, y_position, line)
            y_position -= 0.6 * cm
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def create_quiz_pdf(self, title, school_name, content_type, questions, answers, qr_url=None, logo=None):
        """Create a PDF with quiz content"""
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        left_margin = 1.5 * cm
        right_margin = width - 1.5 * cm
        top_margin = height - 2 * cm
        bottom_margin = 2 * cm
        
        # Header
        if school_name:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(left_margin, top_margin, school_name)
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, top_margin - 1 * cm, title)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, top_margin - 1.8 * cm, content_type)
        c.line(left_margin, top_margin - 2.3 * cm, right_margin, top_margin - 2.3 * cm)
        
        y_position = top_margin - 3 * cm
        
        # Show questions
        c.setFont("Helvetica-Bold", 14)
        c.drawString(left_margin, y_position, content_type)
        y_position -= 0.8 * cm
        
        c.setFont("Helvetica", 12)
        line_height = 0.7 * cm
        
        for i, question in enumerate(questions, 1):
            if y_position < bottom_margin:
                c.showPage()
                y_position = top_margin - 1 * cm
            
            question_text = f"{i}. {question}"
            # Wrap long questions
            import textwrap
            wrapper = textwrap.TextWrapper(width=65)
            wrapped = wrapper.wrap(question_text)
            
            for line in wrapped:
                if y_position < bottom_margin:
                    c.showPage()
                    y_position = top_margin - 1 * cm
                indent = 0.5 * cm if len(str(i)) == 1 else 0
                c.drawString(left_margin + indent, y_position, line)
                y_position -= line_height
        
        # Answer key on new page
        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, top_margin, "เฉลย / Answer Key")
        c.setFont("Helvetica", 12)
        y_position = top_margin - 1.5 * cm
        
        for i, answer in enumerate(answers, 1):
            if y_position < bottom_margin:
                c.showPage()
                y_position = top_margin - 1 * cm
            c.drawString(left_margin, y_position, f"{i}. {answer}")
            y_position -= 0.6 * cm
        
        c.save()
        buffer.seek(0)
        return buffer
