
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LinearRegression

from importlib import reload
import experiments.transformers.pca_transformer
reload(experiments.transformers.pca_transformer)

class LinearRegressor(BaseEstimator, RegressorMixin):
        
        def __init__(self, n_pca_components=0):
            self.n_pca_components = n_pca_components
            if self.n_pca_components > 0:
                self.transformer = experiments.transformers.pca_transformer.PCATransformer(n_components=self.n_pca_components)
            self.regressor = LinearRegression()
        
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
