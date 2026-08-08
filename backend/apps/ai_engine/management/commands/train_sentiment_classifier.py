"""
Fetches the TweetEval sentiment benchmark (pinned commit, not `main` — see
settings.TWEETEVAL_COMMIT_SHA) and trains the TF-IDF + multinomial logistic
regression classifier that apps.ai_engine.services.sentiment_classifier
loads at runtime. Writes the fitted pipeline to
SENTIMENT_MODEL_ARTIFACT_PATH plus a sibling .eval.json report (accuracy,
macro-F1, per-class metrics, confusion matrix) citable in the dissertation.

    python manage.py train_sentiment_classifier
"""

import json
import logging
from datetime import datetime, timezone as dt_timezone

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger("apps")

_LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}
_RAW_BASE = "https://raw.githubusercontent.com/cardiffnlp/tweeteval/{commit}/datasets/sentiment/{filename}"


class Command(BaseCommand):
    help = "Trains the TF-IDF + logistic regression sentiment classifier on TweetEval and writes the artifact + eval report."

    def handle(self, *args, **options):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import classification_report, confusion_matrix
        from sklearn.pipeline import Pipeline

        commit = settings.TWEETEVAL_COMMIT_SHA
        self.stdout.write(f"Fetching TweetEval sentiment dataset at commit {commit}...")

        train_text, train_labels = self._fetch_split(commit, "train")
        test_text, test_labels = self._fetch_split(commit, "test")

        self.stdout.write(f"Loaded {len(train_text)} train / {len(test_text)} test examples. Training...")

        # scikit-learn >=1.5 removed the `multi_class` kwarg: LogisticRegression's
        # default solver (lbfgs) already fits a genuine multinomial/softmax model
        # for a >2-class target, which is what's specified — no explicit flag needed.
        pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer(max_features=50_000, ngram_range=(1, 2), min_df=2)),
                ("clf", LogisticRegression(max_iter=1000, C=1.0)),
            ]
        )
        pipeline.fit(train_text, train_labels)

        predictions = pipeline.predict(test_text)
        report = classification_report(test_labels, predictions, output_dict=True)
        matrix = confusion_matrix(test_labels, predictions, labels=["negative", "neutral", "positive"]).tolist()

        version = f"tfidf-logreg-tweeteval-{commit[:8]}"
        artifact_path = settings.SENTIMENT_MODEL_ARTIFACT_PATH
        artifact_path.parent.mkdir(parents=True, exist_ok=True)

        import joblib

        joblib.dump(
            {
                "pipeline": pipeline,
                "version": version,
                "trained_at": datetime.now(dt_timezone.utc).isoformat(),
                "tweeteval_commit_sha": commit,
            },
            artifact_path,
        )

        eval_report = {
            "model_version": version,
            "tweeteval_commit_sha": commit,
            "trained_at": datetime.now(dt_timezone.utc).isoformat(),
            "n_train": len(train_text),
            "n_test": len(test_text),
            "accuracy": report["accuracy"],
            "macro_f1": report["macro avg"]["f1-score"],
            "per_class": {
                label: report[label] for label in ("negative", "neutral", "positive") if label in report
            },
            "confusion_matrix": {"labels": ["negative", "neutral", "positive"], "matrix": matrix},
        }
        eval_path = artifact_path.with_suffix(".eval.json")
        eval_path.write_text(json.dumps(eval_report, indent=2))

        self.stdout.write(self.style.SUCCESS(f"Wrote classifier artifact to {artifact_path}"))
        self.stdout.write(self.style.SUCCESS(f"Wrote evaluation report to {eval_path}"))
        self.stdout.write(f"Accuracy: {report['accuracy']:.4f}  Macro-F1: {report['macro avg']['f1-score']:.4f}")

    def _fetch_split(self, commit, split):
        text_resp = requests.get(_RAW_BASE.format(commit=commit, filename=f"{split}_text.txt"), timeout=30)
        text_resp.raise_for_status()
        labels_resp = requests.get(_RAW_BASE.format(commit=commit, filename=f"{split}_labels.txt"), timeout=30)
        labels_resp.raise_for_status()

        texts = text_resp.text.strip("\n").split("\n")
        labels = [_LABEL_MAP[int(n)] for n in labels_resp.text.strip("\n").split("\n")]
        if len(texts) != len(labels):
            raise ValueError(f"{split}: text/label count mismatch ({len(texts)} vs {len(labels)})")
        return texts, labels
