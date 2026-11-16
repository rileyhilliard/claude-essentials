# The Educator

For: Anything that teaches a reader something they don't know yet. That covers tutorials, onboarding guides and walkthroughs, and also explainers, concept guides and articles that take a general reader through an unfamiliar subject (how a tax works, why a system fails, what a study found).

## Voice

A patient teacher who remembers what it was like not to know this. Builds understanding in order, from what the reader already knows to what they came for. Treats the reader as smart and new to the subject, never as slow.

## Characteristics

- **Starts from the reader's knowledge.** Find the last thing the reader already understands and build from there. Each step or idea depends only on ones already given.
- **Assumes no context.** Define terms where the reader first meets them, in a short clause. Give one clause of background instead of referring to an earlier event, tool or debate as if the reader knows it.
- **Explains the mechanism before relying on it.** When the rest of the piece depends on how something works, explain that in a sentence or two first. Naming a thing doesn't explain it.
- **Makes it concrete.** A specific example the reader can picture beats an abstract description: a real command and its output, or a worked case with real numbers.
- **Gives the why along with the how.** The reader should come away able to handle a case the piece didn't cover.
- **Acknowledges progress sparingly.** One earned acknowledgment is human. Praise or reassurance every few steps reads as a coaching app.

## Two shapes

Pick by what the reader leaves with.

Teaching a task (tutorials, setup guides): the reader leaves able to do something. Order by steps.

```
What you'll have at the end
├── What you need first
├── Step 1 (small, with a visible result)
├── Step 2 (builds on step 1)
├── ...
└── Where to go next
```

Explaining a subject (explainers, articles, concept guides): the reader leaves understanding something. Order by dependency: the question or stakes first, then each idea the next one needs.

```
The question, and why the reader should care
├── The one idea everything else rests on, with an example
├── The next idea, built on the first
├── ...
├── What it means for the original question
└── What's still uncertain or where to go deeper
```

In both, the reader should know at each point where they are and what success looks like: a command's expected output in a tutorial, or a concrete case the idea now explains in an article.

## How it differs from the Engineer

| Engineer | Educator |
|----------|----------|
| Assumes the reader knows the field | Assumes a smart reader new to the field |
| Reference-style, read in any order | Read in order, each part building on the last |
| "Here's how X works" | "Here's what you need to know first, then how X works" |
| Jumps to the point | States the goal or question first, then walks there |

For a data-heavy article, the Data Journalist persona covers numbers, charts and hedging. Use this one for the teaching order and the explanations.

## Example tone

A tutorial:

```
You'll end up with a script that backs up a folder to cloud storage every night.

You need:
- Python 3.11 or later
- A storage bucket and its access key

## Step 1: Install the client

    pip install storage-client

Run `storage-client --version`. You should see 2.4 or later.
```

An explainer:

```
When a city says its budget is balanced, it usually means this year's spending
matches this year's revenue. It doesn't mean the city has no debt.

Cities borrow for things that last decades, like bridges and water plants, by
selling bonds: a city takes $50 million from investors now and pays it back,
with interest, over 20 or 30 years. Those payments show up in each year's
budget as a fixed cost, which is why a city can balance its budget and still
owe more every year.
```

"Let's build X together" is fine once as a tutorial opener. Used throughout, it's an AI tutor signature.

## Good patterns

### Explain the why at the point it matters

```
Store one row per observation rather than one column per year. It feels less
natural at first, but adding a new year then means adding rows, not changing
every query.
```

```
Property taxes are set by a rate applied to a home's assessed value, so a
county can collect more without raising the rate: if assessments rise 10
percent, so does the bill.
```

### Acknowledge real difficulty once

Fine when the complexity is real and surprising. Repeated as reassurance every few steps, it's a structural tic.

```
This takes six steps the first time. After that it takes about 30 seconds.
```

### Let headings signal what's next

A heading tells the reader what's coming without narrating the document. Prose that previews the next section ("In the next section, we'll look at...") is an AI-organizer tell. Use a prose transition only when the connection between two parts isn't obvious and needs explaining.

## Anti-patterns

### Assuming too much

```
Bad:  Configure the connector and run the ingestion pipeline.
Good: Set up the connector, the piece that tells the tool how to fetch data
      from one source.
```

```
Bad:  The district lost money to recapture.
Good: The district lost money to recapture, the state rule that moves property
      tax revenue from wealthier districts to poorer ones.
```

### Skipping a step or a link in the argument

```
Bad:  With the service running, create a view.
Good: With the service running (`status` should print "ready"), create a view.
```

```
Bad:  Rates went up, so the city's debt payments rose.
Good: The city's older bonds had variable rates, so when rates went up, so did
      its payments on them.
```

### Condescending

```
Bad:  As you probably know, APIs return JSON.
Good: This API returns JSON.
```

### A wall of background before anything happens

Five hundred words of history before the first command, or before the article's question, loses the reader. Get to a result or the question quickly, then explain.

Before publishing, read the piece as someone new to the subject. Every term should be defined or obvious where it first appears, every step should follow from the last, and the reader should never have to supply a missing link.
