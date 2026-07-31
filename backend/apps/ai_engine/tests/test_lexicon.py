from apps.ai_engine.services import lexicon


class TestScoreConstructs:
    def test_stressed_text_scores_high_on_stress(self):
        scores = lexicon.score_constructs(
            "I am so stressed and overwhelmed with these deadlines, I cant cope.", "negative"
        )
        assert scores["stress_score"] > 0.5

    def test_calm_text_scores_near_zero_on_all_constructs(self):
        scores = lexicon.score_constructs(
            "The weather was lovely today and I went for a nice walk in the park.", "positive"
        )
        assert all(v == 0.0 for v in scores.values())

    def test_scores_are_discriminating_not_uniform(self):
        """A stress-specific text shouldn't also max out burnout/depression scores."""
        scores = lexicon.score_constructs("Feeling really stressed about the deadline today.", "negative")
        assert scores["stress_score"] > scores["burnout_score"]
        assert scores["stress_score"] > scores["depression_indicator_score"]

    def test_negative_sentiment_boosts_scores_over_neutral(self):
        text = "stressed anxious worried"
        negative_scores = lexicon.score_constructs(text, "negative")
        neutral_scores = lexicon.score_constructs(text, "neutral")
        assert negative_scores["stress_score"] >= neutral_scores["stress_score"]

    def test_scores_never_exceed_one(self):
        text = " ".join(["stressed overwhelmed anxious worried panic depressed hopeless burnout"] * 10)
        scores = lexicon.score_constructs(text, "negative")
        assert all(0.0 <= v <= 1.0 for v in scores.values())


class TestExtractKeywords:
    def test_extracts_meaningful_words_not_stopwords(self):
        keywords = lexicon.extract_keywords("I have been feeling really anxious about my upcoming deadlines.")
        assert "anxious" in keywords
        assert "deadlines" in keywords
        assert "have" not in keywords

    def test_empty_text_returns_no_keywords(self):
        assert lexicon.extract_keywords("") == []

    def test_respects_max_keywords(self):
        text = " ".join(f"word{i}word" for i in range(20))
        keywords = lexicon.extract_keywords(text, max_keywords=5)
        assert len(keywords) <= 5
