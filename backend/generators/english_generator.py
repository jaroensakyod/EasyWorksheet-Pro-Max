# english_generator.py - English language worksheet generation
import random

class EnglishGenerator:
    """Generator for English language worksheets"""
    
    def __init__(self):
        self.topics = self._load_topics()
    
    def _load_topics(self):
        return {
            # ===== ประถมศึกษา =====
            "ป.1": [
                ("1", "Alphabet (A-Z uppercase/lowercase)"),
                ("2", "Phonics (Aa-Zz sounds)"),
                ("3", "Numbers 1-10 (counting)"),
                ("4", "Colors (Red, blue, green, yellow, etc.)"),
                ("5", "Shapes (Circle, square, triangle, etc.)"),
                ("6", "Body Parts (Head, eyes, ears, nose, etc.)"),
                ("7", "Family (Mother, father, sister, brother)"),
                ("8", "Animals (Cat, dog, bird, fish, etc.)"),
            ],
            "ป.2": [
                ("1", "Numbers 11-100 (counting)"),
                ("2", "Days & Months (Monday-Sunday, Jan-Dec)"),
                ("3", "Time (O'clock, half past)"),
                ("4", "Food & Drinks (Rice, bread, water, milk)"),
                ("5", "Clothing (Shirt, pants, dress, shoes)"),
                ("6", "Weather (Hot, cold, rainy, sunny)"),
                ("7", "Places (School, home, market, hospital)"),
                ("8", "Greetings (Hello, goodbye, thank you)"),
            ],
            "ป.3": [
                ("1", "Present Simple (I am, you are, he/she is)"),
                ("2", "This-That-These-Those"),
                ("3", "Have-Has (possession)"),
                ("4", "Prepositions (In, on, under, behind)"),
                ("5", "WH-Questions (What, Where, When, Why, Who)"),
                ("6", "Daily Routines (Wake up, eat breakfast)"),
                ("7", "Occupations (Doctor, teacher, farmer)"),
                ("8", "Adjectives (Big, small, tall, short)"),
            ],
            "ป.4": [
                ("1", "Past Simple (was/were, regular verbs)"),
                ("2", "Irregular Verbs (went, ate, drank, saw)"),
                ("3", "Object Pronouns (Me, him, her, us, them)"),
                ("4", "There is-There are"),
                ("5", "Commands (Open the door, close)"),
                ("6", "Descriptions (Describing people)"),
                ("7", "School Subjects (Math, English, Science)"),
                ("8", "Time Expressions"),
            ],
            "ป.5": [
                ("1", "Future Will-Going to"),
                ("2", "Present Continuous"),
                ("3", "Can-Could (ability, permission)"),
                ("4", "Some-Any"),
                ("5", "Telling Time (Quarter past, quarter to)"),
                ("6", "Giving Directions (Turn left, right)"),
                ("7", "Invitations (Would you like..., Let's)"),
                ("8", "Letter Writing (Formal, informal)"),
            ],
            "ป.6": [
                ("1", "Tenses Review (Present, Past, Future)"),
                ("2", "Modal Verbs (Must, should, have to)"),
                ("3", "Passive Voice (is/are + verb3)"),
                ("4", "If Clauses (Conditionals type 1)"),
                ("5", "Reported Speech (Said, told, asked)"),
                ("6", "Conjunctions (And, but, or, because)"),
                ("7", "Reading Comprehension"),
                ("8", "Paragraph Writing"),
            ],
            # ===== มัธยมต้น =====
            "ม.1": {
                "เทอม 1": [
                    ("1", "Present Perfect (Have/has + verb3)"),
                    ("2", "Since-For (time expressions)"),
                    ("3", "Tag Questions"),
                    ("4", "Relative Clauses (Who, which, that)"),
                    ("5", "Gerunds & Infinitives"),
                    ("6", "Making Suggestions (Let's, Why don't)"),
                    ("7", "Phone Conversations"),
                    ("8", "Shopping & Money"),
                ],
                "เทอม 2": [
                    ("1", "Past Continuous"),
                    ("2", "Future Continuous"),
                    ("3", "Conditionals Type 2"),
                    ("4", "Reported Questions"),
                    ("5", "Quantifiers (Much, many, a few)"),
                    ("6", "Comparison (Adjectives, adverbs)"),
                    ("7", "Wish Sentences"),
                    ("8", "Email Writing"),
                ],
            },
            "ม.2": {
                "เทอม 1": [
                    ("1", "Past Continuous"),
                    ("2", "Future Continuous"),
                    ("3", "Conditionals Type 2"),
                    ("4", "Reported Questions"),
                    ("5", "Quantifiers"),
                    ("6", "Comparison"),
                    ("7", "Wish Sentences"),
                    ("8", "Email Writing"),
                ],
                "เทอม 2": [
                    ("1", "Conditionals All Types"),
                    ("2", "Passive Voice (All tenses)"),
                    ("3", "Reported Speech (All)"),
                    ("4", "Gerunds & Infinitives"),
                    ("5", "Modal Perfects"),
                    ("6", "Articles (A, an, the)"),
                    ("7", "Essay Writing"),
                    ("8", "O-NET Preparation"),
                ],
            },
            "ม.3": {
                "เทอม 1": [
                    ("1", "Conditionals All Types"),
                    ("2", "Passive Voice (All tenses)"),
                    ("3", "Reported Speech (All)"),
                    ("4", "Gerunds & Infinitives"),
                    ("5", "Modal Perfects"),
                    ("6", "Articles"),
                    ("7", "Essay Writing"),
                    ("8", "O-NET Preparation"),
                ],
                "เทอม 2": [
                    ("1", "Narrative Tenses"),
                    ("2", "Future Perfect"),
                    ("3", "Mixed Conditionals"),
                    ("4", "Wish-Remorse"),
                    ("5", "Linking Words"),
                    ("6", "Paragraph Development"),
                    ("7", "Speaking: Opinions"),
                    ("8", "Vocabulary 1500"),
                ],
            },
            # ===== มัธยมปลาย =====
            "ม.4": {
                "เทอม 1": [
                    ("1", "Narrative Tenses"),
                    ("2", "Future Perfect"),
                    ("3", "Mixed Conditionals"),
                    ("4", "Wish-Remorse"),
                    ("5", "Linking Words"),
                    ("6", "Paragraph Development"),
                    ("7", "Speaking: Opinions"),
                    ("8", "Vocabulary 1500"),
                ],
                "เทอม 2": [
                    ("1", "Mixed Tenses Review"),
                    ("2", "Modal Verbs Review"),
                    ("3", "Participle Clauses"),
                    ("4", "Passive Voice Review"),
                    ("5", "Essay Types"),
                    ("6", "Speaking: Debating"),
                    ("7", "Listening Skills"),
                    ("8", "Vocabulary 2000"),
                ],
            },
            "ม.5": {
                "เทอม 1": [
                    ("1", "Mixed Tenses Review"),
                    ("2", "Modal Verbs Review"),
                    ("3", "Participle Clauses"),
                    ("4", "Passive Voice Review"),
                    ("5", "Essay Types"),
                    ("6", "Speaking: Debating"),
                    ("7", "Listening Skills"),
                    ("8", "Vocabulary 2000"),
                ],
                "เทอม 2": [
                    ("1", "Advanced Grammar"),
                    ("2", "Academic Writing"),
                    ("3", "Critical Reading"),
                    ("4", "Presentation Skills"),
                    ("5", "Test Preparation"),
                    ("6", "Career English"),
                    ("7", "Global Issues"),
                    ("8", "Literature"),
                ],
            },
            "ม.6": {
                "เทอม 1": [
                    ("1", "Advanced Grammar"),
                    ("2", "Academic Writing"),
                    ("3", "Critical Reading"),
                    ("4", "Presentation Skills"),
                    ("5", "Test Preparation"),
                    ("6", "Career English"),
                    ("7", "Global Issues"),
                    ("8", "Literature"),
                ],
                "เทอม 2": [
                    ("1", "University Entrance Preparation"),
                    ("2", "Advanced Writing Skills"),
                    ("3", "Professional English"),
                    ("4", "Global Communication"),
                    ("5", "Research Skills"),
                    ("6", "Public Speaking"),
                    ("7", "Interview Skills"),
                    ("8", "Final Review"),
                ],
            },
        }
    
    def get_topics(self, grade, term=None):
        """Get topics based on grade and optional term"""
        if grade in ["ป.1", "ป.2", "ป.3", "ป.4", "ป.5", "ป.6"]:
            return self.topics.get(grade, [])
        
        if grade in ["ม.1", "ม.2", "ม.3", "ม.4", "ม.5", "ม.6"]:
            grade_data = self.topics.get(grade, {})
            if term:
                return grade_data.get(term, [])
            return grade_data
        
        return []
