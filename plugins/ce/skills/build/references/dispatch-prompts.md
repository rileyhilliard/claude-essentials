# Dispatch prompts

Fill in the angle-bracketed parts and dispatch each in the background. Each prompt bounds scope and output, since an unbounded critic spends its time on things that don't change the build, and carries everything the agent needs so it doesn't guess.

## Fast devil's advocate

Dispatch `devils-advocate` with `model: sonnet`.

```
Critique this build plan before implementation starts. Read only <plan path>; the code and tests don't exist yet, so skip verifying claims against the codebase.

Look for, in this order:
1. Contradictions between the spec and phase 1's test-case list.
2. Cases the in-scope list implies that the test-case list doesn't cover.
3. Phase 1 being too large to land by its checkpoint (<time>), or not demoable on its own.
4. Lanes that would edit the same file, or depend on something not in the contracts section.

Return at most five findings, most important first, each as one or two sentences naming the plan section it concerns. Use this format instead of your default template, with no summary or mitigation essays. If the plan is sound, say so in one line.
```

## Lane

Dispatch `builder` with the model from the plan's lane table, pasting the lane's brief in full. `builder` already knows the ownership, commit and report rules; they're repeated here so the prompt also works for foreman or a plain subagent.

```
Implement lane <id> of phase <N>. Your brief below is the whole task.

Setup, first and in this order, one command at a time:
1. `git merge-base --is-ancestor <phase scaffold sha> HEAD`. If it fails, run `git merge --ff-only <landing branch>` and check again; if it still fails, stop and report.
2. `<worktree setup command>`

<lane brief from the plan>

<code-shape lane block from references/code-shape.md, pasted in full>

Beyond your owned files and tests, read only: <reads list>. Open anything else only if you're blocked without it.

You own these files and may edit only them: <files>. If you need a change outside them, stop and report what and why instead of making it. <For implementation lanes: The tests in <test files> are read-only and define done. | For test-writing lanes: You own <test files>; write one test per case in the brief.>

If you hit a case the brief doesn't settle, pick the simplest option consistent with the contracts, keep going, and list every such choice in your report.

Run `<filtered test command>` as you go and `<typecheck command>` before reporting, exactly as written (they may queue on an rr lock behind other lanes). Don't run the full suite; it runs when this lane lands.

Stage your owned files by path and commit on your branch when done. Don't merge, push or remove the worktree.

Report in under ten lines: what you implemented, the test and typecheck results, anything you couldn't do, and every choice the brief didn't settle.
```

## Lane check (opus lanes only)

Dispatch `code-reviewer` with `model: opus` after your inline check passes.

```
Review one lane before its phase lands: `git diff <landing branch>...<lane branch>`. Its brief below is the spec for this review; ignore the rest of the codebase except where the diff calls into it.

<lane brief>

Check only: behavior that contradicts the brief, edge cases in the brief that the code gets wrong, contract signatures used differently from the brief's interface, errors that are swallowed or lose context, and code a new reader couldn't follow (files over about 250 lines or functions over about 40 doing more than one job, logic mixed with I/O, exports missing a JSDoc-style doc block or `@throws`, comments that restate the code or narrate the change). Skip formatting and anything the brief marks out of scope. Don't run lint, typecheck or tests; the gate covers them.

Return at most five findings, most severe first, each with file:line and the input or state that breaks, instead of your default template. If the lane is sound, say so in one line.
```

## Final review

Dispatch `code-reviewer` with `model: opus`.

```
Review the diff `git diff <scaffold parent>..HEAD` on branch <branch>. Read <plan path> for the agreed scope; anything listed as out of scope is not a finding.

Focus only on correctness against the spec, gaps in the tests for in-scope behavior, type safety, bugs at lane boundaries (code from different lanes that disagrees about a contract), and maintainability: files or functions with more than one responsibility, logic in entry points or catch-all helper files, modules reaching into each other's internals, swallowed errors, exports missing a JSDoc-style doc block or `@throws` for errors callers can see, and comments that restate the code or narrate the change. Skip project-standards discovery, documentation, UX and accessibility. Don't run lint, typecheck or tests; the gate already ran them.

Return at most eight findings, most severe first, each with file:line and the concrete input or state that breaks (for a maintainability finding, the split or rewrite that fixes it), instead of your default template. Skip formatting preferences.
```
