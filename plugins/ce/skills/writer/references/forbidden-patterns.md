# Forbidden Patterns

The thing that gives AI writing away is taste, not vocabulary. Models reach for real rhetorical
devices (antithesis, the triad, parallelism) and deploy them on every paragraph instead of
sparingly and with intent. That's why these patterns survive a find-and-replace: scrubbing
"delve" does nothing to the sentence shape underneath. Weight your self-editing toward the
rhetorical and structural sections first. The word lists at the bottom are the least reliable
signal and the easiest trap, because editing them out feels like progress while the tells remain.

## Rhetorical patterns (fix these first)

These are the highest-frequency tells and the hardest to unsee once you've spotted them.

- **Negative parallelism.** Negate a small thing, then "elevate" it to a grand one. The single
  most recognizable AI tell. It has many surface forms, and deleting the obvious one leaves the
  structure intact, so kill the structure, not the phrasing.
  - Bad: "It's not just a tool, it's a revolution." / "Less about speed, more about trust." /
    "Not a mirror but a portal." / "prioritizing clarity rather than cleverness."
  - Fixed: "The tool formats the report automatically."
- **The triad.** Three parallel items to fake comprehensiveness, often ascending. Two is fine.
  One is fine. Three *every single time* is the tell.
  - Bad: "fast, efficient, and reliable" / "Think bigger. Act bolder. Move faster."
  - Fixed: name the one or two things that actually matter.
- **False range.** "From X to Y" / "everything from A to B" that just lists two examples and
  implies a whole spectrum that isn't there.
  - Bad: "Everything from startups to enterprises benefits."
  - Fixed: "Both small teams and large companies use it."
- **Unearned profundity.** A weighty pivot with nothing behind it. The signpost signals
  significance without delivering any.
  - Bad: "Something shifted." / "Everything changed." / "But here's the thing:"
  - Fixed: state what actually happened.
- **Rhetorical question, answered immediately.** Question then instant answer, especially stacked.
  Pure machine cadence.
  - Bad: "Why does this matter? Because latency compounds." / "The result? A faster pipeline."
  - Fixed: "Latency compounds, so this matters." / "The pipeline gets faster."
- **Inflated significance.** Generic importance bolted onto an ordinary subject.
  - Bad: "marks a pivotal moment," "represents a significant shift," "part of a broader movement."
  - Fixed: say the concrete change, or cut it.

## Structural patterns (paragraph and document level)

- **Participial-phrase tic.** A trailing "-ing" clause that asserts importance without evidence.
  - Bad: "...further enhancing its role as a dynamic hub." / "...cementing its place in the stack."
  - Fixed: delete the clause, or replace it with a fact.
- **Copula avoidance.** Dodging a plain "is/are" for an inflated stand-in.
  - Bad: "The cache serves as / stands as / represents the source of truth."
  - Fixed: "The cache is the source of truth."
- **Uniform weighting.** Every point gets a paragraph of near-identical length regardless of how
  much it matters. Real writing speeds up and slows down; the important thing gets more room and
  the minor thing gets a clause.
- **The recap opener.** A paragraph that restates what you said you'd cover before covering it.
  Cut it and start with the claim.
- **The summary closer.** "In summary..." / "Now that you understand X, you can Y" / "Despite its
  challenges, it continues to thrive." End on the last substantive point. No wrap-up.
- **"There are several reasons for this"** before a list. Just give the list.
- **The hedged recommendation.** "The right approach depends on your use case, but..." before
  finally giving the recommendation. Pick a side first, then note where it breaks down.

## Transition openers

These start sentences in AI output at a rate no human matches. Ban them:

- "Importantly," / "Notably," / "Interestingly,"
- "That said," as a pivot
- "Of course," / "To be fair," as a softener
- "In other words," / "Simply put," / "To put it simply," when restating
- "At the end of the day," / "The reality is," / "The truth is,"
- "When it comes to X," as a paragraph opener
- "It's worth noting that..." / "It bears mentioning that..."
- "Whether you're X or Y..." / "Picture this," / "Imagine you're..." as a fake-personal opener
- "In today's fast-paced world," / "As technology continues to evolve," and other scene-setting

## Tone and stance

- **Hedging seesaw.** Every claim immediately softened or counterbalanced; two qualifiers stacked
  before one observation. Take a position, then name the limit once.
  - Bad: "This could potentially, in some cases, be beneficial."
  - Fixed: "This works well for X. It's weaker for Y."
- **Vague attribution.** Claims pinned to undefined authorities, sometimes inflating quantity.
  - Bad: "Experts say," "Observers note," "Industry reports suggest," "many reviewers."
  - Fixed: name the source or cut the claim.
- **Editorializing meta-commentary.** Telling the reader how to feel about the content instead of
  just stating it. "It's important to note that," "It's worth mentioning," "Notably,".
- **Relentless positivity.** Press-release tone, "commitment to," everything "vibrant" and "rich."
  Describe what's true, including the parts that aren't great.

## Word-level tells (weakest signal; fix structure first)

These shift by model generation and are easy to scrub, so they prove the least. Don't mistake
swapping these for fixing the writing.

- **Inflated verbs:** leverage/utilize -> use; underscore -> show; facilitate -> help (or name the
  mechanism); delve into / dive deep -> just explain it; elucidate -> explain; encompass -> cover;
  unlock, navigate, showcase, foster -> usually a sign you ran out of a specific.
- **Inflated adjectives:** crucial / critical / essential -> say why it matters instead of labeling
  it; robust (unless literally fault tolerance); seamless -> describe what makes it smooth;
  comprehensive -> name what's covered; powerful as a generic modifier.
- **Corporate filler:** best-in-class, cutting-edge, synergy, holistic, scalable (unless literally
  infrastructure), core, modern, ecosystem, framework as filler.
- **Literary-AI set:** tapestry, testament, realm, landscape (abstract), intricate, interplay,
  nuanced, multifaceted, vibrant, meticulous. If you wrote one, you're decorating, not informing.

## Formatting

- **List overuse.** Walls of bullets, each a `**Bold lead-in:** explanation`. Prose that could be
  sentences shouldn't be a list. Use a list when the items are genuinely parallel and scannable.
- **Bold scatter.** Random terms bolded with no emphasis logic. Bold marks the one thing that
  matters in a passage, not every key noun.
- **Title-case headers.** Sentence case, not "Impact Of Technology And Digitalization."
- **Emoji.** None unless requested. The check-in-green-box, the brain, the blue diamond are instant
  giveaways.
- **Unicode decoration.** Arrows, multiplication signs, and smart quotes where plain text belongs.

## A note on em dashes

Older guidance treated the em dash as a hard AI signature. That's now a weak signal: newer models
suppress them and plenty of human writers love them. Don't lean on their presence or absence to
judge whether something reads as AI. Use them if the sentence genuinely needs the break; if you're
reaching for one to dodge a rewrite, that's the actual tell, not the dash itself.
