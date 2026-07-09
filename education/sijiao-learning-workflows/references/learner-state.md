# Learner State

The state layer prevents the tutor from restarting every session.

## File
Use `~/teach/<topic>/learner-state.json`.
Keep `learner-state.example.json` for portable exports.
Do not publish personal state by default.

## Minimal schema

```json
{
  "topic": "linear-algebra",
  "current_module": "eigenvalues-geometric-meaning",
  "mastery": {
    "module-id": 0.65
  },
  "due_reviews": [
    {
      "id": "borrow-rule-1",
      "prompt": "...",
      "answer_key": "...",
      "due": "2026-07-04",
      "interval_days": 3,
      "ease": 2.5
    }
  ],
  "mistakes": [
    {
      "date": "2026-07-03",
      "module": "...",
      "mistake": "...",
      "fix": "..."
    }
  ],
  "last_session": {
    "date": "2026-07-03",
    "summary": "...",
    "next_action": "..."
  }
}
```

## Session update rules
1. Start by reading the state file if it exists.
2. Run due reviews before new content unless the user explicitly asks otherwise.
3. After a user answer, update mastery based on evidence, not encouragement.
4. Add a review item when a concept is important and retrievable.
5. Record mistakes as compact fixable patterns.
6. End with one next action.

## Review scheduling
Use simple spaced repetition unless a topic has a specialized schedule:

- new correct item: +1 day;
- repeated correct: multiply interval by about 2;
- wrong or shaky: reset to same day or +1 day with a narrower prompt;
- do not over-schedule low-value facts.

## Integration with learning records
For non-obvious lessons or strategy changes, also write a `learning-records/NNNN-*.md` entry via the `teach` workflow. Learner state is operational; learning records are durable reflection.
