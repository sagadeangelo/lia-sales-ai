from pydantic import BaseModel
from typing import List, Optional


class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str
    category: str
    difficulty: str
    explanation: Optional[str] = None


class QuizStartRequest(BaseModel):
    player_name: str
    category: str


class QuizAnswerRequest(BaseModel):
    question_id: int
    selected_answer: str


class QuizResult(BaseModel):
    correct: bool
    points: int
    correct_answer: str


class PlayerProfile(BaseModel):
    player_name: str
    total_points: int = 0
    streak_days: int = 0
    games_played: int = 0


class RankingEntry(BaseModel):
    player_name: str
    total_points: int