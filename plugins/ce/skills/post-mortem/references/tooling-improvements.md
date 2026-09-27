# Tooling Improvements Investigation

Investigate whether skills, configs, hooks, or agents need updating based on what was learned during the session. This is the primary reference for `.claude/` configuration improvements since those files directly control agent behavior and are the fastest path to self-improvement.

## What to Look For

**Skill gaps** - A skill gave wrong or incomplete guidance:
- Skill recommended an approach that didn't work for this project
- Skill was missing a pattern that would have helped
- Skill's examples didn't match the actual codebase conventions
- A relevant skill exists but wasn't loaded when it should have been

**Config gaps** - CLAUDE.md, rules, or project config is missing context:
- Agent didn't know about project-specific commands or conventions
- Agent used wrong flags or options for project tools
- Agent didn't know about existing utilities or abstractions
- Project-specific gotchas aren't documented anywhere
- Rules in `.claude/rules/` gave wrong or outdated guidance for this project

**Hook gaps** - Automation could have prevented friction:
- A pre-commit check would have caught the issue earlier
- Session-start hook should inject project-specific context
- A PostToolUse hook could validate output before continuing
- Notification hooks could alert on long-running operations

**Workflow gaps** - A recurring recipe should be codified:
- The user restates the same multi-step instruction across sessions
- An existing skill covers the recipe but its description doesn't match how the user phrases the request, so it never triggers
- An existing workflow skill is missing a step the user keeps adding by hand

Codify recipes as model-invocable skills whose descriptions quote the user's own phrasing, not as slash commands. Custom commands have been merged into skills, and users rarely type custom commands; a skill that triggers on the words they already use needs no new habit.

**Agent gaps** - Review or analysis agents need updating:
- Code reviewer missed an issue type it should catch
- Devils-advocate didn't consider a category of risk
- An agent's skill loading doesn't include relevant domain skills
- A subagent came back with a report when it was supposed to change code (the dispatch prompt said "recommend" or "propose" instead of "fix directly")
- A subagent ran on a model that didn't fit the work, because the dispatch didn't set `model`

## Root Cause Questions

For each tooling issue:
1. Does a skill/config already cover this, but it wasn't loaded?
2. Should this be a CLAUDE.md instruction (always active) or a skill (loaded on demand)?
3. Is this project-specific or would it help across all projects?
4. Could a hook automate what was done manually?

## Typical Actions

- Update existing skill with new patterns or corrections
- Add project-specific instructions to CLAUDE.md
- Create new skill for a recurring pattern
- Add hook to automate a manual step
- Rewrite a skill description so it matches how the user asks for the workflow
- Update agent descriptions to load relevant skills
- Add session-start detection for project-specific tooling
