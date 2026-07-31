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

EMOTION_JOY = "joy"
EMOTION_FEAR = "fear"
EMOTION_SADNESS = "sadness"
EMOTION_ANGER = "anger"
EMOTION_LOVE = "love"
EMOTION_SURPRISE = "surprise"
EMOTION_OPTIMISM = "optimism"
EMOTION_DISAPPOINTMENT = "disappointment"

EMOTION_CHOICES = [
    (EMOTION_JOY, "Joy"),
    (EMOTION_FEAR, "Fear"),
    (EMOTION_SADNESS, "Sadness"),
    (EMOTION_ANGER, "Anger"),
    (EMOTION_LOVE, "Love"),
    (EMOTION_SURPRISE, "Surprise"),
    (EMOTION_OPTIMISM, "Optimism"),
    (EMOTION_DISAPPOINTMENT, "Disappointment"),
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
DETECTION_SOURCE_CHAT = "chat"
DETECTION_SOURCE_ASSESSMENT = "assessment"

DETECTION_SOURCE_CHOICES = [
    (DETECTION_SOURCE_JOURNAL, "Journal Entry"),
    (DETECTION_SOURCE_CHAT, "Chat Message"),
    (DETECTION_SOURCE_ASSESSMENT, "Assessment"),
]

RECOMMENDATION_SOURCE_CHOICES = [
    ("mood", "Mood"),
    ("journal", "Journal"),
    ("assessment", "Assessment"),
    ("chat", "Chat"),
    ("system", "System / Scheduled"),
]

GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
    ("non_binary", "Non-binary"),
    ("prefer_not_to_say", "Prefer not to say"),
]

THEME_CHOICES = [
    ("light", "Light"),
    ("dark", "Dark"),
    ("system", "System"),
]
