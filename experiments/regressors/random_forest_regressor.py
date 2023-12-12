
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import RandomForestRegressor

from importlib import reload
import experiments.transformers.pca_transformer

class RFRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, n_pca_components=0, n_estimators=100, max_depth=None):
        self.n_pca_components = n_pca_components
        self.n_estimators = n_estimators
        self.max_depth = max_depth

        if self.n_pca_components > 0:
            self.transformer = experiments.transformers.pca_transformer.PCATransformer(n_components=self.n_pca_components)
        self.regressor = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth
        )

    def fit(self, X, y=None):
        X = X.to_numpy()
        if self.n_pca_components > 0:
            X = self.transformer.fit_transform(X)
        self.regressor.fit(X, y)
        return self

    def predict(self, X, y=None):
        X = X.to_numpy()
        if self.n_pca_components > 0:
            X = self.transformer.transform(X)
        return self.regressor.predict(X)
