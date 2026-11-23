from sklearn.pipeline import Pipeline
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.preprocessing import FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer, make_column_selector
import pandas as pd
import numpy as np

from kmeans import ClusterSimilarity

def column_ratio(X):
    return X[:, [0]] / X[:, [1]]
# define a function that calculates the ratio of two columns
# for all rows and returns the result as a 2D NumPy array.
def ratio_name (function_transformer, feature_names_in):
    return ['ratio']
# define a function that gives the newly created feature (column)the name "ratio"
def ratio_pipeline():
    return make_pipeline(SimpleImputer(strategy='median'), FunctionTransformer(column_ratio, feature_names_out=ratio_name),
                         StandardScaler())
# define a pipeline for features that need to be transformed to rations
# that fills missing values with the median,
# calculates the ratio between two columns (stores in new column "ratio"),
# and standardizes the resulting ratio

def log_ratio_pipeline():
    return make_pipeline(SimpleImputer(strategy='median'), FunctionTransformer(column_ratio, feature_names_out=ratio_name),
                         FunctionTransformer(np.log, feature_names_out='one-to-one'), StandardScaler())
# define a pipeline for ratios with long tails (like rate and share rate, see step 9)
# that fills missing values with the median,
# calculates the ratio between two columns,
# applies a logarithmic transformation to the ratio,
# and standardizes the resulting values.
# This combines the professor's ratio_pipeline and log_pipeline: the video data has no raw
# column that needs a log on its own, but two of the ratios do.

class FittedClusterSimilarity(ClusterSimilarity):
    def __sklearn_is_fitted__(self):
        return hasattr(self, "kmeans")
# a copy of the professor's ClusterSimilarity that tells scikit-learn when it has been fitted.
# Needed because it is placed inside a small pipeline (after StandardScaler) below:
# scikit-learn checks that every step is fitted before transforming new data (the test set,
# new videos), and it only recognizes fitted attributes that end in "_" (kmeans has no "_").

cluster_simil = make_pipeline(StandardScaler(), FittedClusterSimilarity(n_clusters=4, gamma=1., random_state=42))
# define a ClusterSimilarity object with 4 clusters, a gamma value of 1.0, and a random state of 42 for reproducibility.
# The two columns are standardized first (step 11): length and watch time have different ranges,
# unlike latitude and longitude in the housing data.

default_num_pipeline = make_pipeline(SimpleImputer(strategy="median"),StandardScaler())
# define a default pipeline for numerical values that fills missing values with the median and standardizes the resulting values

cat_pipeline = make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore"))
# define a pipeline for categorical features that fills missing values with the most frequent value
# and applies one-hot encoding to the categorical features, ignoring any unknown categories during transformation

preprocessing = ColumnTransformer([("like_rate", log_ratio_pipeline(), ["likes", "views"]),
                                   ("share_rate", log_ratio_pipeline(), ["shares", "views"]),
                                   ("completion_rate", ratio_pipeline(), ["avg_watch", "length"]),
                                   ("watch", default_num_pipeline, ["avg_watch"]),
                                    ("content", cluster_simil, ["length", "avg_watch"]),
                                    ("cat", cat_pipeline, make_column_selector(dtype_include=object))],
                                  remainder=default_num_pipeline)
# define a ColumnTransformer that applies different preprocessing pipelines to different subsets of features:
# - For the "like_rate" feature, it applies the log_ratio_pipeline to the "likes" and "views" columns.
# - For the "share_rate" feature, it applies the log_ratio_pipeline to the "shares" and "views" columns.
# - For the "completion_rate" feature, it applies the ratio_pipeline to the "avg_watch" and "length" columns.
# - it applies the default_num_pipeline to "avg_watch" so average watch time is also kept as its own feature
#   (in the housing data, features like median_income reach the model through the remainder;
#   avg_watch is already used above, so it has to be listed here to be kept).
# - it applies the cluster_simil to the "length" and "avg_watch" columns.
# - it applies the cat_pipeline to all object (non-numeric) columns (post_day).
# - For all remaining columns, it applies the default_num_pipeline (none are left over in the video data).
# Raw views, likes and shares are only used inside the ratios, so they never reach the model on their own.
