#!/usr/bin/env python3
"""
Question classification for autonomous execution.

This module classifies questions from agents as "optional" vs "critical"
to determine whether execution can continue with a reasonable assumption
or must pause for user input.
"""

from typing import Dict, Any, List
import re


# Keywords indicating critical questions
CRITICAL_KEYWORDS = [
    "security", "authentication", "authorization",
    "data loss", "breaking change", "architecture",
    "cannot", "must know", "which approach",
    "database", "encryption", "credentials",
    "breaking", "incompatible", "migration"
]

# Keywords indicating optional questions
OPTIONAL_KEYWORDS = [
    "prefer", "style", "naming", "formatting",
    "should we", "would you like", "minor",
    "convention", "indentation", "whitespace",
    "color", "layout", "cosmetic"
]


def classify_question(question: Dict[str, Any]) -> str:
    """
    Classify a question as optional vs critical.

    Args:
        question: Question dictionary with 'question' and 'context' fields

    Returns:
        "optional" or "critical"

    Classification rules:
    - Critical: Agent cannot proceed without answer, implementation would be wrong
    - Optional: Agent can make reasonable assumption and continue
    """
    question_text = question.get("question", "").lower()
    context_text = question.get("context", "").lower()
    combined_text = f"{question_text} {context_text}"

    # Check for explicit agent assumption
    has_assumption = bool(question.get("agent_assumption") or question.get("suggested_default"))

    # Count keyword matches
    critical_score = sum(
        1 for keyword in CRITICAL_KEYWORDS
        if keyword in combined_text
    )

    optional_score = sum(
        1 for keyword in OPTIONAL_KEYWORDS
        if keyword in combined_text
    )

    # Decision logic
    if critical_score > optional_score:
        return "critical"
    elif has_assumption and optional_score > 0:
        # Agent has a reasonable default and question seems optional
        return "optional"
    elif has_assumption:
        # Agent has a default - lean toward optional
        return "optional"
    elif critical_score > 0:
        # Has critical keywords - be conservative
        return "critical"
    else:
        # Default to optional to keep execution flowing
        # Most questions agents ask are about preferences, not critical decisions
        return "optional"


def extract_questions_from_response(agent_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract questions from agent response.

    Args:
        agent_response: Agent's full response dictionary

    Returns:
        List of question dictionaries

    Expected question format in response:
    {
        "questions": [
            {
                "question": "Should we use tabs or spaces?",
                "context": "The codebase has mixed formatting",
                "suggested_default": "Using spaces (most common)"
            }
        ]
    }
    """
    # Direct extraction from structured response
    if "questions" in agent_response and isinstance(agent_response["questions"], list):
        return agent_response["questions"]

    # Fallback: Look for question patterns in text content
    content = agent_response.get("content", "")
    if not isinstance(content, str):
        return []

    questions = []

    # Pattern 1: "Question: ..." format
    question_pattern = r"Question:\s*([^\n]+)"
    matches = re.findall(question_pattern, content, re.IGNORECASE)

    for match in matches:
        questions.append({
            "question": match.strip(),
            "context": "Extracted from agent response",
            "classification": "unknown"
        })

    # Pattern 2: Lines ending with "?"
    if not questions:
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.endswith("?") and len(line) > 10:
                questions.append({
                    "question": line,
                    "context": "Extracted from agent response",
                    "classification": "unknown"
                })

    return questions


def should_defer_question(question: Dict[str, Any], classification: str = None) -> bool:
    """
    Determine if a question should be deferred.

    Args:
        question: Question dictionary
        classification: Optional pre-computed classification

    Returns:
        True if question should be deferred (not block execution)
    """
    if classification is None:
        classification = classify_question(question)

    # For now, defer all optional questions
    # Critical questions could potentially block, but we want aggressive deferral
    # per user requirements, so we defer those too unless we add more nuanced logic later

    # Aggressive deferral strategy: defer everything possible
    return True  # Defer all questions per user requirement


def add_classification_to_question(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add classification to a question dictionary.

    Args:
        question: Question dictionary

    Returns:
        Question dictionary with 'classification' and 'priority' fields added
    """
    classification = classify_question(question)

    # Determine priority
    priority = "high" if classification == "critical" else "low"

    return {
        **question,
        "classification": classification,
        "priority": priority
    }


def analyze_question_batch(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze a batch of questions and provide summary.

    Args:
        questions: List of question dictionaries

    Returns:
        Analysis summary
    """
    if not questions:
        return {
            "total": 0,
            "critical": 0,
            "optional": 0,
            "recommendations": "No questions to analyze"
        }

    classified_questions = [add_classification_to_question(q) for q in questions]

    critical_count = sum(1 for q in classified_questions if q["classification"] == "critical")
    optional_count = sum(1 for q in classified_questions if q["classification"] == "optional")

    # Generate recommendations
    if critical_count > 5:
        recommendation = "High number of critical questions - agent may need more initial context"
    elif len(questions) > 20:
        recommendation = "Too many questions - consider pausing execution for user guidance"
    elif critical_count == 0:
        recommendation = "All questions optional - execution can continue safely"
    else:
        recommendation = f"{critical_count} critical question(s) - review after execution completes"

    return {
        "total": len(questions),
        "critical": critical_count,
        "optional": optional_count,
        "recommendations": recommendation,
        "questions": classified_questions
    }


if __name__ == "__main__":
    # Test the classifier
    test_questions = [
        {
            "question": "Should we use tabs or spaces for indentation?",
            "context": "The codebase has mixed formatting",
            "agent_assumption": "Using spaces (most common in repo)"
        },
        {
            "question": "Which database should we use - PostgreSQL or MySQL?",
            "context": "The spec doesn't specify a database",
            "agent_assumption": None
        },
        {
            "question": "What encryption algorithm for passwords?",
            "context": "Security critical decision",
            "agent_assumption": None
        },
        {
            "question": "What color should the submit button be?",
            "context": "UI styling preference",
            "agent_assumption": "Using blue as primary color"
        }
    ]

    print("Question Classification Test\n" + "="*60)

    for i, question in enumerate(test_questions, 1):
        classification = classify_question(question)
        should_defer = should_defer_question(question, classification)

        print(f"\nQuestion {i}: {question['question']}")
        print(f"Classification: {classification}")
        print(f"Should Defer: {should_defer}")
        print(f"Has Assumption: {bool(question.get('agent_assumption'))}")

    # Test batch analysis
    print("\n" + "="*60)
    print("Batch Analysis:")
    analysis = analyze_question_batch(test_questions)
    print(f"Total: {analysis['total']}")
    print(f"Critical: {analysis['critical']}")
    print(f"Optional: {analysis['optional']}")
    print(f"Recommendation: {analysis['recommendations']}")
