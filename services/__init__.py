# /services/__init__.py

from .ai_service import analyze_resume, correct_resume, tailor_resume

__all__ = [
    "analyze_resume",
    "correct_resume",
    "tailor_resume"
]