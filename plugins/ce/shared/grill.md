# Grill

How to question the user until a build's scope is settled. Both `sprint` and `deliver` use it: `sprint` for every build, `deliver` only for decisions an adopted plan leaves open.

Treat the request as a tree of decisions and each round ask every question whose prerequisites are answered.

Ask through the agent's native question tool (`AskUserQuestion` in Claude Code, `request_user_input` in Codex) so the user answers by picking options. Each question is a sentence or two with two to four concrete options, your recommendation first and marked "(Recommended)". When a round has more questions than one call allows, make several calls. Only without a question tool, fall back to a numbered list with a recommendation on each line. Facts you can look up are never questions.

Stop after the round that settles phase 1, usually two and at most three. Decisions that only affect later phases take your recommended default and go in the plan's assumptions, where the user can override them. In `sprint`, the last round always asks where phases land: a new branch (the default) or the current branch. `deliver` always lands on its own branch, so it doesn't ask.
