# TalentScout - AI/ML Hiring Assistant

An intelligent hiring assistant chatbot that collects candidate details, parses tech stacks, and generates tailored technical questions. Built with Streamlit and a pluggable LLM client (OpenAI or deterministic fallback). Optional sentiment analysis is included.

## Features
- Guided information capture: name, email, phone, years of experience, desired roles, location, tech stack
- Tech-stack-based question generation (3-5 questions)
- Conversation context and graceful end on keywords (exit, quit, bye, etc.)
- Fallback responses for off-topic inputs
- Local JSON data storage with user consent
- Optional sentiment analysis of answers

## Tech Stack
- Python, Streamlit
- OpenAI (if `OPENAI_API_KEY` is set) or rule-based fallback
- Pydantic, email and phone validators
- NLTK VADER for sentiment

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. (Optional) Set OpenAI credentials:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY = "YOUR_API_KEY"
$env:OPENAI_MODEL = "gpt-4o-mini"  # optional
```
4. Run the app:
```bash
streamlit run streamlit_app.py
```

## Usage
- Follow the prompts in the chat. Type `exit` to end.
- Toggle consent in the sidebar to allow saving conversation data under `app/data/`.

## Data Privacy
- Only stores data locally when consent is enabled.
- Avoid submitting real personal data during demos. Use anonymized/simulated data.

## Prompt Design
- System prompt constrains scope to hiring and tech screening.
- Deterministic guided flow collects required fields before question generation.
- Questions are derived from normalized tech keywords; generic questions fill gaps.

## Project Structure
```
.
├─ streamlit_app.py           # Streamlit UI and conversation flow
├─ app/
│  ├─ llm/client.py           # OpenAI client + rule-based fallback
│  ├─ storage/store.py        # Local JSON storage
│  └─ utils/
│     ├─ validators.py        # Pydantic schema, parsing, end keywords
│     ├─ questions.py         # Tech-specific question bank
│     └─ sentiment.py         # NLTK VADER sentiment
├─ requirements.txt
├─ .gitignore
└─ README.md
```

## Challenges & Solutions
- Reliable validation: used pydantic and specialized libraries.
- Offline resilience: rule-based LLM fallback ensures demo works without API.
- Data privacy: explicit consent gate before saving.

## Notes
- You can extend `TECH_QUESTIONS` in `app/utils/questions.py` to cover more stacks.
- For a cloud demo, deploy to Streamlit Cloud or any VM with `streamlit run`.
