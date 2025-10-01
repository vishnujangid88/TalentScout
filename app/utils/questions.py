from __future__ import annotations

from typing import List, Dict, Any
import random


TECH_QUESTIONS: Dict[str, List[str]] = {
    "python": [
        "Explain list vs tuple and when to use each.",
        "What are generators? Show a simple example.",
        "How does GIL impact multithreading in Python?",
        "Describe context managers and the 'with' statement.",
    ],
    "django": [
        "Explain Django ORM querysets and lazy evaluation.",
        "How do middleware work in Django?",
        "What are class-based views vs function-based views?",
        "How do you manage migrations and schema changes?",
    ],
    "flask": [
        "How do blueprints help structure Flask apps?",
        "How would you handle configuration per environment?",
        "Explain request context vs application context.",
    ],
    "javascript": [
        "Explain event loop and microtasks in JS.",
        "Difference between var, let, and const.",
        "What is closure and a practical use-case?",
    ],
    "react": [
        "When do you use useMemo and useCallback?",
        "Explain reconciliation and keys in lists.",
        "How would you manage global state?",
    ],
    "node": [
        "Explain Node's event-driven architecture.",
        "How do streams work in Node.js?",
        "What is cluster mode and when to use it?",
    ],
    "postgresql": [
        "Explain indexes and when they might hurt performance.",
        "How do transactions and isolation levels work?",
        "What is a CTE and when to use it?",
    ],
    "mongodb": [
        "How do you design schemas in a document DB?",
        "Explain aggregation pipeline basics.",
        "When would you prefer embedded vs referenced docs?",
    ],
    "docker": [
        "Difference between image and container.",
        "How do multi-stage builds reduce image size?",
        "How do you persist data across container restarts?",
    ],
    "kubernetes": [
        "Explain deployments vs statefulsets.",
        "How does a service route traffic to pods?",
        "What are liveness and readiness probes?",
    ],
    "tensorflow": [
        "Explain eager execution vs graph mode.",
        "How do you prevent overfitting in deep nets?",
        "What is transfer learning and when to use it?",
    ],
    "pytorch": [
        "Explain autograd and computational graphs.",
        "How do you manage device placement (CPU/GPU)?",
        "Describe DataLoader and Dataset abstractions.",
    ],
    "scikit-learn": [
        "How do you handle class imbalance?",
        "Difference between bagging and boosting.",
        "What is cross-validation and why is it important?",
    ],
}

GENERIC_QUESTIONS: List[str] = [
    "Describe a challenging bug you solved and the impact.",
    "How do you ensure code quality and readability?",
    "Explain a system you designed end-to-end.",
]


def _questions_for_tech(tech: str) -> List[str]:
    tech_norm = tech.lower()
    return TECH_QUESTIONS.get(tech_norm, [])


def generate_question_set(techs: List[str], total_questions: int = 5) -> List[Dict[str, Any]]:
    picked: List[Dict[str, Any]] = []
    rnd = random.Random(42)

    per_tech = max(1, total_questions // max(1, len(techs)))
    used: set[str] = set()

    for tech in techs:
        bank = _questions_for_tech(tech)
        rnd.shuffle(bank)
        for q in bank[:per_tech]:
            if len(picked) >= total_questions:
                break
            if q in used:
                continue
            used.add(q)
            picked.append({"tech": tech, "question": q})
        if len(picked) >= total_questions:
            break

    if len(picked) < total_questions:
        remaining = total_questions - len(picked)
        rnd.shuffle(GENERIC_QUESTIONS)
        for q in GENERIC_QUESTIONS:
            if remaining <= 0:
                break
            if q in used:
                continue
            used.add(q)
            picked.append({"tech": "general", "question": q})
            remaining -= 1

    return picked
