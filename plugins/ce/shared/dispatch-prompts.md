# Dispatch prompts

Fill in the angle-bracketed parts and dispatch each in the background. Each prompt bounds scope and output, since an unbounded critic spends its time on things that don't change the build, and carries everything the agent needs so it doesn't guess. The scope and output rules in each prompt replace the agent's defaults.

## Contents

- Plan critique, sprint
- Plan critique, deliver
- Lane
- Lane review
- Phase boundary review
- Final review
- Fix review

## Plan critique, sprint

Dispatch `devils-advocate` with `model: sonnet`.

```
Critique this build plan before implementation starts. If you investigate claims against the codebase, keep that investigation timeboxed/efficient.

Look for, in this order:
1. Contradictions between the spec and phase 1's test-case list.
2. Cases the in-scope list implies that the test-case list doesn't cover, including binary input, line endings, path separators and symlinks for code that handles files, paths or text.
3. Phase 1 being larger than the plan's sizing rules allow (more than four lanes, or a lane spanning more than one capability or roughly 600 lines outside tests), or not demoable on its own. Judge size by scope, not by how long you think it will take.
4. Lanes that depend on something not in the contracts section.

Return at most five findings, most important first, each as one or two sentences naming the plan section it concerns. Use this format instead of your default template, with no summary or mitigation essays. If the plan is sound, say so in one line.
```

## Plan critique, deliver

Dispatch `devils-advocate` with `model: opus`.

```
Critique this implementation plan against the real codebase before implementation starts: <plan path>. Read the code the plan touches and check its claims, not just the plan text.

Look for, in this order:
1. Module boundaries and contracts that won't hold: a module given two responsibilities, a contract that leaks internals, code that will need to reach into another module, or a layout that fights the repo's existing structure.
2. Gaps in the error model: failures the plan doesn't say how to report, errors that would be swallowed or lose context, and what a caller sees in each case.
3. Failure modes and edge cases the spec implies but the test-case lists don't cover, including concurrency, ordering, partial failure and data migration where they apply.
4. Plan claims about the existing code that are wrong: functions, files or behavior that don't exist or work differently.
5. Phases that aren't demoable on their own, or a lane spanning more than one capability.

Return at most eight findings, most important first, each as two or three sentences naming the plan section and, where relevant, the file:line in the code. Use this format instead of your default template. If the plan is sound, say so in one line.
```

## Lane

Dispatch `builder` with the model from the plan's lane table, pasting the lane's brief in full. `builder` already knows the ownership, commit and report rules; they're repeated here so the prompt also works for a plain subagent.

```
Implement lane <phase>/<lane> of the plan at <absolute plan path>. Your brief below is the whole task.

You start in your own worktree. Work only there, with repo-relative paths, and don't `cd` to any other checkout.

Setup, first and in this order, one command at a time:
1. `git checkout -B <lane branch> <phase scaffold sha>`
2. `<worktree setup command>`

<lane brief from the plan>

<code-shape lane block from code-shape.md, pasted in full>

Beyond your owned files and tests, read only: <reads list>. Open anything else only if you're blocked without it.

You own these files and may edit only them: <files>. If you need a change outside them, stop and report what and why instead of making it. <For implementation lanes: The tests in <test files> are read-only and define done. | For test-writing lanes: You own <test files>; write one test per case in the brief.>

If you hit a case the brief doesn't settle, pick the simplest option consistent with the contracts, keep going, and list every such choice in your report.

Run `<filtered test command>` as you go and `<typecheck command>` before reporting, exactly as written (they may queue behind other lanes). Don't run the full suite; it runs when this lane lands.

Stage your owned files by path and commit on your branch when done. Then run `python3 <absolute plan_graph.py path> check-lane <absolute plan path> <phase>/<lane> <phase scaffold sha>` and fix anything it reports. Don't merge, push or remove the worktree.

Report in under ten lines: what you implemented, the test, typecheck and check-lane results, anything you couldn't do, and every choice the brief didn't settle.
```

## Lane review

Dispatch `code-reviewer` with `model: opus` after your inline check passes.

```
Review one lane before it merges: `git diff <phase scaffold sha>...<lane branch>`. Review only that diff; its brief below is the spec for this review. Ignore the rest of the codebase except where the diff calls into it.

<lane brief>

Check only: behavior that contradicts the brief, edge cases in the brief that the code gets wrong, contract signatures used differently from the brief's interface, errors that are swallowed or lose context, and code a new reader couldn't follow (files over about 250 lines or functions over about 40 doing more than one job, logic mixed with I/O, exports missing a JSDoc-style doc block or `@throws`, comments that restate the code or narrate the change). Skip formatting and anything the brief marks out of scope. Don't run lint, typecheck or tests; the gate covers them.

Report a finding only with evidence: for correctness, the input or state that breaks and what happens; for maintainability, the split or rewrite that fixes it. Return at most five findings, most severe first, each with file:line, instead of your default template. If the lane is sound, say so in one line.
```

## Phase boundary review

Dispatch `code-reviewer` with `model: opus` after the phase's gate is green and before it's tagged.

```
Review the boundaries phase <N> set up: `git diff <commit before the phase's scaffold>..HEAD` on <landing branch>. Read <plan path> for the contracts and layout. Each lane in this phase was already reviewed against its brief, so don't re-review lane internals.

Check only: whether the code matches the contracts and layout in the plan, modules reaching into each other's internals instead of their exported contracts, a module carrying two responsibilities, error handling that differs across lanes for the same failure, and contracts later phases will have to break to build on. Don't run lint, typecheck or tests.

Report a finding only with the specific split, rewrite or contract change that fixes it and the file:line it applies to. Return at most five findings, most severe first, instead of your default template. If the boundaries are sound, say so in one line.
```

## Final review

Dispatch `code-reviewer` with `model: opus`.

```
Review the diff `git diff <scaffold parent>..HEAD` on branch <branch>. Read <plan path, or for small work without a plan, the user's request pasted here> for the agreed scope; anything listed as out of scope is not a finding, and findings already rejected in the plan's Log aren't findings unless the code changed since.

Focus only on correctness against the spec, gaps in the tests for in-scope behavior, type safety, bugs at lane boundaries (code from different lanes that disagrees about a contract), and maintainability: files or functions with more than one responsibility, logic in entry points or catch-all helper files, modules reaching into each other's internals, swallowed errors, exports missing a JSDoc-style doc block or `@throws` for errors callers can see, and comments that restate the code or narrate the change. Skip project-standards discovery, documentation, UX and accessibility. Don't run lint, typecheck or tests; the gate already ran them.

Report a finding only with evidence: the concrete input or state that breaks, or for maintainability the split or rewrite that fixes it. Return at most eight findings, most severe first, each with file:line, instead of your default template. Skip formatting preferences.
```

## Fix review

Dispatch `code-reviewer` with `model: opus`, only when the profile allows a second round.

```
Review only the fixes for an earlier review: `git diff <sha before the fixes>..HEAD`. These were the findings:

<findings that were fixed, each with file:line>

For each finding, say whether the diff fixes it. Then report anything the fix diff itself breaks. Don't report anything about code this diff doesn't touch, and don't raise new concerns about the wider change; that review is done.

Return one line per finding (fixed, or not fixed and why), then at most three regressions, each with file:line and the input or state that breaks, instead of your default template.
```
