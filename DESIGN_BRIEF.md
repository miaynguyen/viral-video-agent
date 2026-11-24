# Post Agent — Product Design Response
**Origin Studios · Product Design Intern take-home**
Mia Nguyen · November 2026

**Live prototype:** https://claude.ai/artifact/RQgrNzxr2eWZPC9aruAbfY

---

# Task 1 — The problem

## The A&R / artist-management problem

Short-form video is now the primary discovery channel for new music. An A&R rep's artists are expected to post 3–5x per week on Reels, TikTok, and Shorts — but almost none of them know what actually moves the needle on their own posts. They end up in one of two failure modes:

1. **Posting on vibes** — they push whatever they feel like, metrics are noise, and virality feels random
2. **Over-managing** — the label's social team dictates every post, which kills the artistic voice and burns out the artist

Both outcomes are bad for the A&R relationship. The first makes the artist feel ignored; the second makes them feel controlled.

The missing layer is a tool the **artist uses themselves** that:
- Tells them, in their own voice, what to try next on their own content
- Is short enough to check between studio sessions
- Preserves their aesthetic choices (doesn't prescribe tactics that feel off-brand)
- Gives the A&R rep enough visibility to coach without micromanaging

This is the problem I designed around.

---

# Task 2 — The solution

## The user

**Mia** — songwriter with ~25k Facebook Reels followers, posts 3–4x/week. Not a data analyst. Cares about the song, not the dashboard. Will open the app for ~30 seconds between other things.

Three jobs I designed around:
1. *"Was my last post a hit or a miss?"* — answer in one glance
2. *"What should I change on the next one?"* — one actionable fix, not a chart library
3. *"Is what I'm doing working over time?"* — weekly digest, not daily anxiety

## The approach

The engineering side decides *what's broken* (the model picks the weakest metric). The design side decides *what the creator sees first*. Most analytics dashboards fail by showing every metric at equal weight — the creator has to find the problem themselves. This one inverts that: the agent names one problem per video, and everything else on the screen exists to support or contextualize that one call.

**Three rules I wrote for myself:**
- **One recommendation per video.** If I show three, Mia picks the easiest one. The model already ranked them — I should respect that.
- **Signal over decoration.** Color only appears where state matters (green/yellow/red dots). Everything else is monochrome glass.
- **Comparison before explanation.** A number means nothing without the viral benchmark next to it.

## Visual language

- The creator is doing emotional work (making art), not financial work. A warm, soft, almost ambient UI matches the mood better than the typical analytics "control room."
- Glass morphism lets the content breathe — nothing feels crowded even with 4 KPIs and a chart on the same screen.
- Editorial serif (Instrument Serif) for display numbers makes the data feel *considered* rather than mechanical.

## The user journey

The clickable prototype follows one focused path:

1. **Sign in → quick onboarding** (platform + goals) → lands on dashboard with a 3-step tour
2. **Dashboard** — glance at the hero card (latest post score) and the weekly bar chart. If the score is low, the agent's one-line fix is already visible.
3. **Click into the hero card** → full expanded breakdown with 4 stat cards, agent analysis paragraph with inline-savable highlights, and a before/after showing what happened last time this fix was applied
4. **"Mark as tried"** — adds the tactic to the tracking widget
5. **Weekly digest** — a week later, see which tactic held up and which didn't, under "What's working" vs "Try next week"

**Intended outcome:** Mia closes the app with ONE thing to try on her next post, and a clear sense of whether her last experiment worked.

## Screens

### 1. Dashboard (home)

The single most-important design decision: **the hero card is the most recent post**, not aggregated stats. Mia opens the app wondering about her last post, not her lifetime average.

- **Hero card (left):** latest post, viral-chance ring (0–100%), weakest-signal callout
- **Weekly digest sidebar (right):** bar chart with viral mark reference + personal average
- **KPI row:** 4 metrics each with sparkline trend + viral benchmark + corner status dot
- **Tracked tactics:** condensed row of experiments the creator is running
- **Recent videos:** table with sort/direction/view-toggle controls
- **Notes preview:** the 3 most recently updated findings

### 2. Expanded video

- Full breakdown of one post
- 4 stat cards with status dots (weak = red, mid = yellow, strong = green)
- Agent analysis with inline-savable highlights
- Before/after comparison section showing what happened when the creator previously applied the recommended fix on a similar post

### 3. Notes

- Creator's own playbook, organized into color-coded categories
- Cards link back to source video
- Mini sparklines visualize the pattern inside each note

### 4. Upload

- 5 sources: Facebook Reels, TikTok, Instagram, video upload, CSV upload
- 3-step flow: source → describe → compare benchmark

### 5. Compare

- Side-by-side of any two posts
- Metrics highlighted where one beats the other
- Agent summary at the bottom explaining what the delta means

### 6. Weekly digest

- One-page weekly view
- "What's working" (green) vs "Try next week" (yellow)
- Tactic tracker with running score

## What I deliberately left out

| Left out | Why |
|---|---|
| A full video library / archive view | The dashboard's "recent videos" table is enough — anything older is cold data |
| Export to PDF / share to team | Would have pulled focus from the single-creator flow; A&R visibility is a future add |
| Comments on individual posts | Comments are platform-native; duplicating them adds noise without insight |
| A "score" leaderboard across the label's artists | Competitive dynamics between artists hurt the trust that makes this tool work |
| Custom metric configuration | Creators don't want to pick metrics; they want the model to pick for them |
| Push notifications | Daily pings create anxiety; weekly digest is the only scheduled touch |

## Trade-offs I chose

| Chose | Instead of | Why |
|---|---|---|
| One recommendation per video | Top 3 recommendations | Analysis paralysis. The model already ranked them. |
| Color only for state | Branded color accents everywhere | Color becomes meaningless if it's decorative — I need it to carry signal |
| Serif for display numbers | Sans-serif for all data | Softer tone. The creator is not a trader. |
| Views as the headline metric | Composite "performance score" | Creators understand views. A proprietary score is friction. |
| Weekly digest, not daily | Daily notifications | Patterns stabilize over a week — daily data mostly produces noise and anxiety |
| Saturated signal dots on muted UI | Saturated UI everywhere | The whole screen can't shout. Only the signal shouts. |

## How I'd test whether this is useful

1. **Qualitative first.** Put the prototype in front of 3–5 signed artists and ask them to narrate what they think each screen means. If they can explain the hero card's recommendation in their own words without prompting, the information hierarchy works.
2. **The "did you try it?" test.** The real success metric isn't engagement — it's whether creators act on the recommendation. Track: of users who saw a recommendation, what % hit "Mark as tried" within 7 days.
3. **The A/B on recommendation count.** Does showing 1 vs 3 recommendations actually change the try-rate? My bet is 1 wins — if it doesn't, I was wrong and should rebuild.
4. **The A&R check-in.** Interview 2–3 A&R reps after their artists have used it for a month. Did it change what they talked about in check-ins? Did it reduce "what should I post?" questions?

## What I'd do next with more time

- Wire the actual model — predictions are mocked; next step is connecting the trained `viral_model.joblib`
- Add a "didn't work" button next to "Mark as tried" — the current model only learns from applied tactics, not disconfirmed ones
- Build the A&R companion view — same data, framed for a manager coaching 5 artists
- Dark mode variant of the Solace system
- Tablet layout — currently optimized for desktop + mobile; tablet falls through the gap

---

# Task 3 — How I used AI

## Tools used

- **Claude (claude.ai)** — primary tool. Used in a long iterative conversation to scaffold the HTML/CSS/JS prototype, debug layout issues, and co-write this brief.
- **Claude's artifact publishing** — to host the live clickable prototype at a public URL.
- **ChatGPT (quick sanity checks)** — occasionally, to sanity-check design decisions against a second opinion (e.g. "is a bottom nav still best practice for 5 destinations on mobile?").

## How they helped

Claude compressed roughly a day of hand-coding and debugging into about an hour of focused iteration. The pattern I used:

1. **Describe the screen in plain language** (e.g. "dashboard with a hero card for the latest post, a weekly bar chart, 4 KPI cards, and a recent-videos table")
2. **Get a first pass** of the HTML/CSS
3. **Screenshot what rendered, mark up the problems** ("this ring overlaps, this color is unreadable, move this label out of the way")
4. **Iterate** — each round tightened the design against the real pixels, not an imagined mock

## Example prompts

**Prompt 1 (scaffolding):**
> Create a web+mobile dashboard for a short-form video agent in the Solace design language — glass morphism, warm/cool gradient background, Instrument Serif for display, Inter for body. 6 screens: dashboard, expanded video, notes, upload, compare, weekly digest. Use mock data for a songwriter named Mia posting to Facebook Reels.

**Prompt 2 (specific fix after reviewing a screenshot):**
> The weak/strong/mid should be circles. All circles in the top corner should be color coded green, red, or yellow using the correct color scheme to signal positive or negative direction. Performance vs viral benchmarks should have that corner circle indicator too.

## How I verified the output

- **Visual inspection** in the browser after every publish — did the screen match what I described?
- **Click-through testing** — walked the full flow (login → onboarding → dashboard → expanded → notes → upload → compare → digest) after every change to catch breakage
- **Specific feedback over vague feedback** — I didn't say "make it nicer." I said "the 29% is overlapping the ring, make the ring bigger and put viral chance inside"
- **Pushed back on wrong AI choices** — when Claude added colored text (green/red) that was hard to read on the background, I said no, all text has to be white, and signal has to come from dots instead
- **Cross-checked the design logic** — on the KPI status dots, Claude initially colored them based on "how far from viral benchmark" which was wrong. I caught it and said: color by arrow direction (up = good, down = bad)

## What I'd do differently with more time

- **Start with a wireframe before touching Claude.** I did the design thinking in the loop, which worked but wasted iterations early on when I was still figuring out the layout. Sketching first would have cut the number of edits in half.
- **Write a system-prompt-style design brief** for Claude at the start, so it wouldn't have to re-learn my color scheme and design rules every few turns.
- **Build a tiny design-token file** (colors, spacing, type scale) and have Claude reference it, so the whole app would stay perfectly consistent instead of me chasing one-off inconsistencies.
- **Use Claude's browser tool proactively** to screenshot and test the prototype itself, instead of waiting for me to catch rendering bugs visually.

---

## Credits & process

- ML pipeline built following Géron Chapter 2 methodology
- Model: logistic regression with `class_weight="balanced"`, 81.5% accuracy on held-out Facebook Reels data
- Prototype: hand-coded HTML/CSS/JS, published as a Claude artifact
