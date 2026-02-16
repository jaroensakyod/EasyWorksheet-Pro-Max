# math_generator.py - Math worksheet generation
import random

class MathGenerator:
    """Generator for math worksheets based on IPST curriculum"""
    
    def __init__(self):
        self.curriculum = self._load_curriculum()
    
    def _load_curriculum(self):
        return {
            "ป.1": {
                "จำนวนนับ 1 ถึง 5 และ 0": (1, 5),
                "จำนวนนับ 6 ถึง 9": (6, 9),
                "การบวกจำนวนสองจำนวนที่ผลบวกไม่เกิน 9": (1, 9),
                "การลบจำนวนสองจำนวนที่ตัวตั้งไม่เกิน 9": (1, 9),
                "การบวกลบระคน": (1, 9),
            },
            "ป.2": {
                "จำนวนนับ 10-100": (10, 100),
                "การบวกและการลบ": (10, 100),
                "การคูณ (แม่ 2-5)": (2, 5),
                "การหาร (แม่ 2-5)": (2, 5),
            },
            "ป.3": {
                "การบวกและการลบ (10,000)": (100, 1000),
                "การคูณ (แม่ 2-12)": (2, 12),
                "การหาร (แม่ 2-12)": (2, 12),
                "เศษส่วนเบื้องต้น": (1, 10),
            },
            "ป.4": {
                "การบวกลบคูณหารระคน": (100, 1000),
                "การคูณพหุคูณ": (1000, 10000),
                "การหารพหุคูณ": (1000, 10000),
                "เศษส่วนและทศนิยม": (1, 100),
            },
            "ป.5": {
                "การคูณและการหารทศนิยม": (1, 100),
                "เศษส่วนและการเปรียบเทียบ": (1, 100),
                "ร้อยละและสัดส่วน": (1, 100),
            },
            "ป.6": {
                "ทศนิยมและเศษส่วน": (1, 1000),
                "อัตราส่วน": (1, 100),
                "ร้อยละ": (1, 100),
                "ปริมาตรและความจุ": (1, 100),
            },
            "ม.1": {
                "จำนวนเต็ม": (-100, 100),
                "เลขยกกำลัง": (2, 12),
                "พหุนาม": (1, 50),
            },
            "ม.2": {
                "อัตราส่วน": (1, 100),
                "ร้อยละ": (1, 100),
                "กราฟ": (1, 50),
            },
            "ม.3": {
                "สมการเชิงเส้น": (1, 100),
                "อสมการ": (1, 50),
                "ความน่าจะเป็น": (1, 100),
            },
            "ม.4": {
                "จำนวนจริง": (1, 1000),
                "เลขยกกำลัง": (2, 20),
                "รากที่สอง": (1, 100),
            },
            "ม.5": {
                "ฟังก์ชัน": (1, 100),
                "อัตราส่วนตรีโกณ": (1, 90),
                "สถิติ": (1, 100),
            },
            "ม.6": {
                "แคลคูลัสเบื้องต้น": (1, 100),
                "ความน่าจะเป็น": (1, 100),
                "สถิติขั้นสูง": (1, 100),
            },
        }
    
    def generate_questions(self, operation, num_questions, d_min, d_max):
        """Generate math questions"""
        questions = []
        answers = []
        
        operations = {
            "บวก (+)": lambda a, b: (a, b, a + b),
            "ลบ (-)": lambda a, b: (max(a, b), min(a, b), max(a, b) - min(a, b)),
            "คูณ (×)": lambda a, b: (a, b, a * b),
            "หาร (÷)": lambda a, b: (a * b, b, a) if b != 0 else (a, 1, a),
        }
        
        op_func = operations.get(operation, operations["บวก (+)"])
        
        for _ in range(num_questions):
            a = random.randint(d_min, d_max)
            b = random.randint(d_min, d_max)
            q, a2, ans = op_func(a, b)
            questions.append(f"{q} {operation.replace('(', '').replace(')', '').replace('×', '×').replace('÷', '÷')} {a2} = ?")
            answers.append(str(ans))
        
        return questions, answers
    
    def get_topics(self, grade):
        """Get topics for a grade"""
        return self.curriculum.get(grade, {})
