"""Question management for autonomous execution."""

from .question_classifier import (
    classify_question,
    extract_questions_from_response,
    should_defer_question,
    add_classification_to_question,
    analyze_question_batch
)

from .deferred_questions_handler import (
    save_deferred_question,
    load_pending_questions,
    save_user_answers,
    mark_questions_answered,
    get_unanswered_questions,
    get_answered_questions
)

__all__ = [
    # Classification
    "classify_question",
    "extract_questions_from_response",
    "should_defer_question",
    "add_classification_to_question",
    "analyze_question_batch",

    # Handler
    "save_deferred_question",
    "load_pending_questions",
    "save_user_answers",
    "mark_questions_answered",
    "get_unanswered_questions",
    "get_answered_questions"
]
