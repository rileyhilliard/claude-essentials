---
name: structuring-articles
description: Selects and applies professional journalistic story structures (WSJ Formula, Inverted Pyramid, Hourglass, Tick-Tock, etc.) based on the content being written. Use when writing articles, blog posts, features, essays, long-form content, news stories, trend pieces, investigative reports, profiles, or any narrative prose longer than a few paragraphs. Also use when the user asks for help structuring a piece, choosing a story framework, organizing a draft, outlining an article, or wants to know which article format fits their content. Trigger on requests like "help me structure this," "what format should I use," "write a feature about," "draft a blog post on," or any mention of story structure, article architecture, or narrative frameworks. Complements the writer skill (which handles tone and anti-AI rhetoric) by providing the structural blueprint.
---

# Structuring Articles

Professional journalists don't just write — they select a structure that serves their material. A trend piece about remote work demands a different architecture than a breaking news story about a policy change. This skill helps you match content to the right framework, then execute it.

## How This Skill Relates to Other Skills

This skill handles **structure** — the bones of an article. It tells you what goes where and why.

For **voice, tone, and anti-AI rhetoric**, load the `writer` skill. These two skills are designed to work together: structure from here, style from there.

For **executive/strategy documents** (board decks, business cases, market analysis), the `strategy-writer` skill is more appropriate — those follow their own conventions.

---

## Framework Selection

Match the content to a framework before writing. The decision depends on three things: what kind of story is it, what's the strongest material you have, and how much space do you have?

| You're writing about... | Strongest material | Framework | Reference |
|---|---|---|---|
| A systemic trend or issue, and you have a compelling person affected by it | A character whose experience illustrates the bigger picture | **WSJ Formula** | `references/wsj-formula.md` |
| Breaking news, a new report, or a policy announcement | The headline fact — what just happened and why it matters | **Inverted Pyramid** | `references/inverted-pyramid.md` |
| A news event that also needs narrative depth | Both the headline fact AND a rich chronological story behind it | **Hourglass** | `references/hourglass.md` |
| A sequential news event you want to narrate after the headline | The headline fact AND a chronological sequence of what happened | **Martini Glass** | `references/martini-glass.md` |
| A complex topic you want to ease readers into gradually | A specific person or scene AND broad research/data | **Diamond** | `references/diamond.md` |
| A major event and you want to reconstruct how it unfolded | Detailed sourcing on what happened when — timestamps, scenes, dialogue | **Tick-Tock** | `references/tick-tock.md` |
| A story with a dramatic climax moment | A gripping scene you can open with before rewinding | **Nine Structure** | `references/nine-structure.md` |
| Two parallel storylines that illuminate each other | Multiple characters or threads that intersect | **Braided Narrative** | `references/braided-narrative.md` |
| A data-driven story with a central human character | Both quantitative data AND a compelling personal story | **Accordion** | `references/accordion.md` |
| You're on deadline and need to organize material fast | A pile of notes, quotes, and facts that need ordering | **Five Boxes** | `references/five-boxes.md` |

If you're unsure, default to the **WSJ Formula** for features/essays or the **Inverted Pyramid** for news. They're the workhorses.

After selecting a framework, read the relevant reference file for the step-by-step structure.

---

## Universal Elements

Every framework shares a few building blocks. These apply regardless of which structure you choose.

### The Nut Graf

The single most important paragraph in any article. It answers "so what?" — why this story matters, why now, why the reader should care. If a reader skimmed only your headline and nut graf, they should grasp the central point.

In the WSJ Formula, the nut graf appears after the opening anecdote. In the Inverted Pyramid, it's the second or third paragraph. In every other structure, find its natural home — but it must exist, and it must appear early.

A nut graf that's missing or buried is the #1 reason a draft feels aimless.

See `references/prose-craft.md` for detailed guidance on writing nut grafs, plus ledes, transitions, kickers, data integration, and quote handling.

### The Lede

The opening that earns the reader's attention. Seven major types exist (summary, anecdotal, scene-setting, question, contrast, staccato, delayed) — each suited to different material. The framework you choose often implies the lede type: WSJ Formula calls for an anecdotal lede, Inverted Pyramid calls for a summary lede. But these aren't rigid rules.

See `references/prose-craft.md` for the full lede taxonomy.

### The Kicker

The ending. Six types (circle, quote, echo, future-looking, experiential, surprise/revelation). The best endings are discovered during reporting, not manufactured afterward. If your planned ending isn't working, the real ending is probably a few paragraphs earlier.

See `references/prose-craft.md` for kicker guidance.

---

## Sentence and Paragraph Rhythm

This is not about structure — it's about the texture of the prose within any structure. But it's so foundational it belongs here alongside framework selection.

Vary sentence length deliberately. Short sentences punch. Long sentences build complexity and momentum. Uniform sentence length is one of the clearest signals of machine-generated prose. Gary Provost's famous demonstration:

> "This sentence has five words. Here are five more words. Five-word sentences are fine. But several together become monotonous. Listen to what is happening. The writing is getting boring. The sound of it drones. It's like a stuck record. The ear demands some variety.
>
> Now listen. I vary the sentence length, and I create music. Music. The writing sings. It has a pleasant rhythm, a lilt, a harmony."

Read your work aloud. If everything sounds the same length, it will feel monotonous regardless of content.

Paragraph length works the same way. Short paragraphs accelerate. Long paragraphs slow the reader for reflection. A one-sentence paragraph carries enormous weight — the white space around it says "this matters."

---

## When NOT to Use This Skill

Not everything is an article. Skip this skill for:

- Technical documentation, READMEs, API docs → use the `writer` skill's Engineer persona
- Commit messages, PRs, changelogs → use the `writer` skill's Contributor persona
- UI copy, error messages → use the `writer` skill's UX Writer persona
- Executive strategy documents → use the `strategy-writer` skill
- Quick social posts or comments → use the `writer` skill's Poster/LinkedIn persona
