---
name: study-habits
description: Build effective study habits with spaced repetition, active recall, and session tracking
author: clawd-team
version: 1.0.0
triggers:
  - "study session"
  - "study habits"
  - "learn effectively"
  - "study timer"
  - "exam prep"
---

# Study Habits

*Learning that sticks—through science, not stubbornness.*

## What it does

This skill transforms how you absorb and retain information by combining proven cognitive techniques with persistent session tracking:

- **Study Session Tracking** - Logs when you study, what topic, duration, and effectiveness rating for accountability and pattern recognition
- **Technique Suggestions** - Recommends study methods based on your learning goal (memorization vs. deep understanding vs. skill practice)
- **Spaced Repetition Reminders** - Intelligently schedules review sessions to hit the sweet spot where forgetting begins
- **Progress Dashboard** - Shows your study velocity, topic mastery levels, and retention curves over time
- **Exam Countdown** - Builds personalized prep schedules that work backward from exam date to ensure full coverage

## Usage

**Start study**
: "Start a 50-minute study session on photosynthesis" → Creates a session timer, suggests an optimal study technique, and tracks your focus

**Log topic**
: "I just finished studying Chapter 3, felt confident" → Records the session, captures confidence level, determines next review interval

**Review schedule**
: "When should I review calculus next?" → Shows which topics need review based on spaced repetition algorithm, prioritizes by forgetting curve

**Check progress**
: "Show me my study stats" → Displays sessions completed, topics covered, retention trends, time invested per subject

**Exam countdown**
: "I have an exam in 21 days on biology" → Creates a study plan that distributes chapters across available time, accounts for review cycles, flags high-risk topics

## the user-specific exam prep notes

- For the user's考研/<exam-target> planning, first split a subject into concrete lanes (e.g. English = vocabulary, reading真题, 小三门,作文) instead of treating “start the subject” as one monolithic switch.
- When advising on study materials, prefer one mainline resource plus clear fallback triggers. Do not encourage buying multiple overlapping books before the user has diagnostic evidence from actual practice.
- For <exam-target> math timing, treat late-July math强化 → ~Sep 20真题 as tight but viable: prioritize one main teacher/resource line, independent problem solving, and topic回炉 after真题 starts. Avoid extending强化 for perfection. If线代基础较好, 7–10 days is enough; probability can be 8–10 days; protect roughly 4 weeks for高数 and start真题 around Sep 20 when possible.
- When the user asks about考研报名/预报名 timing, check current official sources (研招网/教育部). Use prior-year dates only as an estimate and label them clearly;预报名 usually costs hours to one day, not a major study-plan blocker, but remind him to check account,学籍校验,报考点,缴费,网上确认.
- For <exam-target> English timing/materials, consult `references/kaoyan-english-<exam-target>-materials.md`: current default is 黄皮书英语一真题 as main material, with 考研真相 only as a sentence-level fallback if reading diagnostics show the need.

## Study Techniques

**Active Recall**
: Test yourself without looking at notes. Forces your brain to retrieve information rather than passively reread. Far more effective than review.

**Spaced Repetition**
: Review material at increasing intervals (1 day, 3 days, 1 week, 2 weeks). This combats the forgetting curve and moves knowledge to long-term memory.

**Pomodoro Technique**
: Study in 25-minute focused bursts with 5-minute breaks. Prevents burnout and maintains attention during sessions.

**Feynman Technique**
: Explain a concept aloud as if teaching it to somuser with no background. Exposes gaps in understanding immediately.

**Interleaving**
: Mix different topics or problem types in one session instead of blocking them. Builds flexible knowledge and stronger pattern recognition.

## Tips

1. **Track confidence, not just completion** — Rate how well you understood each topic (1-10) rather than just marking it done. This surfaces weak areas early.

2. **Use active recall over rereading** — Flashcards, practice problems, and explain-it-aloud beat passively reviewing notes by 10x.

3. **Study in shorter sprints, more often** — Three 45-minute sessions spread across a week beat one 2-hour cramming session. Your brain consolidates overnight.

4. **Review the day after, then space out** — First review should be 24 hours later, then 3 days, then a week. The algorithm handles this automatically.

5. **All data stays local on your machine** — Your study history, notes, and progress never leave your device. Full privacy, full control.
