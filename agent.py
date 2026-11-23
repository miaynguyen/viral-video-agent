import os
import re
import pandas as pd

# ---------------------------------------------------------
# The AI layer: turns predictions + the playbook into advice
# ---------------------------------------------------------
# Run predict.py first: it creates predictions.csv.
# Then run: python agent.py
#
# Two modes:
#   - API mode (automatic): if the ANTHROPIC_API_KEY environment variable is set,
#     the script asks Claude for advice on each video and saves it to advice.md
#   - Manual mode (free with Claude Pro): if no API key is set, the script writes
#     prompt_for_claude.md, which you paste into Claude (claude.ai) yourself

MODEL = "claude-haiku-5-5"
# a small, fast, low-cost Claude model; enough for short written advice

playbook = open("playbook.md", encoding="utf-8").read()
predictions = pd.read_csv("predictions.csv")
# the researched tactics, and the model's output from predict.py

instructions = f"""You are a short-form video coach for a marketing team.
A machine learning model has already predicted each video's chance of passing 100,000 views
and found its weakest and strongest metrics compared with the account's past viral videos.
Your job is only to explain the result and suggest what to try on the next, similar video.

Rules:
- Do not change or second-guess the model's prediction or numbers.
- Recommend tactics ONLY from the playbook below, for the video's weakest metric.
- If the video's hook, type, song/topic or goal is given, make the advice specific to it:
  refer to the actual hook, say how to apply each tactic to this kind of video and this goal,
  and suggest a concrete rewrite or edit where it helps (e.g. a stronger opening line).
- Use only the details given. Never invent facts about the video, the artist or the song.
- If no description is given, give the general version of the tactics.
- Say in one phrase what is already working (the strongest metric).
- Each video says how many tactics to give ("Tactics to give: 1" or "Tactics to give: 2").
  Give exactly that many numbered tactics. If it is 1, the video is on track: say so and
  name what to keep doing.
- "Song or topic" can include a section of the song (chorus, verse, bridge). A section is
  not the song's title; never refer to it as a title.
- Keep it under 120 words, in plain language, and present tactics as things to test.

PLAYBOOK:
{playbook}"""
# the instructions Claude follows: it explains the model's result, it does not decide

def describe_content(row):
    labels = {"hook": "Hook (first line said or shown)", "video_type": "Video type",
              "song_or_topic": "Song or topic", "goal": "Goal of the post"}
    lines = [f"{label}: {row[col]}" for col, label in labels.items()
             if col in row and pd.notna(row[col]) and str(row[col]).strip()]
    return ("\nAbout the video:\n" + "\n".join(lines)) if lines else "\n(No description of the video was provided.)"
# the optional description columns the manager filled in, if any

RATIOS = ["avg_watch_vs_viral", "completion_rate_vs_viral", "share_rate_vs_viral"]

def tactics_to_give(row):
    return 1 if all(row[r] >= 1.0 for r in RATIOS) else 2
# decided in Python, not left to Claude: a video at or above the viral level on every
# metric is on track and gets 1 tactic; any other video gets 2

def describe(row):
    return (f"Video posted {row['published']}\n"
            f"Prediction: {row['prediction']} ({row['viral_chance']:.0%} chance of 100k+ views)\n"
            f"Average watch time: {row['avg_watch']:.1f} s ({row['avg_watch_vs_viral']:.0%} of the viral level)\n"
            f"Completion rate: {row['completion_rate']:.0%} ({row['completion_rate_vs_viral']:.0%} of the viral level)\n"
            f"Share rate: {row['share_rate']:.2%} ({row['share_rate_vs_viral']:.0%} of the viral level)\n"
            f"Weakest metric: {row['weakest_metric']}\n"
            f"Strongest metric: {row['strongest_metric']}\n"
            f"Tactics to give: {tactics_to_give(row)}"
            + describe_content(row))
# one video's results, written out for Claude

videos_text = [describe(row) for _, row in predictions.iterrows()]

def check_advice(advice, row):
    problems = []
    tactics = len(re.findall(r"^\s*(?:\d+[.)]|[-*•])\s+\*\*", advice, flags=re.MULTILINE))
    if tactics != tactics_to_give(row):
        problems.append(f"gave {tactics} tactics, expected {tactics_to_give(row)}")
    if len(advice.split()) > 150:
        problems.append(f"too long ({len(advice.split())} words)")
    keyword = {"Average watch time": "watch", "Completion rate": "complet", "Share rate": "shar"}[row["weakest_metric"]]
    if keyword not in advice.lower():
        problems.append("does not mention the weakest metric")
    if re.search(r"watch (until|till|to) the end", advice, flags=re.IGNORECASE) and "avoid" not in advice.lower() and "don't" not in advice.lower():
        problems.append("suggests a 'watch until the end' prompt (engagement bait)")
    return problems
# automatic check of each response against the rules: number of tactics, length,
# mentions the weakest metric, and no engagement-bait prompt.
# Counts tactics as numbered or bulleted lines that start with a bold title.

if os.environ.get("ANTHROPIC_API_KEY"):
    import anthropic
    client = anthropic.Anthropic()
    # reads the API key from the ANTHROPIC_API_KEY environment variable

    report = ["# Video advice\n"]
    flagged = 0
    for i, text in enumerate(videos_text, start=1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=instructions,
            messages=[{"role": "user", "content": text}],
        )
        advice = "".join(block.text for block in response.content if block.type == "text").strip()
        # the response can start with a "thinking" block (the model's reasoning) before the
        # written answer, so keep only the text blocks. max_tokens leaves room for both.
        if not advice:
            advice = "(No advice returned - try running the script again.)"
        problems = check_advice(advice, predictions.iloc[i - 1])
        check = "Check: passed" if not problems else "Check: FLAGGED - " + "; ".join(problems)
        print(f"\n--- Video {i} ---\n{text}\n\n{advice}\n\n[{check}]")
        report.append(f"## Video {i}\n\n```\n{text}\n```\n\n{advice}\n\n*{check}*\n")
        flagged += bool(problems)
    # one request per video: Claude gets the instructions + playbook and that video's results

    open("advice.md", "w", encoding="utf-8").write("\n".join(report))
    print(f"\nAutomatic check: {len(videos_text) - flagged} of {len(videos_text)} responses passed")
    print("Saved advice.md")

else:
    prompt = (instructions
              + "\n\nWrite the advice for each of these videos, one short section per video:\n\n"
              + "\n\n".join(f"VIDEO {i}\n{t}" for i, t in enumerate(videos_text, start=1)))
    open("prompt_for_claude.md", "w", encoding="utf-8").write(prompt)
    print("No ANTHROPIC_API_KEY found, so no API call was made.")
    print("Saved prompt_for_claude.md: open it, copy everything, and paste it into Claude.")
# manual mode: one prompt with the instructions, the playbook, and every video
