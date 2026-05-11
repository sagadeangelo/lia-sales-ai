from fastapi import APIRouter

from quiz.engine.quiz_manager import QuizManager
from quiz.engine.rewards_engine import RewardsEngine
from quiz.engine.streak_engine import StreakEngine
from quiz.engine.ranking_engine import RankingEngine

from quiz.models.quiz_models import (
    QuizStartRequest,
    QuizAnswerRequest
)

router = APIRouter(
    tags=["🎮 LIA Quiz Arena"]
)

print("🔥 QUIZ ROUTER CARGADO")

quiz_manager = QuizManager()
rewards_engine = RewardsEngine()
streak_engine = StreakEngine()
ranking_engine = RankingEngine()


@router.get("/quiz/question")
def get_question(category: str = None):

    question = quiz_manager.get_random_question(category)

    if not question:
        return {
            "success": False,
            "message": "No questions found"
        }

    return {
        "success": True,
        "question": question
    }


@router.post("/quiz/answer")
def submit_answer(payload: QuizAnswerRequest):

    result = quiz_manager.validate_answer(
        payload.question_id,
        payload.selected_answer
    )

    rewards = rewards_engine.calculate_rewards(result["points"])

    return {
        "success": True,
        "result": result,
        "rewards": rewards
    }


@router.get("/quiz/ranking")
def get_ranking():

    ranking = ranking_engine.get_ranking()

    return {
        "success": True,
        "ranking": ranking
    }