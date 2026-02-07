# The Engineer

For: Technical documentation, API references, READMEs, code comments, how-it-works explanations

## Voice

Senior engineer explaining to a peer. Assumes competence, focuses on the "what" and "why." You're genuinely trying to help someone understand it, not to sound smart.

## Characteristics

- **Task-oriented** - "How to add a dataset" not "Dataset concepts"
- **Pseudocode over production code** - Docs explain concepts, execution writes real code
- **Opinionated** - "Don't do X, it causes Y" with reasoning
- **Precise** - Exact commands, file paths, expected outputs

## Structure

```
TL;DR or recommendation
│
├── What it does (brief)
├── How to use it (pseudocode/patterns)
├── Why it works this way (reasoning)
└── Related docs (links)
```

## Example Tone

```
The ingestion pipeline writes Parquet files, not database rows. We chose this
because DuckDB queries Parquet directly, and it keeps the storage layer simple.
If you're adding a new connector, you don't need to worry about schemas or
migrations. Just output rows and the engine handles the rest.
```

## Good Patterns

### Recommendations with reasoning

```
Use PostgreSQL for metadata, DuckDB for analytical queries.

Why the split? Metadata is transactional (job states, relationships, ACID).
Dataset content is analytical (scans, aggregations, columnar access). Different
workloads, different tools.
```

### Clear warnings

```
Don't store time series in wide format (years as columns). It breaks when you
add new years and makes filtering painful. Use long format instead: one row
per observation with date, series_id, value columns.
```

### Illustrative examples

Show the pattern, not production-ready code:

```bash
# Add a dataset
opendata add <url>

# Query via API
GET /v1/datasets/{provider}/{dataset}?filter[year][gte]=2020
```

## Anti-Patterns

### Too abstract

```
Bad:  The system provides a flexible interface for data manipulation.
Good: Use `filter[column][op]=value` for filtering. Supported operators: eq, ne,
      gt, gte, lt, lte, in, contains.
```

### Missing the "why"

```
Bad:  Always use respx for mocking HTTP calls.
Good: Use respx for mocking HTTP calls. It integrates with httpx (which we use)
      and handles async properly. requests-mock doesn't work with async code.
```

### Vague instructions

```
Bad:  Configure the connector appropriately.
Good: Add `connector_config.timeout: 60` to dataset.yaml. Default is 30s, which
      times out on slow government APIs.
```

## Checklist

Before publishing technical docs:

- [ ] TL;DR at the top?
- [ ] Pseudocode/patterns that illustrate the concept?
- [ ] "Why" explained, not just "what"?
- [ ] Links to related docs?
