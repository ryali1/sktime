# -*- coding: utf-8 -*-
# !/usr/bin/env python3 -u
# copyright: sktime developers, BSD-3-Clause License (see LICENSE file)
"""AutoRegressive Model."""
__all__ = ["AutoReg"]
__author__ = ["ryali1"]


from statsmodels.tsa.api import AutoReg as _AutoReg

from sktime.forecasting.base.adapters import _StatsModelsAdapter


class AutoReg(_StatsModelsAdapter):
    """AutoReg Forecaster.

    Direct interface for statsmodels.tsa.ar_model (AutoReg).

    Parameters
    ----------
    endog: array_like
        A 1-d endogenous response variable. The dependent variable.
    lags: {None, int, list[int]}
        The number of lags to include in the model if an integer or the list of lag
        indices to include. For example, [1,4] will only include lags 1 and 4
        while lags=4 will include lags 1, 2, 3, and 4. None excludes all AR lags,
        and behave identically to 0
    trend : str {"c", "ct", "n", "t"} (default="c")
        The trend to include in the modle
        "c" - add constant
        "ct" - constant and trend
        "n" - co constant, no trend
        "t" - time trend only
        Note that these are prepended to the columns of the dataset.
    seasonal: bool {True, False}
        Flag indicating whether to include seasonal dummies in the model. If seasonal
        is True and trend includdes 'c', then the first period is excluded from the
        seasonal terms
    exog: array_like, optional
        Exogenous variables to include in the model. Must have the same number
        of observations as endogenous and should be aligned so that
        endog[i] is regressed on exog[i]
    missing: str
        Available options are 'none', 'drop', and 'raise'.
        If 'none', no nan checking is done.
        If 'drop', any observations with nans are dropped.
        If 'raise', an ereror is raised.
        Default is 'none'.

    References
    ----------
    [1]Poskitt, D. S. (1994). A Note on Autoregressive Modeling.
    Econometric Theory, 10(5), 884–899. http://www.jstor.org/stable/3532858

    Examples
    --------
    >>> from sktime.forecasting.autoreg import AutoReg
    >>> from sktime.datasets import load_airline
    >>> y = load_airline()
    >>> forecaster = AutoReg()
    >>> forecaster.fit(y)
    AutoReg(...)
    >>> y_pred = forecaster.predict(fh=[1,2,3])
    """

    _tags = {
        "scitype:y": "univariate",
        "univariate-only": True,
        "ignores-exogeneous-X": False,  # does estimator ignore the exogeneous X?
        "requires-fh-in-fit": False,
        "handles-missing-data": False,
    }

    def __init__(
        self,
        lags=None,
        trend="c",
        missing="none",
        seasonal=False,
    ):
        # Model params
        self.trend = trend
        self.lags = lags
        self.missing = missing
        self.seasonal = seasonal

        super(AutoReg, self).__init__()

    def _fit_forecaster(self, y, fh=None, X=None):
        """Fit forecaster to training data.

        Wraps Statsmodel's AutoReg fit method.

        Parameters
        ----------
        y : pd.DataFrame
            Target time series to which to fit the forecaster.
        fh : int, list, np.array or ForecastingHorizon, optional (default=None)
            The forecasters horizon with the steps ahead to to predict.
        X : pd.DataFrame, optional (default=None)

        Returns
        -------
        self : returns an instance of self.
        """
        self._forecaster = _AutoReg(
            endog=y,
            exog=X,
            lags=self.lags,
            missing=self.missing,
            trend=self.trend,
            seasonal=self.seasonal,
        )
        self._fitted_forecaster = self._forecaster.fit()
        return self

    def _predict(self, fh, X=None):
        """Make forecasts.

        Parameters
        ----------
        fh : ForecastingHorizon
            The forecasters horizon with the steps ahead to to predict.
            Default is one-step ahead forecast,
            i.e. np.array([1])
        X : pd.DataFrame, optional (default=None)
            Exogenous variables are ignored.

        Returns
        -------
        y_pred : pd.Series
            Returns series of predicted values.
        """
        # statsmodels requires zero-based indexing starting at the
        # beginning of the training series when passing integers
        start, end = fh.to_absolute_int(self._y.index[0], self.cutoff)[[0, -1]]

        y_pred = self._fitted_forecaster.predict(start=start, end=end)

        # statsmodels forecasts all periods from start to end of forecasting
        # horizon, but only return given time points in forecasting horizon
        return y_pred.loc[fh.to_absolute(self.cutoff).to_pandas()]

    def summary(self):
        """Get a summary of the fitted forecaster.

        This is the same as the implementation in statsmodels:
        https://www.statsmodels.org/dev/examples/notebooks/generated/statespace_
        structural_harvey_jaeger.html
        """
        return self._fitted_forecaster.summary()
