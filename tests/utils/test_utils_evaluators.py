import logging

import pytest
from sklearn.base import BaseEstimator
from sklearn.datasets import make_classification
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, make_scorer
from sklearn.model_selection import KFold, train_test_split
from sklearn.svm import SVC

from siapy.utils.evaluators import (
    _check_model_methods,
    cross_validation,
    hold_out_validation,
)


class MockModelValid(BaseEstimator):
    def fit(self, X, y):
        pass

    def predict(self, X):
        pass

    def score(self, X, y):
        pass


class MockModelInvalid(BaseEstimator):
    def fit(self, X, y):
        pass


def test_check_model_methods_valid():
    model = MockModelValid()
    _check_model_methods(model)


def test_check_model_methods_invalid():
    model = MockModelInvalid()
    with pytest.raises(
        AttributeError,
        match="The model must have methods: 'fit', 'predict', and 'score'.",
    ):
        _check_model_methods(model)


@pytest.fixture(scope="module")
def mock_dataset():
    X, y = make_classification(
        n_samples=100, n_features=10, n_classes=2, random_state=0
    )
    return X, y


def test_cross_validation(mock_dataset):
    X, y = mock_dataset
    mean_score = cross_validation(model=SVC(random_state=0), X=X, y=y)
    assert mean_score == pytest.approx(0.9)
    mean_score = cross_validation(model=DummyClassifier(), X=X, y=y)
    assert round(mean_score, 2) == pytest.approx(0.52)


def test_cross_validation_with_kfold(mock_dataset):
    X, y = mock_dataset
    kf = KFold(n_splits=5, random_state=0, shuffle=True)
    mean_score = cross_validation(model=SVC(random_state=0), X=X, y=y, cv=kf)
    assert mean_score == pytest.approx(0.92)


def test_cross_validation_with_custom_scorer(mock_dataset):
    X, y = mock_dataset
    custom_scorer = make_scorer(accuracy_score)
    mean_score = cross_validation(
        model=SVC(random_state=0), X=X, y=y, scoring=custom_scorer
    )
    assert mean_score == pytest.approx(0.9)


def test_cross_validation_with_x_val_y_val(mock_dataset, caplog):
    X, y = mock_dataset
    caplog.set_level(logging.INFO)  # Set the logging level to INFO
    mean_score = cross_validation(model=SVC(random_state=0), X=X, y=y, X_val=X)
    assert mean_score == pytest.approx(0.9)
    assert (
        "Specification of X_val and y_val is redundant for cross_validation."
        "These parameters are ignored." in caplog.text
    )


def test_hold_out_validation(mock_dataset):
    X, y = mock_dataset
    score = hold_out_validation(model=SVC(random_state=0), X=X, y=y, random_state=0)
    assert score == pytest.approx(0.95)
    score = hold_out_validation(model=DummyClassifier(), X=X, y=y, random_state=0)
    assert score == pytest.approx(0.40)


def test_hold_out_validation_with_manual_validation_set(mock_dataset):
    X, y = mock_dataset
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=0
    )
    score = hold_out_validation(
        model=SVC(random_state=0), X=X_train, y=y_train, X_val=X_val, y_val=y_val
    )
    assert score == pytest.approx(0.95)


def test_hold_out_validation_with_incomplete_manual_validation_set(mock_dataset):
    X, y = mock_dataset
    X_train, X_val, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=0)
    with pytest.raises(
        ValueError,
        match="To manually define validation set, both X_val and y_val must be specified.",
    ):
        hold_out_validation(
            model=SVC(random_state=0), X=X_train, y=y_train, X_val=X_val
        )


def test_hold_out_validation_with_custom_scorer_func(mock_dataset):
    X, y = mock_dataset
    custom_scorer = make_scorer(accuracy_score)
    score = hold_out_validation(
        model=SVC(random_state=0), X=X, y=y, scoring=custom_scorer, random_state=0
    )
    assert score == pytest.approx(0.95)


def test_hold_out_validation_with_custom_scorer_str(mock_dataset):
    X, y = mock_dataset
    score = hold_out_validation(
        model=SVC(random_state=0), X=X, y=y, scoring="accuracy", random_state=0
    )
    assert score == pytest.approx(0.95)


def test_hold_out_validation_with_stratify(mock_dataset):
    X, y = mock_dataset
    score = hold_out_validation(
        model=SVC(random_state=0), X=X, y=y, stratify=y, random_state=0
    )
    assert score == pytest.approx(0.95)
