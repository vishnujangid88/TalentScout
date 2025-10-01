from __future__ import annotations

from typing import List, Set

import phonenumbers
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, field_validator


END_WORDS_DEFAULT: Set[str] = {"quit", "exit", "bye", "goodbye", "stop", "end"}


def is_end_keyword(text: str, end_words: Set[str] | None = None) -> bool:
    words = end_words or END_WORDS_DEFAULT
    return text.strip().lower() in words


def parse_tech_stack(raw: str) -> List[str]:
    items = [
        token.strip().lower()
        for token in raw.replace("/", ",").replace("|", ",").split(",")
        if token.strip()
    ]
    aliases = {
        "js": "javascript",
        "py": "python",
        "ts": "typescript",
        "pgsql": "postgresql",
        "postgre": "postgresql",
        "mongo": "mongodb",
        "tf": "tensorflow",
        "sklearn": "scikit-learn",
    }
    normalized = [aliases.get(x, x) for x in items]
    seen: set[str] = set()
    result: List[str] = []
    for x in normalized:
        if x not in seen:
            seen.add(x)
            result.append(x)
    return result


class CandidateProfile(BaseModel):
    full_name: str
    email: str
    phone: str
    years_experience: float
    desired_positions: str
    location: str
    tech_stack: str

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        try:
            validate_email(v, check_deliverability=False)
            return v
        except EmailNotValidError as exc:
            raise ValueError("Invalid email address") from exc

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, v: str) -> str:
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return v
        except Exception as exc:
            raise ValueError("Invalid phone number") from exc

    @field_validator("full_name", "desired_positions", "location", "tech_stack")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("years_experience")
    @classmethod
    def _years(cls, v: float) -> float:
        if v < 0 or v > 60:
            raise ValueError("Years of experience must be between 0 and 60")
        return v

    @classmethod
    def from_raw(cls, raw: dict) -> "CandidateProfile":
        data = dict(raw)
        years_raw = str(data.get("years_experience", "0")).strip()
        try:
            data["years_experience"] = float(years_raw)
        except Exception:
            data["years_experience"] = -1.0
        return cls(**data)

    def is_complete_minimal(self) -> bool:
        try:
            _ = CandidateProfile(**self.model_dump())
            return True
        except Exception:
            return False
