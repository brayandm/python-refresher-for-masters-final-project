
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import LinearRegression

from importlib import reload
import experiments.transformers.pca_transformer
reload(experiments.transformers.pca_transformer)

class LinearRegressor(BaseEstimator, RegressorMixin):
        
        def __init__(self, n_components=2):
            self.n_components = n_components
            self.transformer = experiments.transformers.pca_transformer.PCATransformer(n_components=self.n_components)
            self.regressor = LinearRegression()
        
        def fit(self, X, y=None):
            pca_features = self.transformer.fit_transform(X)
            self.regressor.fit(pca_features, y)
            return self
    
        def predict(self, X, y=None):
            pca_features = self.transformer.transform(X)
            return self.regressor.predict(pca_features)
