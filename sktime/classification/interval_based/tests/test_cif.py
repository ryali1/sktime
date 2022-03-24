# -*- coding: utf-8 -*-
"""CanonicalIntervalForest test code."""
import numpy as np
from numpy import testing

from sktime.classification.interval_based import CanonicalIntervalForest
from sktime.datasets import load_basic_motions, load_unit_test


def test_cif_on_unit_test_data():
    """Test of CanonicalIntervalForest on unit test data."""
    # load unit test data
    X_train, y_train = load_unit_test(split="train")
    X_test, y_test = load_unit_test(split="test")
    indices = np.random.RandomState(0).choice(len(y_train), 10, replace=False)

    # train CIF
    cif = CanonicalIntervalForest(
        n_estimators=10, n_intervals=2, att_subsample_size=4, random_state=0
    )
    cif.fit(X_train, y_train)

    # assert probabilities are the same
    probas = cif.predict_proba(X_test.iloc[indices])
    testing.assert_array_equal(probas, cif_unit_test_probas)


def test_dtc_on_unit_test_data():
    """Test of CanonicalIntervalForest on unit test data."""
    # load unit test data
    X_train, y_train = load_unit_test(split="train")
    X_test, y_test = load_unit_test(split="test")
    indices = np.random.RandomState(0).choice(len(y_train), 10, replace=False)

    # train CIF with the sklearn decision tree classifier
    cif = CanonicalIntervalForest(
        n_estimators=10,
        n_intervals=2,
        att_subsample_size=4,
        base_estimator="dtc",
        random_state=0,
    )
    cif.fit(X_train, y_train)

    cif.predict_proba(X_test.iloc[indices])


def test_cif_on_basic_motions():
    """Test of CanonicalIntervalForest on basic motions data."""
    # load basic motions data
    X_train, y_train = load_basic_motions(split="train")
    X_test, y_test = load_basic_motions(split="test")
    indices = np.random.RandomState(4).choice(len(y_train), 10, replace=False)

    # train CIF
    cif = CanonicalIntervalForest(
        n_estimators=10, n_intervals=2, att_subsample_size=4, random_state=0
    )
    cif.fit(X_train.iloc[indices], y_train[indices])

    # assert probabilities are the same
    probas = cif.predict_proba(X_test.iloc[indices])
    testing.assert_array_equal(probas, cif_basic_motions_probas)


cif_unit_test_probas = np.array(
    [
        [0.41, 0.5900000000000001],
        [0.7333333333333333, 0.26666666666666666],
        [0.18333333333333332, 0.8166666666666667],
        [0.7666666666666666, 0.2333333333333333],
        [0.5, 0.5],
        [0.76, 0.24],
        [0.8, 0.2],
        [0.2833333333333333, 0.7166666666666666],
        [0.86, 0.13999999999999999],
        [0.7, 0.3],
    ]
)
cif_basic_motions_probas = np.array(
    [
        [0.0, 0.0, 0.3, 0.7],
        [0.6, 0.2, 0.2, 0.0],
        [0.0, 0.1, 0.6, 0.3],
        [0.1, 0.5, 0.0, 0.4],
        [0.0, 0.0, 0.3, 0.7],
        [0.0, 0.0, 0.3, 0.7],
        [0.6, 0.2, 0.0, 0.2],
        [0.2, 0.0, 0.6, 0.2],
        [0.0, 0.5, 0.1, 0.4],
        [0.3, 0.7, 0.0, 0.0],
    ]
)
