# Claude Essentials

A Claude Code plugin with the skills and agents I use every day: executing plans with a devil's advocate pass and a code review, writing that doesn't read like AI, and a handful of engineering skills. Everything lives under the `ce` namespace.

<img src="/assets/hackerman.gif" width="100%" alt="hackerman">

## What's included

### Skills

Skills load on their own when a request matches their description, and each one can also be run by hand as `/ce:<name>`.

| Skill | What it does |
| --- | --- |
| [ce:executing-plans](plugins/ce/skills/executing-plans/SKILL.md) | Takes a plan or RFC through devil's advocate review, grouped subagent implementation, tests, code review and a local merge to main. Pushes only when asked |
| [ce:post-mortem](plugins/ce/skills/post-mortem/SKILL.md) | Reviews one session or many and turns friction into concrete changes to docs, config, skills and tests |
| [ce:writer](plugins/ce/skills/writer/SKILL.md) | Voice guide with ten personas (engineer, architect, PM, contributor, UX writer and others) plus a catalog of AI rhetorical tells |
| [ce:structuring-articles](plugins/ce/skills/structuring-articles/SKILL.md) | Journalistic story structures (WSJ Formula, Inverted Pyramid, Hourglass, Tick-Tock and more) for long-form pieces |
| [ce:design](plugins/ce/skills/design/SKILL.md) | Design direction and craft rules for product UIs, with CSS and Tailwind references |
| [ce:planning-products](plugins/ce/skills/planning-products/SKILL.md) | Product definition before technical planning: discovery, jobs to be done, experience, scope |
| [ce:architecting-systems](plugins/ce/skills/architecting-systems/SKILL.md) | Module structure, boundaries, coupling, concurrency and observability |
| [ce:writing-tests](plugins/ce/skills/writing-tests/SKILL.md) | Testing Trophy with real dependencies, async waiting, and diagnosing flaky tests |
| [ce:handling-errors](plugins/ce/skills/handling-errors/SKILL.md) | Error handling that doesn't swallow failures or lose context |
| [ce:managing-databases](plugins/ce/skills/managing-databases/SKILL.md) | PostgreSQL, DuckDB, Parquet, PGVector and Neo4j architecture, plus SQL and indexing patterns |

### Agents

| Agent | Model | What it does |
| --- | --- | --- |
| [ce:code-reviewer](plugins/ce/agents/code-reviewer.md) | opus | Reviews a branch diff and returns a flat list of fixes with file:line references |
| [ce:devils-advocate](plugins/ce/agents/devils-advocate.md) | opus | Checks a plan or design against the real code and reports genuine flaws only |
| [ce:copywriter](plugins/ce/agents/copywriter.md) | opus | Drafts articles and essays with the structuring-articles and writer skills preloaded |
| [ce:log-reader](plugins/ce/agents/log-reader.md) | sonnet | Filters large logs by time, severity and request ID and reports the likely cause |

## Installation

You need [Claude Code](https://www.claude.com/product/claude-code).

```bash
/plugin marketplace add https://github.com/rileyhilliard/claude-essentials
/plugin install ce
```

## Usage

Most of the time you don't invoke anything. Ask for the work and the matching skill loads:

- "Have DA review the plan, then implement it, run code review and merge to main" loads `ce:executing-plans`.
- "Rewrite this README so it doesn't sound like AI" loads `ce:writer`.
- "Why is this test flaky?" loads `ce:writing-tests`.
- "Do a post-mortem on this session" loads `ce:post-mortem`.

To run a skill by hand, type `/ce:executing-plans`, `/ce:post-mortem` and so on. Agents are dispatched by the model, or you can ask for one by name ("run ce:code-reviewer on this branch").

## Customizing

A repo's own `.claude/rules/` and `CLAUDE.md` take precedence over these skills' defaults, and the opinionated skills say so at the top. To extend `ce` for a specific codebase (project skills, rules that point at `ce` skills, hooks), see [docs/extending-for-projects.md](docs/extending-for-projects.md).

Skill and agent formats follow the current Claude Code docs; [docs/claude-code-best-practices.md](docs/claude-code-best-practices.md) summarizes them with links.

## License

MIT
