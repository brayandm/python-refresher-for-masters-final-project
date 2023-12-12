
from sklearn.base import BaseEstimator, RegressorMixin
from xgboost import XGBRegressor

from importlib import reload
import experiments.transformers.pca_transformer
reload(experiments.transformers.pca_transformer)

class XGBoostRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, n_pca_components=0, learning_rate=0.3, max_depth=6, n_estimators=100):
        self.n_pca_components = n_pca_components
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.n_estimators = n_estimators

        if self.n_pca_components > 0:
            self.transformer = experiments.transformers.pca_transformer.PCATransformer(n_components=self.n_pca_components)
        self.regressor = XGBRegressor(
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            n_estimators=self.n_estimators
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
