
from sklearn.base import BaseEstimator, RegressorMixin
from xgboost import XGBRegressor

from importlib import reload
import experiments.transformers.pca_transformer
reload(experiments.transformers.pca_transformer)

class XGBoostRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, n_pca_components=0):
        self.n_pca_components = n_pca_components
        if self.n_pca_components > 0:
            self.transformer = experiments.transformers.pca_transformer.PCATransformer(n_components=self.n_pca_components)
        self.regressor = XGBRegressor()

    def fit(self, X, y=None):
        if self.n_pca_components > 0:
            X = self.transformer.fit_transform(X)
        self.regressor.fit(X, y)
        return self

    def predict(self, X, y=None):
        if self.n_pca_components > 0:
            X = self.transformer.transform(X)
        return self.regressor.predict(X)
