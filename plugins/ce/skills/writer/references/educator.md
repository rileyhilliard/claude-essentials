# The Educator

For: Tutorials, onboarding guides, learning content, walkthroughs, getting started guides

## Voice

Patient teacher who remembers what it was like to not know this stuff. Builds understanding step by step. Never makes the reader feel dumb for not knowing something.

## Characteristics

- **Builds incrementally** - Each step builds on the last
- **Doesn't assume context** - Explains prerequisites, defines terms
- **Shows the "aha" moment** - Helps reader understand why, not just how
- **Celebrates small wins** - Acknowledges progress, but use this sparingly. Tutorials do it; AI tutors do it every 3 steps as a structural beat. One acknowledgment, earned, is human. One per step is a coaching app.

## How It Differs From The Engineer

| Engineer | Educator |
|----------|----------|
| Assumes competence | Assumes willingness to learn |
| Reference-style | Narrative-style |
| "Here's how X works" | "Let's build X together" |
| Jumps to the point | Builds to the point |

## Structure

```
What we're building / learning
│
├── Prerequisites (what you need first)
├── Step 1 (small, achievable)
├── Step 2 (builds on step 1)
├── ...
├── Step N (the goal)
└── What's next (where to go from here)
```

## Example Tone

Note: "Let's X together" is fine once as an opener. Using it as a recurring phrase throughout a tutorial is an LLM tutor signature. After the opening, drop it.

```
Let's add your first dataset to OpenData.

Before we start, make sure you have:
- OpenData running locally (see Getting Started if not)
- A URL to a CSV or JSON file you want to add

Ready? Let's go.

## Step 1: Find a dataset

Pick any public CSV. For this tutorial, we'll use population data from the
Census Bureau:

    https://api.census.gov/data/2020/dec/pl?get=NAME,P1_001N&for=state:*

Don't worry about what that URL means yet. We'll break it down in a minute.

## Step 2: Add it

Run this command:

    opendata add <that-url>

You should see output like:

    Detected: Census Bureau API
    Format: JSON
    Rows: 52
    Status: ready

That's it. Your first dataset is queryable.
```

## Good Patterns

### Acknowledge the learning curve

Fine to use once when genuinely warranted. AI defaults to this as a reassurance loop -- every few steps, preemptively managing the reader's frustration. Real writers use it when the complexity is real and surprising, not as a structural beat.

```
This might seem like a lot of steps. It is, the first time. Once you've done it
twice, it takes about 30 seconds. We're going slow so you understand what's
happening.
```

### Explain the "why" along the way

```
We use long format (one row per observation) instead of wide format (years as
columns). This feels less intuitive at first, but it makes queries much simpler.
You'll see why in Step 4.
```

### Small wins

```
Run `opendata status census/population` and you should see "ready".

Nice. Your dataset is live. Let's query it.
```

### Signpost what's coming

High-risk pattern. Prose transitions that preview the next section ("In the next section, we'll X. But first, let's Y") are a top-tier LLM-as-organizer tell. Use a section header to signal structure. Only use prose transitions when the connection between steps is genuinely non-obvious and needs explanation.

```
In the next section, we'll add filtering. But first, let's make sure basic
queries work.
```

Better approach: just use a heading. "## Adding Filters" tells the reader what's next without narrating the document aloud.

## Anti-Patterns

### Assuming too much

```
Bad:  Configure your connector and run the ingestion pipeline.
Good: Let's set up the connector. A connector tells OpenData how to fetch data
      from a specific source. Census data needs the Census connector.
```

### Skipping steps

```
Bad:  Now that your dataset is ready, let's create a view.
Good: Now that your dataset is ready (you should see "status: ready" when you
      run `opendata status`), let's create a view.
```

### Being condescending

```
Bad:  As you probably know, APIs return JSON.
Good: This API returns JSON. OpenData handles the parsing automatically.
```

### Wall of text before action

```
Bad:  [500 words of explanation before the first command]
Good: Let's start by running one command, then we'll explain what happened.
```

## Checklist

Before publishing tutorials:

- [ ] Prerequisites clearly stated?
- [ ] Each step small and achievable?
- [ ] Reader knows what success looks like at each step?
- [ ] "Why" explained, not just "how"?
- [ ] No assumed knowledge that wasn't introduced?
- [ ] Clear path to "what's next"?
