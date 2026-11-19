# Lane DAG

How `sprint` and `deliver` turn a phased plan into merged code. The skill that sent you here sets the effort profile: which reviews run, whether they block, and how the run ends. This file covers everything else, and the skill's steps use its terms.

## Contents

- The graph
- Planning the graph: contracts, sizing, model routing, briefs
- Existing codebases
- plan_graph.py
- Scaffold
- Running a phase
- Landing a lane and a phase
- Stopping for the user
- Reviews
- Manual QA
- Resuming

## The graph

```
plan ─> validate ─> scaffold ─> phase 1 ─┬─> phase 2 ─> phase 4 ─┐
                                         └─> phase 3 ────────────┴─> final review ─> finish

inside a phase:
  scaffold commit ─> lane a ─┐
                     lane b ─┼─> each lane landed as it reports ─> gate ─> tag phase-N
                     lane c ─┘
```

A lane is one brief handed to one subagent, which works in its own worktree and branch on files no other running lane touches. Lanes are grouped into phases, and each phase adds one demoable capability. A phase's `Depends on` line names the phases it builds on: a phase depends on another if it imports, extends or demos on top of that phase's code, or if it needs one of that phase's files. It can start once every one of them is tagged and its own scaffold is committed. Phase 1 always runs alone. The landing branch is where phases merge, and the gate is the full test suite plus typecheck and build, if any.

The plan file is the state store. Every lane's status and branch, every phase's scaffold SHA and tag, and every accepted choice and review decision live there, so a resumed run reads the plan instead of reconstructing state from git.

Small work skips the graph. When the whole change is one lane's worth of scope by the sizing table below, do it inline in one worktree (or none for a single-file change) with no plan file or phases. Record the base commit before starting. The final review then uses that commit as `<scaffold parent>` and the user's request (or the plan they gave you) as the spec, and rejected findings go in the final report instead of a plan Log.

## Planning the graph

Load `architecting-systems`, `writing-tests`, `handling-errors` and `writer`, and read code-shape.md. Module boundaries, contracts, error model and comment style are cheapest to decide here, before lanes depend on them.

Lanes pass their tests by the shortest route, usually one large file, and can only split work across files the plan gave them. So the contracts section lists every new module path with its single responsibility, and the spec states the error model (what fails, how it's reported, what a caller sees). A plan that names one implementation file for two responsibilities isn't ready.

Write the plan from plan-template.md, inside the run's checkout (the landing branch's worktree), and use that one absolute path for the plan from then on: in `plan_graph.py` calls, lane prompts and resume. Only phase 1 gets full lane briefs and a test-case list up front. Later phases get lane rows with owned files and a `Depends on` line, and their briefs are written while earlier phases run, so phases that will start together are all briefed before dispatch.

Phase 1 is the smallest end-to-end slice the user could watch work. Order phases by capability, not by layer, or there is nothing to show until the end.

### Sizing lanes

A phase takes as long as its slowest lane plus landing, and each lane has a fixed cost: agent startup and code reading, worktree setup, and about a minute of your time checking and merging. Keep lanes small, roughly equal and few. Size by scope, since time estimates are unreliable: agents estimate their own work like a human team would and say days for what lanes finish in minutes.

| Size | Scope | Where it goes |
| --- | --- | --- |
| Tiny | A few lines, one small function, a config change | Inline |
| S | 1 to 2 owned files, one function, endpoint or component, up to about 5 tests | Folded into a related lane, or grouped with other S units into one lane |
| M | One module or capability, with no contract seam inside it. Usually under about 8 files and 20 tests | A lane |
| L+ | More than one capability, or more code than you can check in one read (roughly 600+ lines outside tests) | Split by capability along a contract set in the scaffold, or across two phases |

Then check each phase:

- Lanes own disjoint files. Two lanes that need the same file are one lane, or the shared part moves into the scaffold. `plan_graph.py validate` checks this across concurrent phases too.
- The scaffold owns registration files (the public index or barrel, routers, tests or docs that pin the public API) with every planned export stubbed, so no lane edits them.
- The longest lane is at most about twice the shortest.
- Two to four lanes. Each extra lane is another diff to check and merge.
- Each lane has a reads list: contracts, owned files, its tests, and at most two pattern files. Code reading is the largest per-lane overhead.
- A phase with only one unit of work, or only tiny ones, runs inline in your checkout.

### Choosing a lane's model

Route by how much judgment a lane needs, not its size, since a wrong lane costs more to investigate. A lane goes to sonnet only when its contract and tests are settled in the scaffold, the spec answers every case it touches, it stays inside its owned files with no cross-module invariant, and a wrong implementation would fail its tests. Implementing against a contract, writing tests from a settled case list and mechanical edits usually qualify.

Everything else goes to opus: designing a contract others depend on, filling a spec gap, invariants around state, ordering, caching, concurrency, security or money, cross-module changes, and debugging a failed lane.

### Briefing lanes

Each lane's brief lets an engineer who never saw the conversation finish without asking anything; the template has the fields. Paste it into the dispatch prompt in full, because every ambiguity left in becomes a choice the agent makes alone and you find in review. A brief you can't write without open questions means the lane isn't ready: settle the question, or route it to opus with the question named.

## Existing codebases

The scaffold mechanics assume new code. In an existing codebase:

- The scaffold holds only new contracts (new types, new module stubs, new exports added to shared registration files) and the phase's new failing tests. Existing modules aren't stubbed.
- When two lanes need the same shared file (a router, a types file, a barrel), declarations go in the scaffold and behavior goes to the one lane that owns the file. A phase where most lanes need the same file has too many lanes: run it as fewer, larger lanes or across two phases.
- A lane may edit existing tests it owns when the plan says the behavior changes. Its brief names which tests change and why.

## plan_graph.py

`scripts/plan_graph.py` (in the shared directory) checks the plan and a lane's diff. Run it; don't read it. `-h` describes the plan format it parses. Resolve its absolute path once and write it into the plan header, and give that path to every lane, since lanes run in other worktrees.

| Command | When |
| --- | --- |
| `validate <plan>` | After writing or changing the plan, and before every dispatch |
| `ready <plan>` | Whenever a lane finishes or a phase tags, to see what to dispatch next |
| `check-lane <plan> <phase>/<lane> <base>` | First step of landing a lane, and by the lane itself before it reports |
| `mark <plan> <phase>/<lane> <status> [--branch <name>]` | When you dispatch (`running`, with its branch), merge (`merged`) or cut (`cut`) a lane |
| `tag <plan> <phase> <tag>` | After you create the git tag for a phase |

Exit 1 means it found problems, listed one per line; fix the plan or send the lane back. Exit 2 means a usage or git error.

`check-lane` covers ownership (every changed path is under the lane's `Owns files`, so a lane's read-only `Tests` are protected too), manifest and lockfile changes, and added skip, focus or suppression markers. A plan can extend the manifest and suppression lists in its header.

## Scaffold

Create the landing branch and commit the scaffold for phase 1:

- The plan file.
- Shared types and interfaces.
- The folder layout from the contracts section, with the entry point limited to wiring.
- A stub at every new module path that exports its signatures and throws "not implemented", so typecheck passes and only tests fail.
- Phase 1's tests, written from the test-case list with a test for every edge case the spec names, and read by you before committing. A lane implements what its tests check and skips the rest.
- Anything the gate needs.

Record the SHA on the phase's `Scaffold:` line; lanes start from it. Tests are read-only to implementation lanes, and you fix a missing case in the scaffold.

Later phases get their own scaffold commit of stubs and tests when they start. Never merge a later phase's tests early, or the gate fails on tests nobody is meant to pass yet.

Before phase 1, find: the test runner and its filter syntax, the typecheck command, and how long the full gate takes (run it once); one setup command that makes a fresh worktree runnable without touching the lockfile (symlink the dependency directory from the main checkout, or a frozen-lockfile install); ports, databases or other services the tests share, which the setup command gives each worktree its own copy of; any wrapper that queues or offloads test runs; and whether lanes can run tests, typecheck and `git add`/`git commit` without permission prompts, since background lanes can't answer one.

## Running a phase

Run `plan_graph.py ready` and dispatch what it prints. It holds lanes until their phase's dependencies are tagged and its scaffold is recorded, and caps lanes in flight at four across all phases, since each is a diff you check by hand.

A phase that runs alongside another scaffolds on its own phase branch, `<landing branch>-p<N>`, cut from the landing tip, so its tests stay off the landing branch until it's green. Its lanes branch from that scaffold. A phase's base branch is that phase branch when it has one, and the landing branch otherwise; lane prompts and lane reviews use it. When both phases add exports to a registration file, commit both phases' stubs to the landing branch before either starts; stubs don't fail the gate, only tests do.

Name each lane's branch before dispatch, `<landing branch>-<phase><lane>` (for example `sprint/orders-2a`), and `mark` it `running --branch <name>`. Then dispatch all ready lanes in one message as background `builder` agents, each in its own worktree, with the lane prompt from dispatch-prompts.md and the code-shape lane block. The prompt's first setup step renames the worktree's branch to that name, so the plan, the lane's own `check-lane` and a resume all know it. `builder` defaults to sonnet; pass `model: opus` per the routing above.

While lanes run, do the phase's inline work, then write briefs and test-case lists for every phase that can start once this one lands. Commit inline work whenever it compiles, since lane merges land in the same checkout.

| Who | When | Runs |
| --- | --- | --- |
| Lane | While working | Tests for its own files, filtered |
| Lane | Before reporting | Filtered tests, typecheck, `check-lane` |
| You | Each phase landing | Full gate |
| You | End of run | Full gate plus the demo |

Lanes skip the full suite because the landing gate repeats it. If the full gate takes under about 10 seconds, lanes can run it too. When the repo has a wrapper that queues or offloads test runs, put every test and typecheck command through it, yours and the lanes', and write the wrapped commands into each brief. Before starting a run, stop any earlier run of yours that is still going.

## Landing a lane and a phase

Check each lane as soon as it reports. The usual lane failures (an edit outside its files, a weakened test, an unrequested feature, a silent assumption) pass the gate, and the next phase builds on whatever merges.

1. `plan_graph.py check-lane`. Any violation sends the lane back.
2. Against the brief: nothing extra was added, no new export exists only for tests, and you accept each choice the lane reported. Log accepted choices in the plan.
3. For shape, using "Checking a lane diff" in code-shape.md. Tests don't catch these, and they compound across phases.
4. A lane review, when the profile calls for it: dispatch `code-reviewer` in the background with the "Lane review" prompt and keep landing other lanes while it runs. This lane waits for it: triage its findings per "Reviews", and have the fixes made on the lane branch before it merges, so a merged lane never has an open review.

Send a lane back with the violations or findings, and let it fix its own failure first, since it has the context. If it fails again, or it's a sonnet lane that reported failing tests, made a choice you reject, or touched a contract or another lane's files, redispatch it on opus with the brief, the diff and what went wrong, since it needed judgment the routing missed.

Merge each lane with `git merge --no-ff <lane branch>` into its phase's base branch once it passes, and `mark` it `merged`. Run the full gate after the phase's last merge, and fix small failures yourself.

A merge conflict means two lanes shared a file, which `validate` should have caught. Resolve it and fix the plan.

When the gate is green, commit any fixes as `phase N: fixes`, run any review the profile puts before the tag and land its fixes, run the demo, create the git tag `phase-N`, run `plan_graph.py tag`, and remove the phase's lane worktrees. Then tell the user in one line what the phase adds and how to try it (see "Manual QA"). Tags are the demo points; commits between them may be red.

A phase on its own branch lands the same way, with its lanes merged into the phase branch. Once its gate is green there, merge the phase branch into the landing branch, run the full gate again, and tag on the landing branch.

A lane far behind the others doesn't hold the phase when the profile has a timebox. Land without it, then merge it at the start of the next phase, or cut it. A phase that needs its code waits until it merges.

## Stopping for the user

Stop and ask when the same error comes back after a lane's second attempt, or when the plan leaves open a decision the user would want to make (a tradeoff, not a fact you can look up). Otherwise keep going; the user sees progress through phase tags.

## Reviews

The profile sets which reviews run. These rules apply to all of them.

Each review has one scope:

| Review | Diff | Checks |
| --- | --- | --- |
| Lane | Phase scaffold to the lane branch | The lane against its brief |
| Phase boundary | Before the phase's scaffold to the phase's gate-green HEAD | Contracts and module boundaries between the phase's lanes and the code they call |
| Final | Scaffold parent to HEAD | The whole change against the plan |
| Fix | Pre-fix SHA to HEAD | Whether each earlier finding was fixed, and whether the fix broke anything |

Use the matching prompt from dispatch-prompts.md. Each prompt sets the diff, the scope and the output format, which override `code-reviewer`'s defaults.

A finding needs evidence. A correctness finding names the input or state that breaks and what happens; a maintainability finding names the split or rewrite that fixes it. Drop a finding without that.

You triage. Check each finding against the code, then fix it or reject it with a one-line reason in the plan's Log. You have the spec, and the reviewer doesn't.

A fix review is the only second round. It reviews the fix diff, not the whole change, and can't raise findings on code the fix didn't touch. There is no third round. Anything still open goes in the final report.

Leave structural cleanup to a running review instead of refactoring under it, since the refactor makes its findings stale and goes unreviewed.

## Manual QA

Every `phase-N` tag is a point the user can check by hand while later phases keep running. QA is optional: never wait for a sign-off, and a run where the user checks nothing proceeds the same way.

When a phase tags, create a separate checkout for it (`git worktree add <dir> phase-N`), since lane merges keep changing files in the landing checkout and would shift under a running dev server. Tell the user the directory and the demo command. Remove these checkouts when the run finishes.

Treat issues the user reports like review findings. One in files no running lane owns becomes a fix lane in the next phase to start, or a fix commit before the final review if no phases are left. One in files a running lane owns waits until that lane merges. Pause dependent phases only when the user asks to hold after a phase.

## Resuming

After a compaction or restart, re-read this file, the skill and the plan. The plan header names the skill and profile. For each lane marked `running` whose agent is no longer live: if its branch has commits past the phase's scaffold, land it as if it just reported, including any lane review; otherwise `mark` it `pending` and let `ready` dispatch it again. A phase whose lanes are all `merged` but which has no `Tag:` line resumes at the gate: run it, then any review the profile puts before the tag, then tag.

## Commits

Commit messages say what changed and why, not which step of this process produced them: `phase 2: fixes` names the phase, and its body says what was fixed.
