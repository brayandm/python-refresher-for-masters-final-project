
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

class PCATransformer(BaseEstimator, TransformerMixin):
    
        def __init__(self, n_components=2):
            self.n_components = n_components
            self.transformer = Pipeline([
                ('scaler', StandardScaler()),
                ('pca', PCA(n_components=self.n_components))
            ])
    
        def fit(self, X, y=None):         
            self.transformer.fit(X, y)
            return self

        def transform(self, X, y=None):
            return self.transformer.transform(X)
