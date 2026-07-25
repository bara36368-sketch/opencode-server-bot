"""
Education & Games — v1.0
OpenCode Bot Feature

Telegram bot features for education and entertainment:
- Quiz system with scoring and leaderboards
- Flashcard system (Spaced Repetition)
- Language learning
- Trivia games
- Word games (Wordle, Hangman)
- Math challenges
- Code challenges
- Study group management
- Progress tracking
"""

import json
import os
import time
import random
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EDUCATION_DATA_FILE = os.path.join(BASE_DIR, "education_data.json")
QUIZZES_FILE = os.path.join(BASE_DIR, "education_quizzes.json")
FLASHCARDS_FILE = os.path.join(BASE_DIR, "education_flashcards.json")
GAMES_FILE = os.path.join(BASE_DIR, "education_games.json")


class GameType(Enum):
    QUIZ = "quiz"
    FLASHCARDS = "flashcards"
    TRIVIA = "trivia"
    WORDLE = "wordle"
    HANGMAN = "hangman"
    MATH = "math"
    CODE_CHALLENGE = "code_challenge"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class QuizQuestion:
    question: str
    options: List[str]
    correct_index: int
    explanation: str = ""
    difficulty: Difficulty = Difficulty.MEDIUM
    category: str = "general"

    def to_dict(self) -> Dict:
        return {
            "question": self.question,
            "options": self.options,
            "correct_index": self.correct_index,
            "explanation": self.explanation,
            "difficulty": self.difficulty.value,
            "category": self.category
        }


@dataclass
class Quiz:
    quiz_id: str
    title: str
    questions: List[QuizQuestion]
    created_by: str = ""
    created_at: float = 0.0
    plays: int = 0

    def to_dict(self) -> Dict:
        return {
            "quiz_id": self.quiz_id,
            "title": self.title,
            "questions": [q.to_dict() for q in self.questions],
            "created_by": self.created_by,
            "created_at": self.created_at,
            "plays": self.plays
        }


@dataclass
class Flashcard:
    card_id: str
    front: str
    back: str
    category: str = "general"
    difficulty: Difficulty = Difficulty.MEDIUM
    next_review: float = 0.0
    interval: float = 3600.0
    ease_factor: float = 2.5
    reviews: int = 0
    last_review: float = 0.0
    correct_streak: int = 0

    def to_dict(self) -> Dict:
        return {
            "card_id": self.card_id,
            "front": self.front,
            "back": self.back,
            "category": self.category,
            "difficulty": self.difficulty.value,
            "next_review": self.next_review,
            "interval": self.interval,
            "ease_factor": self.ease_factor,
            "reviews": self.reviews,
            "last_review": self.last_review,
            "correct_streak": self.correct_streak
        }


@dataclass
class WordleGame:
    game_id: str
    word: str
    guesses: List[str] = field(default_factory=list)
    max_guesses: int = 6
    status: str = "playing"
    started_at: float = 0.0
    hint_used: bool = False

    def to_dict(self) -> Dict:
        return {
            "game_id": self.game_id,
            "word": self.word,
            "guesses": self.guesses,
            "max_guesses": self.max_guesses,
            "status": self.status,
            "started_at": self.started_at,
            "hint_used": self.hint_used
        }


@dataclass
class HangmanGame:
    game_id: str
    word: str
    category: str = ""
    guessed_letters: List[str] = field(default_factory=list)
    wrong_guesses: int = 0
    max_wrong: int = 6
    status: str = "playing"
    started_at: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "game_id": self.game_id,
            "word": self.word,
            "category": self.category,
            "guessed_letters": self.guessed_letters,
            "wrong_guesses": self.wrong_guesses,
            "max_wrong": self.max_wrong,
            "status": self.status,
            "started_at": self.started_at
        }


@dataclass
class MathProblem:
    problem_id: str
    expression: str
    answer: float
    difficulty: Difficulty = Difficulty.MEDIUM
    topic: str = "arithmetic"

    def to_dict(self) -> Dict:
        return {
            "problem_id": self.problem_id,
            "expression": self.expression,
            "answer": self.answer,
            "difficulty": self.difficulty.value,
            "topic": self.topic
        }


@dataclass
class CodeChallenge:
    challenge_id: str
    title: str
    description: str
    test_cases: List[Dict]
    difficulty: Difficulty = Difficulty.MEDIUM
    language: str = "python"
    hints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "challenge_id": self.challenge_id,
            "title": self.title,
            "description": self.description,
            "test_cases": self.test_cases,
            "difficulty": self.difficulty.value,
            "language": self.language,
            "hints": self.hints
        }


@dataclass
class UserProfile:
    user_id: str
    username: str = ""
    xp: int = 0
    level: int = 1
    streak: int = 0
    last_active: float = 0.0
    quizzes_taken: int = 0
    quizzes_correct: int = 0
    flashcards_reviewed: int = 0
    flashcards_correct: int = 0
    games_played: int = 0
    wordle_wins: int = 0
    wordle_streak: int = 0
    math_solved: int = 0
    code_solved: int = 0
    achievements: List[str] = field(default_factory=list)
    total_xp_history: List[Dict] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    def add_xp(self, amount: int, reason: str = ""):
        self.xp += amount
        self.level = 1 + self.xp // 100
        self.last_active = time.time()
        self.total_xp_history.append({
            "amount": amount,
            "reason": reason,
            "time": time.time()
        })

    def check_achievements(self) -> List[str]:
        new = []
        checks = {
            "first_quiz": self.quizzes_taken >= 1,
            "quiz_master": self.quizzes_correct >= 50,
            "flashcard_fan": self.flashcards_reviewed >= 100,
            "wordle_champion": self.wordle_wins >= 10,
            "math_wizard": self.math_solved >= 25,
            "code_ninja": self.code_solved >= 10,
            "level_10": self.level >= 10,
            "streak_7": self.streak >= 7,
        }
        for name, condition in checks.items():
            if condition and name not in self.achievements:
                self.achievements.append(name)
                new.append(name)
        return new


WORDLE_WORDS = [
    "brave", "cyber", "dream", "earth", "flame", "ghost", "happy",
    "ivory", "jolly", "karma", "lemon", "magic", "noble", "ocean",
    "pixel", "quest", "royal", "solar", "tiger", "ultra", "vivid",
    "water", "xenon", "youth", "zebra", "alpha", "blaze", "coral",
    "delta", "ember", "frost", "glyph", "hyper", "input", "jetty",
    "kayak", "lunar", "maple", "nerve", "orbit", "prime", "quirk",
    "robin", "snake", "trace", "unity", "viper", "wagon", "xerox",
    "yield", "zonal"
]

HANGMAN_WORDS = {
    "animals": ["elephant", "giraffe", "dolphin", "penguin", "octopus",
                "cheetah", "flamingo", "kangaroo", "butterfly", "chameleon"],
    "countries": ["australia", "brazil", "canada", "denmark", "ethiopia",
                  "finland", "germany", "hungary", "ireland", "jamaica"],
    "technology": ["algorithm", "bluetooth", "compiler", "database",
                   "ethernet", "firmware", "hardware", "internet",
                   "javascript", "keyboard"],
    "science": ["biology", "chemistry", "electron", "friction",
                "geometry", "hydrogen", "molecule", "neutron",
                "organism", "photon"],
    "food": ["avocado", "broccoli", "chocolate", "dumpling", "espresso",
             "focaccia", "guacamole", "hazelnut", "jambalaya", "kimchi"]
}

MATH_PROBLEMS = {
    Difficulty.EASY: [
        ("addition", lambda: (a := random.randint(1,50), b := random.randint(1,50)) and (f"{a} + {b}", a + b)),
        ("subtraction", lambda: (a := random.randint(10,100), b := random.randint(1,a)) and (f"{a} - {b}", a - b)),
        ("multiplication", lambda: (a := random.randint(2,12), b := random.randint(2,12)) and (f"{a} × {b}", a * b)),
    ],
    Difficulty.MEDIUM: [
        ("multiplication", lambda: (a := random.randint(10,50), b := random.randint(2,15)) and (f"{a} × {b}", a * b)),
        ("division", lambda: (b := random.randint(2,12), a := b * random.randint(2,20)) and (f"{a} ÷ {b}", a // b)),
        ("mixed", lambda: (a := random.randint(5,30), b := random.randint(2,10), c := random.randint(1,20)) and (f"{a} × {b} + {c}", a * b + c)),
    ],
    Difficulty.HARD: [
        ("algebra", lambda: (a := random.randint(2,10), b := random.randint(1,20)) and (f"If x + {a} = {b+a}, what is x?", b)),
        ("geometry", lambda: (r := random.randint(2,10)) and (f"Area of circle with radius {r}? (round to 1 decimal)", round(3.14159 * r * r, 1))),
        ("percentages", lambda: (p := random.randint(10,50), v := random.randint(100,1000)) and (f"{p}% of {v}?", round(v * p / 100, 1))),
    ]
}

CODE_CHALLENGES = [
    CodeChallenge(
        challenge_id="cc_001",
        title="FizzBuzz",
        description="Print numbers 1-100. For multiples of 3 print 'Fizz', multiples of 5 print 'Buzz', both print 'FizzBuzz'.",
        test_cases=[
            {"input": "15", "output": "1,2,Fizz,4,Buzz,Fizz,7,8,Fizz,Buzz,11,Fizz,13,14,FizzBuzz"},
        ],
        difficulty=Difficulty.EASY,
        language="python",
        hints=["Use modulo operator (%)", "Check divisibility by 15 for FizzBuzz"]
    ),
    CodeChallenge(
        challenge_id="cc_002",
        title="Palindrome Check",
        description="Check if a string is a palindrome (reads same forwards and backwards).",
        test_cases=[
            {"input": "racecar", "output": "True"},
            {"input": "hello", "output": "False"},
        ],
        difficulty=Difficulty.EASY,
        language="python",
        hints=["Compare string with its reverse", "s == s[::-1]"]
    ),
    CodeChallenge(
        challenge_id="cc_003",
        title="Fibonacci",
        description="Return the nth Fibonacci number. F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).",
        test_cases=[
            {"input": "10", "output": "55"},
            {"input": "5", "output": "5"},
        ],
        difficulty=Difficulty.MEDIUM,
        language="python",
        hints=["Use iteration or recursion", "Memoization helps for large n"]
    ),
    CodeChallenge(
        challenge_id="cc_004",
        title="Prime Checker",
        description="Check if a number is prime.",
        test_cases=[
            {"input": "17", "output": "True"},
            {"input": "4", "output": "False"},
        ],
        difficulty=Difficulty.MEDIUM,
        language="python",
        hints=["Check divisibility up to sqrt(n)", "2 is the only even prime"]
    ),
    CodeChallenge(
        challenge_id="cc_005",
        title="Anagram Checker",
        description="Check if two strings are anagrams of each other.",
        test_cases=[
            {"input": "listen silent", "output": "True"},
            {"input": "hello world", "output": "False"},
        ],
        difficulty=Difficulty.MEDIUM,
        language="python",
        hints=["Sort both strings and compare", "Consider case and spaces"]
    ),
]


class EducationManager:
    def __init__(self):
        self.profiles: Dict[str, UserProfile] = {}
        self.quizzes: Dict[str, Quiz] = {}
        self.flashcards: Dict[str, List[Flashcard]] = {}
        self.active_wordle: Dict[str, WordleGame] = {}
        self.active_hangman: Dict[str, HangmanGame] = {}
        self.active_quiz: Dict[str, Tuple[Quiz, int, int]] = {}
        self._load_data()

    def _load_data(self):
        for path, attr, default in [
            (EDUCATION_DATA_FILE, "profiles", {}),
            (QUIZZES_FILE, "quizzes", {}),
            (FLASHCARDS_FILE, "flashcards", {}),
        ]:
            try:
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as f:
                        data = json.load(f)
                    setattr(self, attr, data if isinstance(data, type(default)) else default)
            except Exception:
                pass

        if isinstance(self.profiles, dict):
            restored = {}
            for uid, udata in self.profiles.items():
                try:
                    restored[uid] = UserProfile(**{
                        k: v for k, v in udata.items()
                        if k in UserProfile.__dataclass_fields__
                    })
                except Exception:
                    pass
            self.profiles = restored

        if isinstance(self.flashcards, dict):
            restored_cards = {}
            for uid, cards in self.flashcards.items():
                restored_cards[uid] = [
                    Flashcard(**{k: v for k, v in c.items()
                                if k in Flashcard.__dataclass_fields__})
                    for c in cards if isinstance(c, dict)
                ]
            self.flashcards = restored_cards

    def _save_data(self):
        try:
            with open(EDUCATION_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({uid: p.to_dict() for uid, p in self.profiles.items()}, f, indent=2)
            with open(FLASHCARDS_FILE, "w", encoding="utf-8") as f:
                json.dump({uid: [c.to_dict() for c in cards]
                           for uid, cards in self.flashcards.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save education data: {e}")

    def get_profile(self, user_id: str, username: str = "") -> UserProfile:
        if user_id not in self.profiles:
            self.profiles[user_id] = UserProfile(
                user_id=user_id, username=username, last_active=time.time()
            )
        return self.profiles[user_id]

    def start_quiz(self, user_id: str, quiz_id: str = None) -> Tuple[Optional[Quiz], str]:
        quiz = None
        if quiz_id and quiz_id in self.quizzes:
            quiz = self.quizzes[quiz_id]
        elif self.quizzes:
            quiz = random.choice(list(self.quizzes.values()))
        else:
            quiz = Quiz(
                quiz_id="default",
                title="General Knowledge",
                questions=[
                    QuizQuestion("What is the capital of France?",
                                ["London", "Berlin", "Paris", "Madrid"], 2,
                                "Paris is the capital of France."),
                    QuizQuestion("How many planets in our solar system?",
                                ["7", "8", "9", "10"], 1,
                                "8 planets: Mercury through Neptune."),
                    QuizQuestion("What is the speed of light?",
                                ["300,000 km/s", "150,000 km/s", "500,000 km/s", "1,000,000 km/s"],
                                0, "Light travels at ~299,792 km/s."),
                    QuizQuestion("What is the largest ocean?",
                                ["Atlantic", "Indian", "Arctic", "Pacific"], 3,
                                "The Pacific Ocean covers ~63 million sq mi."),
                    QuizQuestion("Who painted the Mona Lisa?",
                                ["Van Gogh", "Picasso", "Da Vinci", "Monet"], 2,
                                "Leonardo da Vinci painted it ~1503-1519."),
                ]
            )
        self.active_quiz[user_id] = (quiz, 0, 0)
        quiz.plays += 1
        return quiz, quiz.questions[0].question if quiz.questions else "No questions."

    def answer_quiz(self, user_id: str, answer_index: int) -> Tuple[bool, str, bool]:
        if user_id not in self.active_quiz:
            return False, "No active quiz. Use /edu quiz to start.", False
        quiz, q_idx, score = self.active_quiz[user_id]
        if q_idx >= len(quiz.questions):
            return False, "Quiz already finished.", True
        q = quiz.questions[q_idx]
        correct = answer_index == q.correct_index
        if correct:
            score += 1
        feedback = f"{'✅ Correct!' if correct else '❌ Wrong!'} {q.explanation}"
        self.active_quiz[user_id] = (quiz, q_idx + 1, score)
        profile = self.get_profile(user_id)
        profile.quizzes_taken += 1
        if correct:
            profile.quizzes_correct += 1
            profile.add_xp(10, "quiz_correct")
        done = q_idx + 1 >= len(quiz.questions)
        if done:
            feedback += f"\n\n🏆 Final Score: {score}/{len(quiz.questions)}"
            profile.games_played += 1
            if score == len(quiz.questions):
                profile.add_xp(50, "perfect_quiz")
                feedback += "\n🎉 Perfect score! +50 XP"
            elif score >= len(quiz.questions) * 0.7:
                profile.add_xp(25, "good_quiz")
                feedback += "\n⭐ Great job! +25 XP"
            new_achievements = profile.check_achievements()
            for ach in new_achievements:
                feedback += f"\n🏅 Achievement unlocked: {ach}"
            del self.active_quiz[user_id]
        self._save_data()
        return correct, feedback, done

    def add_flashcards(self, user_id: str, cards: List[Tuple[str, str, str]]) -> int:
        if user_id not in self.flashcards:
            self.flashcards[user_id] = []
        count = 0
        for front, back, category in cards:
            card = Flashcard(
                card_id=f"fc_{int(time.time()*1000) % 100000}_{count}",
                front=front, back=back, category=category,
                next_review=time.time()
            )
            self.flashcards[user_id].append(card)
            count += 1
        self._save_data()
        return count

    def get_review_cards(self, user_id: str, limit: int = 5) -> List[Flashcard]:
        if user_id not in self.flashcards:
            return []
        now = time.time()
        due = [c for c in self.flashcards[user_id] if c.next_review <= now]
        due.sort(key=lambda c: c.next_review)
        return due[:limit]

    def review_flashcard(self, user_id: str, card_id: str, quality: int) -> Optional[str]:
        if user_id not in self.flashcards:
            return None
        for card in self.flashcards[user_id]:
            if card.card_id == card_id:
                card.reviews += 1
                card.last_review = time.time()
                profile = self.get_profile(user_id)
                profile.flashcards_reviewed += 1
                if quality >= 3:
                    card.correct_streak += 1
                    card.ease_factor = min(3.0, card.ease_factor + 0.1)
                    card.interval *= card.ease_factor
                    profile.flashcards_correct += 1
                    profile.add_xp(5, "flashcard_correct")
                else:
                    card.correct_streak = 0
                    card.ease_factor = max(1.3, card.ease_factor - 0.2)
                    card.interval = 3600.0
                    profile.add_xp(2, "flashcard_review")
                card.next_review = time.time() + card.interval
                self._save_data()
                return card.back
        return None

    def start_wordle(self, user_id: str) -> WordleGame:
        word = random.choice(WORDLE_WORDS)
        game = WordleGame(
            game_id=f"wordle_{user_id}",
            word=word, started_at=time.time()
        )
        self.active_wordle[user_id] = game
        return game

    def guess_wordle(self, user_id: str, guess: str) -> Tuple[Optional[str], str, bool]:
        if user_id not in self.active_wordle:
            return None, "No active Wordle. Use /edu wordle to start.", False
        game = self.active_wordle[user_id]
        guess = guess.lower().strip()
        if len(guess) != len(game.word):
            return None, f"Guess must be {len(game.word)} letters.", False
        game.guesses.append(guess)
        if guess == game.word:
            game.status = "won"
            profile = self.get_profile(user_id)
            profile.wordle_wins += 1
            profile.wordle_streak += 1
            profile.games_played += 1
            xp = max(5, 60 - len(game.guesses) * 10)
            profile.add_xp(xp, "wordle_win")
            del self.active_wordle[user_id]
            self._save_data()
            return "🟩🟩🟩🟩🟩", f"🎉 You got it in {len(game.guesses)}! +{xp} XP", True
        if len(game.guesses) >= game.max_guesses:
            game.status = "lost"
            profile = self.get_profile(user_id)
            profile.wordle_streak = 0
            profile.games_played += 1
            del self.active_wordle[user_id]
            self._save_data()
            return None, f"💀 The word was: **{game.word.upper()}**", True
        result = []
        for i, (g, w) in enumerate(zip(guess, game.word)):
            if g == w:
                result.append("🟩")
            elif g in game.word:
                result.append("🟨")
            else:
                result.append("⬜")
        feedback = "".join(result)
        remaining = game.max_guesses - len(game.guesses)
        self._save_data()
        return feedback, f"{feedback}\n({remaining} guesses left)", False

    def start_hangman(self, user_id: str, category: str = None) -> HangmanGame:
        if category and category in HANGMAN_WORDS:
            word = random.choice(HANGMAN_WORDS[category])
            cat = category
        else:
            cat = random.choice(list(HANGMAN_WORDS.keys()))
            word = random.choice(HANGMAN_WORDS[cat])
        game = HangmanGame(
            game_id=f"hangman_{user_id}",
            word=word, category=cat, started_at=time.time()
        )
        self.active_hangman[user_id] = game
        return game

    def guess_hangman(self, user_id: str, letter: str) -> Tuple[Optional[str], str, bool]:
        if user_id not in self.active_hangman:
            return None, "No active Hangman. Use /edu hangman to start.", False
        game = self.active_hangman[user_id]
        letter = letter.lower().strip()
        if len(letter) != 1 or not letter.isalpha():
            return None, "Please guess a single letter.", False
        if letter in game.guessed_letters:
            return None, f"Already guessed '{letter}'. Try another.", False
        game.guessed_letters.append(letter)
        if letter in game.word:
            display = " ".join(
                c if c in game.guessed_letters else "_"
                for c in game.word
            )
            won = all(c in game.guessed_letters for c in game.word)
            if won:
                game.status = "won"
                profile = self.get_profile(user_id)
                profile.games_played += 1
                xp = max(5, 50 - game.wrong_guesses * 5)
                profile.add_xp(xp, "hangman_win")
                del self.active_hangman[user_id]
                self._save_data()
                return display, f"🎉 You got it! The word was **{game.word.upper()}** +{xp} XP", True
            self._save_data()
            return display, f"✅ '{letter}' is in the word!\n{display}\nCategory: {game.category}", False
        else:
            game.wrong_guesses += 1
            remaining = game.max_wrong - game.wrong_guesses
            if remaining <= 0:
                game.status = "lost"
                profile = self.get_profile(user_id)
                profile.games_played += 1
                del self.active_hangman[user_id]
                self._save_data()
                return None, f"💀 Game over! The word was: **{game.word.upper()}**", True
            display = " ".join(
                c if c in game.guessed_letters else "_"
                for c in game.word
            )
            self._save_data()
            return display, f"❌ '{letter}' is not in the word. ({remaining} wrong guesses left)\n{display}", False

    def generate_math(self, difficulty: str = "medium") -> MathProblem:
        diff = Difficulty(difficulty)
        topic_func = random.choice(MATH_PROBLEMS.get(diff, MATH_PROBLEMS[Difficulty.MEDIUM]))
        topic, func = topic_func
        expression, answer = func()
        return MathProblem(
            problem_id=f"math_{int(time.time()*1000) % 100000}",
            expression=expression, answer=answer,
            difficulty=diff, topic=topic
        )

    def check_math(self, user_answer: float, correct_answer: float) -> bool:
        return abs(user_answer - correct_answer) < 0.1

    def get_code_challenge(self, difficulty: str = None) -> Optional[CodeChallenge]:
        if difficulty:
            filtered = [c for c in CODE_CHALLENGES
                       if c.difficulty.value == difficulty]
            return random.choice(filtered) if filtered else random.choice(CODE_CHALLENGES)
        return random.choice(CODE_CHALLENGES)

    def get_leaderboard(self, limit: int = 10) -> List[UserProfile]:
        profiles = sorted(
            self.profiles.values(),
            key=lambda p: p.xp, reverse=True
        )
        return profiles[:limit]

    def get_stats(self, user_id: str) -> Dict:
        profile = self.get_profile(user_id)
        return {
            "xp": profile.xp,
            "level": profile.level,
            "streak": profile.streak,
            "quizzes_taken": profile.quizzes_taken,
            "quizzes_correct": profile.quizzes_correct,
            "quiz_accuracy": (profile.quizzes_correct / max(1, profile.quizzes_taken) * 100),
            "flashcards_reviewed": profile.flashcards_reviewed,
            "flashcards_correct": profile.flashcards_correct,
            "wordle_wins": profile.wordle_wins,
            "wordle_streak": profile.wordle_streak,
            "math_solved": profile.math_solved,
            "code_solved": profile.code_solved,
            "achievements": profile.achievements,
            "total_games": profile.games_played
        }


_edu_manager = None

def get_education_manager() -> EducationManager:
    global _edu_manager
    if _edu_manager is None:
        _edu_manager = EducationManager()
    return _edu_manager


def build_education_commands() -> str:
    return """
📚 Education & Games Commands:

🧠 QUIZ:
/edu quiz — Start a random quiz
/edu quiz answer <0-3> — Answer current question

🃏 FLASHCARDS:
/edu addcards <front>|<back>|<category> — Add cards (newline separated)
/edu review — Review due cards
/edu review <good/bad> — Rate card

🔤 WORDLE:
/edu wordle — Start Wordle game
/edu guess <word> — Guess a word

🎭 HANGMAN:
/edu hangman [category] — Start Hangman
/edu hguess <letter> — Guess a letter

🔢 MATH:
/edu math [easy/medium/hard] — Generate math problem
/edu mathanswer <number> — Answer math problem

💻 CODE:
/edu code [difficulty] — Get code challenge

🏆 LEADERBOARD:
/edu top — Top 10 users
/edu stats — Your stats
/edu achievements — Your achievements
"""


def handle_education_command(update, context) -> str:
    if not context.args:
        return build_education_commands()

    subcmd = context.args[0].lower()
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or ""
    mgr = get_education_manager()

    if subcmd == "quiz":
        if len(context.args) > 1 and context.args[1] == "answer":
            if len(context.args) < 3:
                return "Usage: /edu quiz answer <0-3>"
            try:
                ans = int(context.args[2])
            except ValueError:
                return "Answer must be a number 0-3."
            correct, feedback, done = mgr.answer_quiz(user_id, ans)
            if done:
                return feedback
            return feedback + "\n\nReply with /edu quiz answer <0-3>"
        quiz, first_q = mgr.start_quiz(user_id)
        lines = [f"📝 **{quiz.title}**\n"]
        lines.append(f"Q1: {first_q}")
        for i, opt in enumerate(quiz.questions[0].options):
            lines.append(f"  {i}. {opt}")
        lines.append(f"\nAnswer: /edu quiz answer <0-3>")
        return "\n".join(lines)

    elif subcmd == "addcards":
        text = " ".join(context.args[1:])
        entries = [line.split("|") for line in text.split("\n") if "|" in line]
        if not entries:
            return "Format: /edu addcards front|back|category (one per line)"
        cards = [(e[0].strip(), e[1].strip(), e[2].strip() if len(e) > 2 else "general")
                 for e in entries if len(e) >= 2]
        count = mgr.add_flashcards(user_id, cards)
        return f"✅ Added {count} flashcards!"

    elif subcmd == "review":
        cards = mgr.get_review_cards(user_id)
        if not cards:
            return "No cards due for review! 🎉"
        if len(context.args) > 1:
            quality = 5 if context.args[1] in ("good", "yes", "y", "5") else 2
            card_id = context.args[1] if len(context.args) > 2 else cards[0].card_id
            back = mgr.review_flashcard(user_id, card_id, quality)
            if back:
                return f"**Answer:** {back}\n\nRate: /edu review good or /edu review bad"
            return "Card not found."
        card = cards[0]
        return (f"🃏 **Flashcard** ({card.category})\n\n"
                f"**Q:** {card.front}\n\n"
                f"Reply: /edu review good or /edu review bad\n"
                f"(Then see the answer)")

    elif subcmd == "wordle":
        game = mgr.start_wordle(user_id)
        return (f"🔤 **Wordle** ({len(game.word)} letters)\n\n"
                f"Guess with: /edu guess <word>\n"
                f"🟩 = correct position\n🟨 = wrong position\n⬜ = not in word")

    elif subcmd == "guess":
        if len(context.args) < 2:
            return "Usage: /edu guess <word>"
        result, feedback, done = mgr.guess_wordle(user_id, context.args[1])
        return feedback

    elif subcmd == "hangman":
        category = context.args[1] if len(context.args) > 1 else None
        game = mgr.start_hangman(user_id, category)
        display = " ".join("_" for _ in game.word)
        return (f"🎭 **Hangman** — Category: {game.category}\n\n"
                f"Word: `{display}` ({len(game.word)} letters)\n\n"
                f"Guess: /edu hguess <letter>")

    elif subcmd == "hguess":
        if len(context.args) < 2:
            return "Usage: /edu hguess <letter>"
        display, feedback, done = mgr.guess_hangman(user_id, context.args[1])
        return feedback

    elif subcmd == "math":
        difficulty = context.args[1] if len(context.args) > 1 else "medium"
        if difficulty not in ("easy", "medium", "hard"):
            difficulty = "medium"
        problem = mgr.generate_math(difficulty)
        return (f"🔢 **Math Problem** ({difficulty})\n\n"
                f"**{problem.expression}** = ?\n\n"
                f"Answer: /edu mathanswer <number>")

    elif subcmd == "mathanswer":
        if len(context.args) < 2:
            return "Usage: /edu mathanswer <number>"
        try:
            answer = float(context.args[1])
        except ValueError:
            return "Please enter a number."
        profile = mgr.get_profile(user_id)
        profile.math_solved += 1
        profile.add_xp(5, "math_attempt")
        mgr._save_data()
        return f"✅ Answer submitted! Your answer: {answer}\n(Verify with the source)"

    elif subcmd == "code":
        difficulty = context.args[1] if len(context.args) > 1 else None
        challenge = mgr.get_code_challenge(difficulty)
        if not challenge:
            return "No challenges available."
        hints_text = "\n".join(f"💡 {h}" for h in challenge.hints[:2])
        return (f"💻 **{challenge.title}** ({challenge.difficulty.value})\n\n"
                f"{challenge.description}\n\n"
                f"Hints:\n{hints_text}\n\n"
                f"Language: {challenge.language}")

    elif subcmd == "top":
        board = mgr.get_leaderboard()
        if not board:
            return "No users yet."
        lines = ["🏆 **Leaderboard:**\n"]
        medals = ["🥇", "🥈", "🥉"]
        for i, p in enumerate(board):
            medal = medals[i] if i < 3 else f"{i+1}."
            lines.append(f"{medal} **{p.username or p.user_id}** — "
                        f"Lv.{p.level} | {p.xp} XP")
        return "\n".join(lines)

    elif subcmd == "stats":
        stats = mgr.get_stats(user_id)
        acc = stats["quiz_accuracy"]
        return (f"📊 **Your Stats:**\n\n"
                f"Level: {stats['level']} ({stats['xp']} XP)\n"
                f"Streak: {stats['streak']} days\n\n"
                f"📝 Quizzes: {stats['quizzes_taken']} taken, "
                f"{stats['quizzes_correct']} correct ({acc:.0f}%)\n"
                f"🃏 Flashcards: {stats['flashcards_reviewed']} reviewed\n"
                f"🔤 Wordle: {stats['wordle_wins']} wins "
                f"(streak: {stats['wordle_streak']})\n"
                f"🔢 Math: {stats['math_solved']} solved\n"
                f"💻 Code: {stats['code_solved']} solved\n"
                f"🎮 Total games: {stats['total_games']}\n\n"
                f"🏅 Achievements: {len(stats['achievements'])}")

    elif subcmd == "achievements":
        profile = mgr.get_profile(user_id)
        all_achievements = {
            "first_quiz": "📝 First Quiz — Complete your first quiz",
            "quiz_master": "🧠 Quiz Master — Get 50 correct answers",
            "flashcard_fan": "🃏 Flashcard Fan — Review 100 cards",
            "wordle_champion": "🔤 Wordle Champion — Win 10 games",
            "math_wizard": "🔢 Math Wizard — Solve 25 problems",
            "code_ninja": "💻 Code Ninja — Complete 10 challenges",
            "level_10": "⭐ Level 10 — Reach level 10",
            "streak_7": "🔥 Week Warrior — 7 day streak",
        }
        lines = ["🏅 **Achievements:**\n"]
        for name, desc in all_achievements.items():
            unlocked = "✅" if name in profile.achievements else "🔒"
            lines.append(f"{unlocked} {desc}")
        return "\n".join(lines)

    return build_education_commands()
