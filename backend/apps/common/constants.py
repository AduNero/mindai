"""
Shared enumerations used across multiple apps.

Centralized here so that, e.g., the mood recorded on a `MoodEntry`,
the mood tagged on a `JournalEntry`, and the mood predicted by
`MoodPrediction` all draw from a single source of truth.
"""

MOOD_HAPPY = "happy"
MOOD_NEUTRAL = "neutral"
MOOD_SAD = "sad"
MOOD_ANGRY = "angry"
MOOD_ANXIOUS = "anxious"
MOOD_TIRED = "tired"
MOOD_EXCITED = "excited"
MOOD_DEPRESSED = "depressed"

MOOD_CHOICES = [
    (MOOD_HAPPY, "😊 Happy"),
    (MOOD_NEUTRAL, "😐 Neutral"),
    (MOOD_SAD, "😢 Sad"),
    (MOOD_ANGRY, "😡 Angry"),
    (MOOD_ANXIOUS, "😰 Anxious"),
    (MOOD_TIRED, "😴 Tired"),
    (MOOD_EXCITED, "😍 Excited"),
    (MOOD_DEPRESSED, "😞 Depressed"),
]

SENTIMENT_POSITIVE = "positive"
SENTIMENT_NEGATIVE = "negative"
SENTIMENT_NEUTRAL = "neutral"

SENTIMENT_CHOICES = [
    (SENTIMENT_POSITIVE, "Positive"),
    (SENTIMENT_NEGATIVE, "Negative"),
    (SENTIMENT_NEUTRAL, "Neutral"),
]

SENTIMENT_ACTION_PENDING = "pending"
SENTIMENT_ACTION_ACCEPTED = "accepted"
SENTIMENT_ACTION_REJECTED = "rejected"
SENTIMENT_ACTION_CORRECTED = "corrected"

SENTIMENT_ACTION_CHOICES = [
    (SENTIMENT_ACTION_PENDING, "Pending"),
    (SENTIMENT_ACTION_ACCEPTED, "Accepted"),
    (SENTIMENT_ACTION_REJECTED, "Rejected"),
    (SENTIMENT_ACTION_CORRECTED, "Corrected"),
]

RISK_NONE = "none"
RISK_LOW = "low"
RISK_MODERATE = "moderate"
RISK_HIGH = "high"
RISK_CRITICAL = "critical"

RISK_LEVEL_CHOICES = [
    (RISK_NONE, "None"),
    (RISK_LOW, "Low"),
    (RISK_MODERATE, "Moderate"),
    (RISK_HIGH, "High"),
    (RISK_CRITICAL, "Critical"),
]

DETECTION_SOURCE_JOURNAL = "journal"

DETECTION_SOURCE_CHOICES = [
    (DETECTION_SOURCE_JOURNAL, "Journal Entry"),
]

THEME_CHOICES = [
    ("light", "Light"),
    ("dark", "Dark"),
    ("system", "System"),
]
