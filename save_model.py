import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from pipeline_video import preprocessing

train = pd.read_csv("videos_train.csv")
train["post_day"] = pd.to_datetime(train["published"]).dt.day_name()
# the training set from step 4, with the post_day column the pipeline expects

features = ["watch__avg_watch", "completion_rate__ratio", "share_rate__ratio"]
# the 3 features the final model uses (average watch time, completion rate, share rate)

X_train = pd.DataFrame(preprocessing.fit_transform(train.drop(["viral", "published"], axis=1)),
                       columns=preprocessing.get_feature_names_out())[features].values
y_train = train["viral"].values
# fit the step 12 pipeline on the training data and keep the 3 features

model = LogisticRegression(C=100, solver="lbfgs", random_state=1, class_weight="balanced")
model.fit(X_train, y_train)
# the tuned logistic regression model from LogReg_video_bnr.py / LogReg_video_tuning.py

train["completion_rate"] = train["avg_watch"] / train["length"]
train["share_rate"] = train["shares"] / train["views"]
viral = train[train["viral"] == 1]
benchmarks = {
    "avg_watch": viral["avg_watch"].median(),
    "completion_rate": viral["completion_rate"].median(),
    "share_rate": viral["share_rate"].median(),
}
# typical (median) values of the past viral videos, in original units.
# The agent compares each new video to these to find its weakest metric.

joblib.dump({"preprocessing": preprocessing, "model": model,
             "features": features, "benchmarks": benchmarks}, "viral_model.joblib")
# save everything the agent needs into one file: the fitted pipeline, the trained model,
# the feature names, and the viral benchmarks

print("Saved viral_model.joblib")
print("Viral benchmarks:", {k: round(float(v), 4) for k, v in benchmarks.items()})
