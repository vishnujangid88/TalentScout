from __future__ import annotations

import os
from typing import List, Dict


class RuleBasedLLM:
    def chat(self, system_prompt: str, messages: List[Dict]) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        if any(word in last_user.lower() for word in ["salary", "ctc"]):
            return "Compensation details depend on the role and experience. A recruiter will follow up."
        if "interview" in last_user.lower():
            return "We will schedule interviews based on your fit. Please ensure your details are complete."
        return "I can assist with hiring and tech-screening questions. Could you clarify your query?"


class OpenAILLM:
    def __init__(self) -> None:
        from openai import OpenAI

        self.client = OpenAI()

    def chat(self, system_prompt: str, messages: List[Dict]) -> str:
        history = [
            {"role": "system", "content": system_prompt},
        ] + messages
        try:
            resp = self.client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                messages=history,
                temperature=0.2,
                max_tokens=400,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return RuleBasedLLM().chat(system_prompt, messages)


def get_llm_client():
    if os.getenv("OPENAI_API_KEY"):
        return OpenAILLM()
    return RuleBasedLLM()
