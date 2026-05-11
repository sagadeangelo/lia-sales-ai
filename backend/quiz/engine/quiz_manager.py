import json
import random

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

QUESTIONS_PATH = BASE_DIR / "data" / "questions.json"

print("📂 QUESTIONS PATH:")
print(QUESTIONS_PATH)


class QuizManager:

    def __init__(self):

        self.questions = self.load_questions()

    def load_questions(self):

        try:

            with open(QUESTIONS_PATH, "r", encoding="utf-8") as file:

                data = json.load(file)

                print(f"✅ QUESTIONS LOADED: {len(data)}")

                return data

        except Exception as e:

            print(f"❌ Error loading questions: {e}")

            return []

    def get_random_question(self, category=None):

        filtered_questions = self.questions

        if category:

            filtered_questions = [
                q for q in self.questions
                if q["category"].lower() == category.lower()
            ]

        if not filtered_questions:
            return None

        return random.choice(filtered_questions)

    def validate_answer(self, question_id, selected_answer):

        question = next(
            (q for q in self.questions if q["id"] == question_id),
            None
        )

        if not question:

            return {
                "correct": False,
                "points": 0,
                "correct_answer": "Question not found"
            }

        is_correct = (
            question["correct_answer"].strip().lower()
            == selected_answer.strip().lower()
        )

        return {
            "correct": is_correct,
            "points": 10 if is_correct else 0,
            "correct_answer": question["correct_answer"]
        }