"""Optional machine learning utilities for DC3 Model.

This module imports scikit-learn lazily so the deterministic DC3 engine can be
used without installing machine learning dependencies.
"""

from __future__ import annotations


def require_sklearn():
    """Return scikit-learn objects or raise a helpful installation error."""

    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import StratifiedKFold, cross_validate
    except ImportError as exc:
        raise ImportError(
            "Machine learning utilities require the optional 'ml' dependencies. "
            "Install them with: python -m pip install -e .[ml]"
        ) from exc

    return RandomForestClassifier, StratifiedKFold, cross_validate


class DC3RandomForestClassifier:
    """Small wrapper around scikit-learn's RandomForestClassifier."""

    def __init__(self, *, n_estimators: int = 100, random_state: int | None = 42, **kwargs):
        RandomForestClassifier, _, _ = require_sklearn()
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            **kwargs,
        )

    def fit(self, X, y):
        """Fit the underlying Random Forest model."""

        self.model.fit(X, y)
        return self

    def predict(self, X):
        """Predict target labels for new rows."""

        return self.model.predict(X)

    def predict_proba(self, X):
        """Predict class probabilities for new rows."""

        return self.model.predict_proba(X)
