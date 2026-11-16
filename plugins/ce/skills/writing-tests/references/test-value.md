# Sizing a Suite

For deciding how many tests a behavior needs, trimming a suite whose tests repeat each other, and checking that a rewrite of a suite didn't lose coverage.

A test is worth its cost when it guards a behavior no other test guards: a rule, a branch, an error path, an output contract. A row that runs the same code path to the same outcome as another row adds runtime and upkeep, and no protection. Realistic combinations are not repetition: a chained command, an operation on state an earlier step left behind, or a failure partway through each reach a different path and keep their rows. Trimming removes the contrived copies, not the realistic cases.

## Patterns that inflate a suite

| Pattern | What it costs | Instead |
| --- | --- | --- |
| One row per spelling of an input that takes the same branch (every flag order, quoting or alias of the same command) | Rows grow with the input space, and one change to the rule breaks dozens of them at once | One realistic input per rule or branch. Add the near misses that guard a specific false positive, one per kind of false positive (a quoted mention, a read-only form, a safe variant), not one per rule |
| A cross product of independent dimensions (every case with and without an optional tool, every case on every platform) | The second dimension is tested once per case of the first | Test the second dimension once, on one representative of each outcome, plus any case that takes a different path there |
| Tests that pin a policy in full detail (every blocked command, every message wording) | Changing the policy means rewriting hundreds of rows, so the tests resist the change they should follow | One row per rule and one per documented exception. When the policy changes, the test diff should be about as large as the rule diff |
| Tests that drive internals (sourcing a script's functions, calling a helper the real caller never calls) | They pass when a change breaks the wiring and fail when a refactor keeps the behavior | Enter the way production does: the command exactly as its config wires it, an input shaped like the one the real caller sends (record one and reuse it), and assertions on what that caller sees |

## Prove a cut before making it

Before deleting tests, measure what each one protects rather than going by its name.

1. List mutations: for each rule, branch and fallback in the code under test, one small edit that breaks it (delete the rule, invert the condition, drop the error handling). Include the non-code inputs the tests read: config files, wiring, templates, and anything composed from them. A mutation set that covers only code lets a rewrite drop every test of the configuration around it with nothing going red.
2. Run the tests against each mutation with a throwaway script that applies it, runs, records which tests failed, and restores the file.
3. Delete a test only when other tests catch every mutation it catches. Every mutation keeps at least one catcher; a mutation nothing catches gets a new test.
4. Run the matrix again on the trimmed suite and keep the table with the change.

When a rewrite replaces whole test files, also list what each deleted file asserted and name the test that now covers it. A check over a whole inventory (every route has auth, every package wires its hooks once) is the easiest to lose, because no mutation of a single artifact shows it missing.

## When a valuable suite is slow

Cost alone isn't a reason to delete a test that guards a behavior. Remove its wasted work first ([slow-tests.md](slow-tests.md)), then run the suite in parallel: shard it across CI jobs (`vitest --shard=1/4`, `pytest -n auto` or splits per job, one `go test` package set per job), with one required check that passes only when every shard did.
