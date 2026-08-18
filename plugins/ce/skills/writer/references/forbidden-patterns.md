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
- **Windup paragraphs.** Two or three sentences of setup before the point lands. The reader has
  to reach sentence three to learn what the paragraph is about.
  - Bad: "The tempting conclusion is that COVID caused this. The data says something more
    specific, and getting the distinction right matters. The trend predates the pandemic by a
    decade."
  - Fixed: "COVID accelerated this trend but did not start it. The trend predates the pandemic
    by a decade."
  - The test: find the sentence a reader would start at if they were skimming. That sentence is
    the lead. Everything before it is windup; cut or move it after the lead.
- **Every paragraph opens with its point.** This is the single most effective structural rule
  against longform AI slop. If the point arrives in sentence two or later, move it to sentence
  one. Supporting detail follows; it does not precede.

## Longform tells (articles, reports, analyses)

These show up in sustained writing where the model has room to build habits across sections. They
survive sentence-level editing because each sentence reads fine in isolation; the tell is the
repetition of the shape across the piece.

- **Meta-narration.** The writer commenting on the writing instead of just writing. Naming the
  article's own structure, thesis, or argument as if from outside it.
  - Bad: "Up to here this has been a story about percentages." / "That is the whole thesis in
    one county." / "the thing this whole article has been about" / "That is the mechanism."
  - Fixed: cut. The reader is already inside the article; they don't need you to label what
    section they're in or name what you just argued.
- **Reader-directing imperatives.** Telling the reader what to feel or do with the information
  instead of letting the information do it. Often appears as a short sentence before or after a
  finding.
  - Bad: "Hold that number against the record." / "That last number is the one to sit with." /
    "That is worth sitting with before handing the blame to one tribe."
  - Fixed: cut the directive; state the finding. "Measles killed three Americans in 2025. It
    had killed three in the preceding 22 years." The comparison speaks without being told to.
- **Section-ending kickers.** A dramatic one-liner closing every section, adding drama but no
  information. Budget this device to zero or one per piece. If most of your sections end on a
  punchy fragment, rewrite most of them as ordinary sentences.
  - Bad: "It builds the kindling." / "The average will keep looking fine right up until it
    doesn't." / "Their protection got spent on someone else's exemption form."
  - Fixed: end on the last substantive sentence. If the section needs a closer, make it carry
    a concrete fact or implication, not a restatement in dramatic clothing.
- **Callback flourishes.** A sentence that names what the preceding paragraph just argued, as if
  labeling its own thesis for the reader. Closely related to the summary closer, but appears
  mid-article after individual sections rather than at the end.
  - Bad: "That is the mechanism, and it repeats wherever the tail is thickest." / "This one
    hid a public-health line getting crossed in more and more places at once."
  - Fixed: cut, or replace with a concrete forward-looking sentence. If the argument was clear,
    it does not need a label.
- **The dramatic negation pair.** Two sentences where the first sets up a straw version and the
  second knocks it down. A specific form of negative parallelism that appears in longform when
  the model transitions between sections.
  - Bad: "Those are serious arguments. Here is where they run out." / "That reading is what
    makes the case surge look like it came out of nowhere. It did not come out of nowhere."
  - Fixed: cut the setup sentence. Start with the substantive claim. "The trend predates the
    pandemic by a decade" does not need "It did not come out of nowhere" in front of it.

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
  just stating it. Includes both the obvious adverb form and the subtler imperative form.
  - Obvious: "It's important to note that," "It's worth mentioning," "Notably,"
  - Subtle: "so it is worth being careful about which one the data actually shows" /
    "and getting the distinction right matters, because the overclaim is easy to knock down"
  - Fixed: cut the editorial frame and state the content directly.
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
