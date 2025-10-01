import os
import json
import csv
from io import StringIO
from typing import List, Dict, Any

import streamlit as st
from dotenv import load_dotenv

from app.utils.validators import (
    CandidateProfile,
    parse_tech_stack,
    is_end_keyword,
)
from app.utils.questions import generate_question_set
from app.storage.store import LocalJSONStore
from app.utils.sentiment import analyze_sentiment_label
from app.llm.client import get_llm_client

from email_validator import validate_email, EmailNotValidError
import phonenumbers


load_dotenv()

APP_TITLE = "TalentScout - Hiring Assistant"
END_KEYWORDS = {"quit", "exit", "bye", "goodbye", "stop", "end"}


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "profile" not in st.session_state:
        st.session_state.profile: Dict[str, Any] = {}
    if "consent" not in st.session_state:
        st.session_state.consent = False
    if "questions" not in st.session_state:
        st.session_state.questions: List[Dict[str, Any]] = []
    if "ended" not in st.session_state:
        st.session_state.ended = False
    if "question_count" not in st.session_state:
        st.session_state.question_count = 5


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def greeting_block() -> None:
    if not st.session_state.messages:
        add_message(
            "assistant",
            "Hello! I'm TalentScout, your hiring assistant. I will collect your basic details,"
            " understand your tech stack, and ask a few tailored technical questions. You can type"
            " 'exit' anytime to end the conversation.",
        )
        add_message(
            "assistant",
            "First, what's your full name?",
        )


def render_chat() -> None:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])


def _valid_email(text: str) -> bool:
    try:
        validate_email(text.strip(), check_deliverability=False)
        return True
    except EmailNotValidError:
        return False


def _valid_phone(text: str) -> bool:
    try:
        parsed = phonenumbers.parse(text.strip(), None)
        return phonenumbers.is_valid_number(parsed)
    except Exception:
        return False


def collect_candidate_info(user_input: str) -> str:
    profile = st.session_state.profile
    text = user_input.strip()

    if "full_name" not in profile:
        if len(text) < 3:
            return "Please provide your full name (at least 3 characters)."
        profile["full_name"] = text
        return "Great, please share your email address."

    if "email" not in profile:
        if not _valid_email(text):
            return "That doesn't look like a valid email. Please re-enter your email."
        profile["email"] = text
        return "Thanks! What's your phone number (with country code if possible)?"

    if "phone" not in profile:
        if not _valid_phone(text):
            return "That phone number seems invalid. Please include country code if possible."
        profile["phone"] = text
        return "How many years of experience do you have? (e.g., 2, 3.5)"

    if "years_experience" not in profile:
        try:
            years_val = float(text)
            if years_val < 0 or years_val > 60:
                return "Please enter years of experience between 0 and 60."
            profile["years_experience"] = text
        except Exception:
            return "Please enter a number for years of experience (e.g., 2, 3.5)."
        return "What's your desired position(s)?"

    if "desired_positions" not in profile:
        if len(text) < 2:
            return "Please specify at least one desired position."
        profile["desired_positions"] = text
        return "What's your current location (City, Country)?"

    if "location" not in profile:
        if len(text) < 2:
            return "Please provide your current location (City, Country)."
        profile["location"] = text
        return (
            "Please list your tech stack (languages, frameworks, databases, tools)."
            " For example: Python, Django, PostgreSQL, Docker"
        )

    if "tech_stack" not in profile:
        techs = parse_tech_stack(text)
        if not techs:
            return "I couldn't parse that. Please list comma-separated technologies (e.g., Python, React)."
        profile["tech_stack"] = ", ".join(techs)
        return "Would you like to consent to storing your data locally for screening? (yes/no)"

    if not st.session_state.consent:
        st.session_state.consent = text.lower() in {"yes", "y"}
        return "Thanks! Generating tailored technical questions based on your tech stack..."

    return ""


def maybe_finalize_profile() -> CandidateProfile | None:
    if not st.session_state.profile:
        return None
    try:
        return CandidateProfile.from_raw(st.session_state.profile)
    except Exception:
        return None


def ask_technical_questions(profile: CandidateProfile) -> List[Dict[str, Any]]:
    techs = parse_tech_stack(profile.tech_stack)
    questions = generate_question_set(techs, total_questions=st.session_state.question_count)
    return questions


def end_conversation_block(profile: CandidateProfile | None) -> None:
    add_message(
        "assistant",
        "Thank you for your time. Our team will review your responses and reach out with next steps."
    )
    st.session_state.ended = True
    store = LocalJSONStore(base_dir="app/data")
    if st.session_state.consent and profile is not None:
        store.save_conversation(profile.model_dump(), st.session_state.messages, st.session_state.questions)


def _export_profile_json() -> bytes:
    profile = st.session_state.profile
    return json.dumps(profile, ensure_ascii=False, indent=2).encode("utf-8")


def _export_qa_csv() -> bytes:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["idx", "tech", "question", "answer", "sentiment"])
    for idx, q in enumerate(st.session_state.questions, start=1):
        writer.writerow([idx, q.get("tech", ""), q.get("question", ""), q.get("answer", ""), q.get("sentiment", "")])
    return output.getvalue().encode("utf-8")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon="🤝", layout="centered")
    init_state()

    st.title(APP_TITLE)

    with st.sidebar:
        st.subheader("Settings")
        st.write("Conversation end keywords: " + ", ".join(sorted(END_KEYWORDS)))
        st.write("LLM Provider: OpenAI (if OPENAI_API_KEY set) or rule-based fallback")
        st.toggle("Consent to local storage", key="consent")
        st.session_state.question_count = st.slider("Number of technical questions", min_value=3, max_value=8, value=st.session_state.question_count)
        st.divider()
        st.subheader("Exports")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download Profile (JSON)", _export_profile_json(), file_name="profile.json", mime="application/json")
        with col2:
            st.download_button("Download Q&A (CSV)", _export_qa_csv(), file_name="qa.csv", mime="text/csv")

    greeting_block()
    render_chat()

    if st.session_state.ended:
        st.info("Conversation ended. Refresh the page to start again.")
        return

    user_input = st.chat_input("Type your message…")
    if not user_input:
        return

    if is_end_keyword(user_input, END_KEYWORDS):
        add_message("user", user_input)
        end_conversation_block(maybe_finalize_profile())
        render_chat()
        return

    add_message("user", user_input)

    profile = maybe_finalize_profile()

    if profile is None or not profile.is_complete_minimal():
        assistant_reply = collect_candidate_info(user_input)
        if assistant_reply:
            add_message("assistant", assistant_reply)
            render_chat()
            return
        profile = maybe_finalize_profile()

    if profile and not st.session_state.questions:
        questions = ask_technical_questions(profile)
        st.session_state.questions = questions
        intro = (
            f"Generating questions for your tech stack: {', '.join(parse_tech_stack(profile.tech_stack))}. "
            f"Please answer briefly."
        )
        add_message("assistant", intro)
        for idx, q in enumerate(questions, start=1):
            add_message("assistant", f"Q{idx}. {q['question']}")
        render_chat()
        return

    unanswered = [q for q in st.session_state.questions if "answer" not in q]
    if unanswered:
        current = unanswered[0]
        current["answer"] = user_input
        current["sentiment"] = analyze_sentiment_label(user_input)
        remaining = len([q for q in st.session_state.questions if "answer" not in q])
        add_message("assistant", "Noted. " + (f"{remaining} question(s) remaining." if remaining else "Type 'exit' to finish or ask a follow-up."))
        render_chat()
        return

    llm = get_llm_client()
    assistant_reply = llm.chat(
        system_prompt=(
            "You are a hiring assistant for a tech recruitment agency. Keep answers concise,"
            " stay within hiring and tech-screening topics only. If asked unrelated questions,"
            " politely refuse and redirect to hiring-related topics."
        ),
        messages=st.session_state.messages[-10:],
    )
    add_message("assistant", assistant_reply)
    render_chat()


if __name__ == "__main__":
    main()
