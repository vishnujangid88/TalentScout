from __future__ import annotations

from typing import Literal

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer


_analyzer: SentimentIntensityAnalyzer | None = None


def _ensure_vader() -> SentimentIntensityAnalyzer:
    global _analyzer
    if _analyzer is None:
        try:
            _analyzer = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download("vader_lexicon", quiet=True)
            _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def analyze_sentiment_label(text: str) -> Literal["positive", "neutral", "negative"]:
    analyzer = _ensure_vader()
    scores = analyzer.polarity_scores(text)
    compound = scores.get("compound", 0.0)
    if compound >= 0.2:
        return "positive"
    if compound <= -0.2:
        return "negative"
    return "neutral"
