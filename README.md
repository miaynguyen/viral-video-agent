# Post Agent: telling artist marketing teams what to fix in their next short-form video

A product proposal and working prototype for an artist's marketing team. It reads a spreadsheet of posted short-form videos, predicts each video's chance of passing 100,000 views, finds the metric holding it back, and writes specific advice for the next video.

**Pipeline:** spreadsheet → machine learning model (chance of going viral + weakest metric) → research playbook (how to fix that metric) → Claude (advice written for that specific video) → automatic check (flags responses that break the rules)

---

## Task 1: Problem and opportunity

**The problem.** Artist teams post short-form videos (teasers, behind-the-scenes clips, live performances) every week to promote releases. Platforms report the numbers (views, watch time, shares), but they don't explain *why* a video stalled or *what to change next time*. Teams fall back on gut feel, so the same mistakes repeat across a release cycle.

**Who experiences it.** Artist managers, label marketing teams and independent artists running their own socials, usually without a data analyst.

**What data helps.** The platform's own post-level insights: views, average watch time, video length, likes and shares. These are things every team can already export. Meta's documentation says Reels ranking predicts how long a viewer will watch and how often a reel is watched to completion, so these metrics directly affect reach.

**Proposed solution.** An agent that turns each post's numbers into a diagnosis and a specific next step: "This teaser has a 29% chance of 100k views. Completion is the problem (24% vs 35% for your viral videos). Your hook promises the chorus, so start the chorus within the first few seconds and put the pre-save prompt right after it."

---

## Task 2: Product feature proposal (Product Management)

### The feature: Post Agent
A weekly "what to fix next" report inside an artist's analytics tool. For every short-form video the team posted, it shows the chance the video passes 100k views, the one metric holding it back compared with the artist's own past hits, and a specific change to try on the next similar video.

### Who it's for
- **Primary:** artist managers and label marketing coordinators who post several promo videos a week (teasers, behind-the-scenes, live clips) and need to decide what to change before the next post.
- **Secondary:** independent artists running their own socials without a data analyst.

### How a user interacts with it
1. **Connect or upload.** The manager connects the artist's Meta account or uploads the Insights export (CSV or Excel). No setup beyond that.
2. **Add a line of context (optional, about a minute per post).** For each video: the hook (first line said or shown), the video type, the song or section, and the goal (pre-saves, followers, reach).
3. **Read the report.** One card per video:
   > **Teaser, "Wait for the chorus" — goal: pre-saves**
   > 29% chance of 100k views · **Fix: completion** (24% vs 35% for your viral videos) · **Working: shares**
   > *Try next:* start the chorus within the first few seconds and put the pre-save prompt right after it.
4. **Act and track.** The manager applies one change to the next post; the following report shows whether that metric improved.

### The three most important requirements
1. **Advice must be specific and grounded.** It names the weakest metric with numbers, compares against the artist's own viral benchmarks, and recommends only tactics from a researched playbook. It never invents facts about the song or artist.
2. **The prediction must be trustworthy, and honest about its limits.** It's shown as a probability, validated on posts the model never saw, and framed as "likely viral or not," not an exact view count, which the data can't support.
3. **It must fit a manager's workflow.** It works from the export teams already have, needs under a minute of input per post, and returns results in seconds, with no data skills required.

### How I'd measure whether it's useful
| Question | Metric |
| --- | --- |
| Do managers use it? | Weekly active teams; share of posts that get a report; share of posts with the optional context filled in |
| Is the advice trusted? | Thumbs up/down on each card; share of suggestions marked "tried" |
| Does it work? | For posts where a suggestion was tried: change in the flagged metric on the next similar post vs. the artist's baseline; change in the share of posts passing 100k over a release cycle |
| Is the prediction reliable? | Accuracy of the viral / not-viral call on new posts, tracked monthly |

### Prototype: evidence it works
I built a working version to test whether the idea holds up on real data (code in this repo).

**Data.** 649 Facebook Reels (April 2025 onward) from a real wellness creator's account, anonymized (captions, links and earnings removed). The account isn't a music artist; I used it because it is real, large and complete. The example descriptions in `new_videos.csv` (hooks, song sections, release goals) are **illustrative**, written to show how an artist team would use it.

**What the data showed.**
- A logistic regression model predicted viral (100k+) vs. not on 130 unseen videos with **81.5% accuracy** (81.4% balanced), beating a decision tree (73.1%) and a random forest (76.9%). It also gives the probability the report displays.
- **Completion rate and watch time drive virality most; like rate barely matters.** That's a useful product insight on its own: teams chasing likes are optimizing the wrong number.
- Exact view counts are hard to predict (watch time explains only about 20% of the variation), which is why requirement 2 frames the output as "likely viral or not."
- An early "under 10k views" category turned out to track account size, not video quality (42 of 43 such videos came from early 2025), so I dropped it. Benchmarks need to come from the artist's own recent posts.

**How it works.** `predict.py` scores the spreadsheet and finds each video's weakest metric → `playbook.md` holds researched tactics per metric (Meta's ranking documentation and creator guidance; Berger & Milkman 2012 on shareable content) → `agent.py` has Claude (Haiku 5.5) write the advice for each video, then automatically checks each response against the rules. The model decides; Claude only explains.

**Run it.**
```
pip install -r requirements.txt
python save_model.py                      # once: trains and saves the model
python predict.py                         # or: python predict.py your_videos.csv
export ANTHROPIC_API_KEY="your-key"       # never commit this
python agent.py                           # writes advice.md
```
Required columns: `published`, `views`, `avg_watch` (seconds), `length` (seconds), `likes`, `shares`. Optional: `hook`, `video_type`, `song_or_topic`, `goal`. Full sample output: `advice.md`.

### What I would build next
- **Retention curves:** show the exact second viewers drop off ("you lose 40% at 0:04, when the text appears").
- **Compare against the artist's own similar posts,** so advice reads "what worked for you."
- **An earlier read:** score posts in their first few hours, while there's still time to boost or repost.
- **Accept the platform's export as-is** and add an upload page, so managers never touch a terminal.
- **Let the AI see the video** (first frames or transcript) to judge the hook directly.

---

## Task 3: How I used AI

**Tools.** Claude (claude.ai, Pro plan) as a coding partner throughout; the Claude API (Haiku 5.5) inside the agent itself; VS Code to run everything.

**How it helped.**
- Building: turning the idea into a working prototype, adapting my machine learning pipeline code with reels data, then building the agent.
- Debugging: a pipeline bug that only appeared on unseen test data.
- Research: finding sources for the playbook.

**Examples of AI-assisted work.**
1. I discussed with Claude how a marketing manager could get advice tailored to the specific video they posted, since the output felt generic. It proposed four approaches; I chose adding description columns (hook, video type, song, goal) and directed Claude to implement it in predict.py and agent.py. The advice went from generic tips to suggestions that reference each video's actual hook and goal.
2. After reviewing the agent's output against the playbook and finding rule violations, I had Claude move the tactic-count rule from the prompt into code and add an automatic check on every response, then reran the agent to confirm the fixes: 4 of 8 responses passed before, 8 of 8 after. The pre-fix version and its output are in before_fixes/ for comparison.

**How I verified the output.**
- **Model:** evaluated only on 130 videos it never saw during training; tuned with cross-validation on training data only; checked that the reloaded saved model reproduced the same 81.5%.
- **Agent:** read every response against the playbook and the rules. I found real mistakes: one response gave two tactics when the rules said one, one treated "bridge" (a song section) as a song title, and an earlier run told the user to move the payoff *earlier* when the playbook says *later*.
- **Fixes:** moved the tactic-count rule from the prompt into code, clarified the instructions, and added an automatic check that flags responses with the wrong number of tactics, too many words, no mention of the weakest metric, or an engagement-bait prompt. **Before the fixes, 4 of 8 responses passed; after, 8 of 8.**
- **Sources:** checked the playbook's claims against the original pages. The strongest evidence comes from Meta's own documentation and peer-reviewed research; one statistic comes from a marketing analytics company and is labeled as directional.

**What I'd do differently.** Plan the data question first: I'd confirm which metrics the export actually contains before choosing features, rather than discovering the missing skip rate later. I'd also build the automatic output check from the start instead of after reading responses by hand.

---

*Data note: the video data is an anonymized export from a real creator account (captions, links and earnings removed), used with permission. No API keys are stored in this repository.*
