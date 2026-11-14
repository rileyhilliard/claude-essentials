# Lane executor benchmarks

The measurements behind the model routing in SKILL.md. Observed in November 2026; re-measure when models change.

## Small task

Add four validators (`literal`, `union`, `nullable`, `enumeration`) with type inference to an existing two-file schema library, with tests. Codex gpt-6.1-sol through foreman (high effort, priority tier) and an Opus subagent ran in parallel on the same contract in separate worktrees. Both took 62 seconds and passed all 11 hidden acceptance tests, including type-level assertions, with nearly identical code.

## Multi-file task

Build an expression language from a precise spec: lexer, parser, evaluator, error type and public API, about 300 lines plus tests, with exact error kinds and positions. Three trials per arm, all nine started at once in separate worktrees.

| Arm | Times | Hidden suite (36) | Edge-case probes (39) | Blind quality score (of 10) |
| --- | --- | --- | --- | --- |
| Sonnet subagent | 69s, 71s, 74s | all pass | all pass | 8, 7, 7 |
| Opus subagent | 94s, 112s, 116s | all pass | all pass | 7, 7, 6 |
| Codex via foreman | 180s, 213s, 222s | all pass | all pass | 8, 8, 8 |

The blind review relabeled the nine implementations so the reviewer couldn't tell which model wrote which. The only correctness gaps it found, in Sonnet and Opus runs alike, were non-finite literals and env values passing through unchecked: a case the spec named loosely ("any result that is NaN or infinite") and that none of those runs' own tests exercised. Other differences were type looseness (string-typed operators with casts) and error-message quality.

## What it supports and what it doesn't

On well-specified work, Sonnet was the fastest and gave up nothing on quality, and defects tracked untested spec cases rather than the model. Codex through foreman is cheaper but was never faster, so it is not a speed option. The tasks had no open design questions, so this says nothing about Sonnet on judgment-heavy work, which is why routing sends that to opus.
