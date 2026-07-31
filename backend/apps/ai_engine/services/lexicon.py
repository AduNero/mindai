"""
Lexicon-based scoring for stress, anxiety, burnout, and depression
indicators, plus lightweight keyword extraction.

This is a transparent, explainable heuristic — word/phrase matching
weighted by density and sentiment polarity — not a clinically validated
instrument or a learned model. It exists because no standard Hugging Face
pipeline outputs these four specific constructs; a real clinical deployment
would pair a validated NLP model with professional review, not lexicon
matching alone. Combined with the sentiment/emotion model outputs, it gives
SentimentResult genuinely content-driven scores today.
"""

import re
from collections import Counter

STRESS_TERMS = {
    "stressed", "stress", "overwhelmed", "overwhelming", "pressure", "deadline",
    "deadlines", "swamped", "burnt out", "burned out", "too much", "can't cope",
    "cant cope", "no time", "exhausting", "frantic", "chaotic", "hectic",
}

ANXIETY_TERMS = {
    "anxious", "anxiety", "worried", "worry", "worrying", "nervous", "panic",
    "panicking", "on edge", "restless", "racing thoughts", "what if", "dread",
    "uneasy", "tense", "afraid", "scared", "fear", "fearful",
}

BURNOUT_TERMS = {
    "burnout", "burned out", "burnt out", "exhausted", "drained", "numb",
    "can't anymore", "cant anymore", "no motivation", "unmotivated", "detached",
    "checked out", "running on empty", "depleted", "apathetic", "indifferent",
}

DEPRESSION_TERMS = {
    "depressed", "depression", "hopeless", "worthless", "empty", "numb",
    "no point", "pointless", "sad", "sadness", "crying", "cry", "alone",
    "lonely", "isolated", "tired of everything", "give up", "giving up",
    "can't go on", "cant go on", "nothing matters", "no energy",
}

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "so", "to", "of", "in",
    "on", "at", "for", "with", "about", "as", "is", "was", "were", "are", "be",
    "been", "being", "i", "me", "my", "myself", "we", "our", "you", "your",
    "he", "she", "it", "they", "them", "this", "that", "these", "those", "just",
    "really", "very", "much", "get", "got", "going", "go", "have", "has", "had",
    "do", "does", "did", "not", "no", "yes", "im", "its", "it's", "dont", "don't",
}

_WORD_RE = re.compile(r"[a-zA-Z']+")


def _term_density(text_lower: str, terms: set[str]) -> float:
    """Fraction of the text (by word count, with multi-word phrases counted once each) matching the lexicon, clamped to [0, 1]."""

    word_count = max(len(_WORD_RE.findall(text_lower)), 1)
    matches = sum(text_lower.count(term) for term in terms)
    density = matches / max(word_count / 12, 1)  # ~1 hit per 12 words saturates the score
    return min(density, 1.0)


def score_constructs(text: str, sentiment_label: str) -> dict:
    """Returns stress/anxiety/burnout/depression_indicator scores in [0, 1]."""

    text_lower = text.lower()
    negativity_boost = 1.15 if sentiment_label == "negative" else 1.0

    return {
        "stress_score": round(min(_term_density(text_lower, STRESS_TERMS) * negativity_boost, 1.0), 3),
        "anxiety_score": round(min(_term_density(text_lower, ANXIETY_TERMS) * negativity_boost, 1.0), 3),
        "burnout_score": round(min(_term_density(text_lower, BURNOUT_TERMS) * negativity_boost, 1.0), 3),
        "depression_indicator_score": round(
            min(_term_density(text_lower, DEPRESSION_TERMS) * negativity_boost, 1.0), 3
        ),
    }


def extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    """Simple frequency-based extractive keywords: lowercased words, stopwords removed, longest/most frequent first."""

    words = [w.lower() for w in _WORD_RE.findall(text) if len(w) > 3 and w.lower() not in _STOPWORDS]
    if not words:
        return []
    counts = Counter(words)
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], -len(kv[0])))
    return [word for word, _ in ranked[:max_keywords]]
