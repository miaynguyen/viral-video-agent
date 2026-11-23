import sys
import joblib
import pandas as pd

import pipeline_video  # needed so the saved pipeline can be loaded

# ---------------------------------------------------------
# Load the saved model and the new videos
# ---------------------------------------------------------

saved = joblib.load("viral_model.joblib")
preprocessing = saved["preprocessing"]
model = saved["model"]
features = saved["features"]
benchmarks = saved["benchmarks"]
# everything save_model.py stored: the fitted pipeline, the trained model,
# the 3 feature names, and the typical values of past viral videos

file_name = sys.argv[1] if len(sys.argv) > 1 else "new_videos.csv"
# the spreadsheet to score: give its name after the command
# (python predict.py my_videos.xlsx), or it uses new_videos.csv

if file_name.endswith(".xlsx"):
    videos = pd.read_excel(file_name)
else:
    videos = pd.read_csv(file_name)
# read a CSV or an Excel file. Needed columns (same as video_data.csv):
# published, views, avg_watch, length, likes, shares
# Optional description columns: hook, video_type, song_or_topic, goal

# ---------------------------------------------------------
# Predict the chance of going viral
# ---------------------------------------------------------

videos["post_day"] = pd.to_datetime(videos["published"]).dt.day_name()
X = pd.DataFrame(preprocessing.transform(videos[["views", "avg_watch", "length", "likes", "shares", "post_day"]]),
                 columns=preprocessing.get_feature_names_out())[features].values
# prepare the new videos exactly like the training data (same pipeline, same settings)

videos["viral_chance"] = model.predict_proba(X)[:, 1]
videos["prediction"] = ["Likely viral" if p >= 0.5 else "Likely not viral" for p in videos["viral_chance"]]
# probability of passing 100k views, and the yes/no call at the 0.5 threshold

# ---------------------------------------------------------
# Diagnose: compare each metric to past viral videos
# ---------------------------------------------------------

videos["completion_rate"] = videos["avg_watch"] / videos["length"]
videos["share_rate"] = videos["shares"] / videos["views"]
# the same metrics the model uses, in their original units

metric_names = {"avg_watch": "Average watch time",
                "completion_rate": "Completion rate",
                "share_rate": "Share rate"}

for metric in metric_names:
    videos[metric + "_vs_viral"] = videos[metric] / benchmarks[metric]
# each metric as a share of the typical viral video's value
# (1.0 = matches viral videos, 0.6 = 60% of the viral level)

ratio_columns = [m + "_vs_viral" for m in metric_names]
videos["weakest_metric"] = videos[ratio_columns].idxmin(axis=1).str.replace("_vs_viral", "").map(metric_names)
videos["strongest_metric"] = videos[ratio_columns].idxmax(axis=1).str.replace("_vs_viral", "").map(metric_names)
# the metric furthest below the viral level is what to fix first

# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

for i, row in videos.iterrows():
    print(f"\nVideo {i + 1} (posted {row['published']})")
    print(f"  Prediction: {row['prediction']} ({row['viral_chance']:.0%} chance of 100k+ views)")
    print(f"  Average watch time: {row['avg_watch']:.1f} s   (viral videos: {benchmarks['avg_watch']:.1f} s)")
    print(f"  Completion rate:    {row['completion_rate']:.0%}      (viral videos: {benchmarks['completion_rate']:.0%})")
    print(f"  Share rate:         {row['share_rate']:.2%}    (viral videos: {benchmarks['share_rate']:.2%})")
    print(f"  Weakest metric: {row['weakest_metric']}   Strongest metric: {row['strongest_metric']}")

context_columns = [c for c in ["hook", "video_type", "song_or_topic", "goal"] if c in videos.columns]
# optional description columns the manager can fill in; they are passed on to the AI layer
# so its advice can refer to the actual video (they are not used by the model)

output = videos[["published", "viral_chance", "prediction", "avg_watch", "completion_rate", "share_rate"]
                + ratio_columns + ["weakest_metric", "strongest_metric"] + context_columns]
output.to_csv("predictions.csv", index=False)
print("\nSaved predictions.csv")
# save the results; the next step (the AI layer) reads this file to write the suggestions
