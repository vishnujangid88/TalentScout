from __future__ import annotations

import os
import json
import time
import uuid
from typing import List, Dict, Any


class LocalJSONStore:
    def __init__(self, base_dir: str = "app/data") -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_conversation(self, profile: Dict[str, Any], messages: List[Dict[str, Any]], questions: List[Dict[str, Any]]) -> str:
        payload = {
            "id": str(uuid.uuid4()),
            "ts": int(time.time()),
            "profile": profile,
            "messages": messages,
            "questions": questions,
        }
        fname = f"{payload['ts']}_{payload['id']}.json"
        path = os.path.join(self.base_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return path
