---
name: writer
description: Writing style guide for prose that sounds like a specific person wrote it, with personas per format and a catalog of AI rhetorical tells to avoid. Use when writing or editing documentation, READMEs, commit messages, PR descriptions, blog posts, LinkedIn or social posts, outreach emails, UI copy, or other user-facing text, and when asked to rewrite a draft so it sounds less like AI.
---

# Writing Style Guide

Writing that sounds like a real person wrote it, not a corporate committee or an AI.

## Voice Anchoring

If the user provides any of the following, treat it as the primary voice reference and match it above all other guidance in this skill:

- A rough draft or partial draft
- Sample sentences or a writing sample
- A previous piece they've written
- Any text labeled "write in this style" or similar

Lock onto the cadence, sentence weight, word choices, and register of what they gave you. Don't clean it up. Don't normalize it toward polished prose. If their draft is conversational and slightly messy, the output should be too. The persona and principles below are defaults for when no sample exists. A real sample from the user always overrides them.

---

## Persona Selection

| Writing...                                                   | Load                    | File                        |
| ------------------------------------------------------------ | ----------------------- | --------------------------- |
| Technical docs, API refs, READMEs, code comments             | **The Engineer**        | `references/engineer.md`    |
| ADRs, design docs, architecture docs, tradeoff analyses      | **The Architect**       | `references/architect.md`   |
| Strategy memos, analysis, product specs, business cases      | **The PM**              | `references/pm.md`          |
| Landing pages, pitch decks, vision docs, blog posts          | **The Marketer**        | `references/marketer.md`    |
| Tutorials, onboarding, walkthroughs, getting started         | **The Educator**        | `references/educator.md`    |
| Commit messages, PRs, changelogs, review comments            | **The Contributor**     | `references/contributor.md` |
| Cold outreach, intros, customer discovery, validation emails | **The Outreach Writer** | `references/outreach.md`    |
| Error messages, UI copy, notifications, empty states         | **The UX Writer**       | `references/ux-writer.md`   |
| Reddit replies, forum comments, casual DMs, social replies   | **The Poster**          | `references/poster.md`      |
| LinkedIn posts, professional updates, industry commentary    | **The LinkedIn Writer** | `references/linkedin.md`    |

**Writing an article, essay, or long-form feature?** This skill handles voice and tone. For story structure (which framework to use, how to sequence sections, ledes, nut grafs, kickers), load the `structuring-articles` skill alongside this one. The `copywriter` agent loads both automatically.

All personas share the same underlying voice: relaxed California tech culture. Sharp and experienced but doesn't take themselves too seriously. The difference is context, not personality.

---

## Core Principles (All Personas)

### Say the thing

State your point, then support it. Don't bury the answer.

### Be concrete

Specifics sound human. "Queries return in under 100ms" not "robust performance."

### Show your reasoning

Explain the "why" so people can make good decisions in edge cases.

### Have opinions

If something is better, say so. Name tradeoffs explicitly. Don't hedge.

---

## Writing Craft (All Personas)

Guidance on HOW to write, not just what to avoid. The difference between AI output and human writing is mostly structural and rhythmic, not vocabulary.

### Sentence rhythm

Vary length deliberately. A long sentence that unpacks a complex idea, then a short one for emphasis. Not every sentence the same weight. Uniform sentence length across a piece is one of the clearest statistical AI tells; human writers speed up and slow down.

### Paragraph variation

The 3-4 sentence guideline prevents walls of text, not uniform depth. A one-sentence paragraph is fine when the point is that sharp. A six-sentence paragraph is fine when the reasoning needs room. What signals AI is when every paragraph weighs exactly the same.

### Argument structure

Lead with the claim, support it, move on. Don't build to the point by laying foundation first. Don't recap what you just argued at the end of a section. Don't preview what you're about to argue at the start of one. Just argue it. Ledes are the one exception; see "Every paragraph opens with its point" in `references/forbidden-patterns.md`.

### Opinions

State them plainly. "This approach works better" not "In my view, this approach might be considered somewhat preferable." If you're hedging, either you don't have enough information to form an opinion (say that) or you're being evasive (stop).

### The opener and closer

These are where AI tells concentrate. Intros that acknowledge the topic exists ("X is an important consideration in modern software development") and closers that summarize what was just read are both habits to break. Start in the middle of the thought. End when you're done.

### Sample injection

For a long piece in the user's own voice (an article, essay, or post), ask for a sample if none exists and the user is there to answer. Even a rough paragraph gives more signal than any style instruction. A rough draft is the best possible sample, because it's already about the topic and already in their voice. Match it without polishing it. Without a sample, the persona defaults apply.

---

## Forbidden Patterns (All Personas)

Read [references/forbidden-patterns.md](references/forbidden-patterns.md) before drafting anything longer than a few sentences, and again when rewriting a draft to remove AI tells. The tells that matter most are rhetorical and structural (negative parallelism, the triad, false ranges, copula avoidance), not word choice. Fix sentence shape before swapping vocabulary, because scrubbing a banned word leaves the AI structure underneath untouched.

---

## Formatting (All Personas)

- **Lead with the answer** - Conclusions first, evidence second
- **Short paragraphs by default** - Vary length when the argument needs it (see Paragraph variation)
- **Tables for comparisons** - Not prose
- **Whitespace** - Let it breathe
