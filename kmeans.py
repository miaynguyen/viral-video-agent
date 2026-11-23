from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.metrics.pairwise import rbf_kernel

class ClusterSimilarity (BaseEstimator, TransformerMixin):
    def __init__(self, n_clusters = 10, gamma=1.0, random_state=None):
        self.n_clusters = n_clusters
        self.gamma = gamma
        self.random_state = random_state
# define initialize method to set the number of clusters, gamma value, and random state for reproducibility.

    def fit(self, X, y=None, sample_weight=None):
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=self.random_state)
        self.kmeans.fit(X, sample_weight=sample_weight)
        return self
# define fit method to fit the KMeans model to the input data X,
# with optional sample weights. The fitted model is stored in self.kmeans.

    def transform(self, X):
        return rbf_kernel(X, self.kmeans.cluster_centers_, gamma=self.gamma)
# define transform method to compute the RBF kernel similarity between the input data X
# and the cluster centers obtained from the fitted KMeans model.
# The gamma parameter controls the width of the RBF kernel.

    def get_feature_names_out (self, names=None):
        return [f"cluster_{i} similarity" for i in range(self.n_clusters)]
# define get_feature_names_out method to return the names of the output features,
# which are based on the number of clusters specified during initialization.
