# worksheet_generator.py - Main worksheet generator class
import random
import io
from .ai_providers import create_ai_provider
from .generators import MathGenerator, ScienceGenerator, ThaiGenerator, EnglishGenerator
from .exporters import PDFExporter, DocxExporter

class WorksheetGenerator:
    """Main class for generating worksheets"""
    
    def __init__(self, ai_api_key=None, provider="Google Gemini"):
        self.provider = provider
        self.ai_api_key = ai_api_key
        self.ai = None
        
        # Initialize generators
        self.math_gen = MathGenerator()
        self.science_gen = ScienceGenerator()
        self.thai_gen = ThaiGenerator()
        self.english_gen = EnglishGenerator()
        self.pdf_exp = PDFExporter()
        self.docx_exp = DocxExporter()
        
        # Initialize AI provider
        if ai_api_key:
            self.ai = create_ai_provider(provider, ai_api_key)
    
    # ===== Math Methods =====
    def generate_questions(self, operation, num_questions, d_min, d_max):
        """Generate math questions"""
        return self.math_gen.generate_questions(operation, num_questions, d_min, d_max)
    
    # ===== PDF Export Methods =====
    def create_pdf(self, title, school_name, topic, questions, answers, qr_url=None, uploaded_logo=None):
        """Create PDF worksheet"""
        return self.pdf_exp.create_worksheet_pdf(title, school_name, topic, questions, answers, qr_url, uploaded_logo)
    
    def create_wordsearch_pdf(self, title, school_name, topic, grid, placed_words, answers=None, qr_link=None, uploaded_logo=None):
        """Create word search PDF"""
        return self.pdf_exp.create_wordsearch_pdf(title, school_name, topic, grid, placed_words, answers, qr_link, uploaded_logo)
    
    def create_tracing_pdf(self, title, school_name, topic, lines, uploaded_logo=None):
        """Create tracing PDF"""
        return self.pdf_exp.create_tracing_pdf(title, school_name, topic, lines, uploaded_logo)
    
    # ===== Word Export Methods =====
    def create_word_doc(self, title, school_name, topic, questions, answers):
        """Create Word document worksheet"""
        return self.docx_exp.create_worksheet_doc(title, school_name, topic, questions, answers)
    
    def create_wordsearch_doc(self, title, school_name, topic, grid, placed_words, answers=None):
        """Create word search Word document"""
        return self.docx_exp.create_wordsearch_doc(title, school_name, topic, grid, placed_words, answers)
    
    def create_tracing_doc(self, title, school_name, topic, lines):
        """Create tracing Word document"""
        return self.docx_exp.create_tracing_doc(title, school_name, topic, lines)
    
    # ===== Word Search =====
    def generate_word_search(self, words, grid_size=12):
        """Generate word search puzzle"""
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        placed_words = []
        
        def can_place(word, row, col, dr, dc):
            if len(word) > grid_size:
                return False
            for i, char in enumerate(word):
                new_row, new_col = row + i * dr, col + i * dc
                if (new_row < 0 or new_row >= grid_size or 
                    new_col < 0 or new_col >= grid_size or
                    (grid[new_row][new_col] != ' ' and grid[new_row][new_col] != char)):
                    return False
            return True
        
        def place_word(word, row, col, dr, dc):
            for i, char in enumerate(word):
                grid[row + i * dr][col + i * dc] = char
        
        for word in words:
            word = word.upper().strip()
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                attempts += 1
                directions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1), (-1, 1)]
                random.shuffle(directions)
                
                for dr, dc in directions:
                    row = random.randint(0, grid_size - 1)
                    col = random.randint(0, grid_size - 1)
                    
                    if can_place(word, row, col, dr, dc):
                        place_word(word, row, col, dr, dc)
                        placed_words.append(word)
                        placed = True
                        break
        
        # Fill empty spaces
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZกขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ"
        for row in range(grid_size):
            for col in range(grid_size):
                if grid[row][col] == ' ':
                    grid[row][col] = random.choice(letters)
        
        return grid, placed_words
    
    def generate_tracing_lines(self, text):
        """Generate lines for tracing"""
        return [line.strip() for line in text.split(',') if line.strip()]
    
    # ===== AI Generation Methods =====
    def _call_ai(self, prompt):
        """Call AI provider to generate content"""
        if self.ai:
            return self.ai.generate(prompt)
        return None
    
    def is_ai_working(self):
        """Check if AI provider is working"""
        if self.ai and hasattr(self.ai, 'test_connection'):
            return self.ai.test_connection()
        return False
    
    def _create_ai_prompt(self, subject, topic, grade, num_questions, exercise_type="mix"):
        """Create AI prompt for worksheet generation"""
        return f"""Create {num_questions} {subject} exercises for Thai students.
Grade: {grade}
Topic: {topic}
Exercise Type: {exercise_type}

Please provide questions and answers in Thai format.
Questions should be age-appropriate and educational.

Format:
Questions:
1. [question 1]
2. [question 2]
...

Answers:
1. [answer 1]
2. [answer 2]
..."""
    
    def generate_ai_worksheet(self, topic, grade, num_questions):
        """Generate worksheet using AI"""
        # Check if AI is working first
        if self.is_ai_working():
            prompt = self._create_ai_prompt("Math", topic, grade, num_questions)
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        # Fallback to template generation
        print("[INFO] AI not working, using template generation")
        return self.generate_questions("บวก (+)", num_questions, 1, 100)
    
    def generate_science_worksheet(self, topic, grade, num_questions):
        """Generate science worksheet using AI"""
        if self.is_ai_working():
            prompt = self._create_ai_prompt("Science", topic, grade, num_questions)
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        # Fallback to template generation
        print("[INFO] AI not working, using template generation")
        return [f"คำถามเกี่ยวกับ {topic}" for _ in range(num_questions)], [f"คำตอบสำหรับ {topic}" for _ in range(num_questions)]
    
    def generate_chemistry_worksheet(self, topic, grade, num_questions):
        """Generate chemistry worksheet using AI"""
        if self.is_ai_working():
            prompt = self._create_ai_prompt("Chemistry", topic, grade, num_questions)
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        print("[INFO] AI not working, using template generation")
        return [f"คำถามเคมีเกี่ยวกับ {topic}" for _ in range(num_questions)], [f"คำตอบ" for _ in range(num_questions)]
    
    def generate_physics_worksheet(self, topic, grade, num_questions):
        """Generate physics worksheet using AI"""
        if self.is_ai_working():
            prompt = self._create_ai_prompt("Physics", topic, grade, num_questions)
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        print("[INFO] AI not working, using template generation")
        return [f"คำถามฟิสิกส์เกี่ยวกับ {topic}" for _ in range(num_questions)], [f"คำตอบ" for _ in range(num_questions)]
    
    def generate_biology_worksheet(self, topic, grade, num_questions):
        """Generate biology worksheet using AI"""
        if self.is_ai_working():
            prompt = self._create_ai_prompt("Biology", topic, grade, num_questions)
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        print("[INFO] AI not working, using template generation")
        return [f"คำถามชีววิทยาเกี่ยวกับ {topic}" for _ in range(num_questions)], [f"คำตอบ" for _ in range(num_questions)]
    
    def generate_thai_worksheet(self, topic, grade, num_questions, exercise_type="mix"):
        """Generate Thai worksheet using AI"""
        if self.is_ai_working():
            prompt = self._create_ai_prompt("Thai Language", topic, grade, num_questions, exercise_type)
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        print("[INFO] AI not working, using template generation")
        return [f"แบบฝึกหัดภาษาไทยเกี่ยวกับ {topic}" for _ in range(num_questions)], [f"คำตอบ" for _ in range(num_questions)]
    
    def generate_english_worksheet(self, topic, grade, num_questions, exercise_type="mix"):
        """Generate English worksheet using AI"""
        if self.is_ai_working():
            prompt = f"""Create {num_questions} English {exercise_type} exercises for Thai students.
Grade: {grade}
Topic: {topic}

Format:
Questions:
1. [question in English]
2. [question in English]
...

Answers:
1. [answer in English]
2. [answer in English]
..."""
            
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        print("[INFO] AI not working, using template generation")
        return [f"{exercise_type} exercise about {topic}" for _ in range(num_questions)], [f"Answer" for _ in range(num_questions)]
    
    def generate_ai_word_problems(self, topic, grade, num_questions):
        """Generate AI word problems"""
        if self.is_ai_working():
            prompt = f"""Create {num_questions} math word problems for Thai students.
Grade: {grade}
Topic: {topic}

Make problems interesting and age-appropriate. Use Thai context.

Format:
Questions:
1. [word problem in Thai]
2. [word problem in Thai]
...

Answers:
1. [answer with explanation]
2. [answer with explanation]
..."""
            
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        print("[INFO] AI not working, using template generation")
        return [f"โจทย์ปัญหาเรื่อง {topic}" for _ in range(num_questions)], [f"คำตอบ" for _ in range(num_questions)]
    
    def generate_quiz_from_text(self, text, num_questions):
        """Generate quiz questions from uploaded text"""
        if self.is_ai_working():
            prompt = f"""Create {num_questions} quiz questions based on the following text.
Generate questions that test comprehension.

Text: {text[:2000]}

Format:
Questions:
1. [question]
2. [question]
...

Answers:
1. [answer]
2. [answer]
..."""
            
            result = self._call_ai(prompt)
            
            if result:
                questions, answers = self._parse_ai_response(result)
                if questions and answers:
                    return questions, answers
        
        print("[INFO] AI not working, using template generation")
        return ["คำถามจากบทความ"], ["คำตอบ"]
    
    def _parse_ai_response(self, response):
        """Parse AI response into questions and answers"""
        try:
            parts = response.split("Answers:")
            if len(parts) >= 2:
                questions = [q.strip() for q in parts[0].split("\n") if q.strip() and not q.lower().startswith("questions:")]
                answers = [a.strip() for a in parts[1].split("\n") if a.strip()]
                
                # Clean up question numbers
                questions = [q.split(".")[1].strip() if "." in q and q[0].isdigit() else q for q in questions]
                answers = [a.split(".")[1].strip() if "." in a and a[0].isdigit() else a for a in answers]
                
                return questions, answers
        except Exception as e:
            print(f"[!] Error parsing AI response: {e}")
        
        return None, None
    
    # ===== Utility Methods =====
    def get_math_topics(self, grade):
        """Get math topics for a grade"""
        return self.math_gen.get_topics(grade)
    
    def get_science_topics(self, grade, subject=None, term=None):
        """Get science topics"""
        return self.science_gen.get_topics(grade, subject, term)
    
    def get_thai_topics(self, grade, term=None):
        """Get Thai topics"""
        return self.thai_gen.get_topics(grade, term)
    
    def get_english_topics(self, grade, term=None):
        """Get English topics"""
        return self.english_gen.get_topics(grade, term)
